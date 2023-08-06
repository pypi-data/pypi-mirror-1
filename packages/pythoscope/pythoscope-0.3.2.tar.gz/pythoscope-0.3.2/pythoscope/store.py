import __builtin__
import os
import cPickle
import re
import time
import types

from pythoscope.astvisitor import EmptyCode, Newline, create_import, find_last_leaf, \
     get_starting_whitespace, is_node_of_type, regenerate, \
     remove_trailing_whitespace
from pythoscope.util import all_of_type, set, all, \
     write_string_to_file, ensure_directory, DirectoryException, \
     get_last_modification_time, read_file_contents, is_generator_code, \
     extract_subpath, directories_under, findfirst, contains_active_generator


# So we can pickle the function and generator types.
__builtin__.function = types.FunctionType
__builtin__.generator = types.GeneratorType

class ModuleNeedsAnalysis(Exception):
    def __init__(self, path, out_of_sync=False):
        Exception.__init__(self, "Destination test module %r needs analysis." % path)
        self.path = path
        self.out_of_sync = out_of_sync

class ModuleNotFound(Exception):
    def __init__(self, module):
        Exception.__init__(self, "Couldn't find module %r." % module)
        self.module = module

class ModuleSaveError(Exception):
    def __init__(self, module, reason):
        Exception.__init__(self, "Couldn't save module %r: %s." % (module, reason))
        self.module = module
        self.reason = reason

def get_pythoscope_path(project_path):
    return os.path.join(project_path, ".pythoscope")

def get_pickle_path(project_path):
    return os.path.join(get_pythoscope_path(project_path), "project.pickle")

def get_points_of_entry_path(project_path):
    return os.path.join(get_pythoscope_path(project_path), "points-of-entry")

def get_test_objects(objects):
    def is_test_object(object):
        return isinstance(object, TestCase)
    return filter(is_test_object, objects)

class Project(object):
    """Object representing the whole project under Pythoscope wings.

    No modifications are final until you call save().
    """
    def from_directory(cls, project_path):
        """Read the project information from the .pythoscope/ directory of
        the given project.

        The pickle file may not exist for project that is analyzed the
        first time and that's OK.
        """
        project_path = os.path.realpath(project_path)
        try:
            fd = open(get_pickle_path(project_path))
            project = cPickle.load(fd)
            fd.close()
            # Update project's path, as the directory could've been moved.
            project.path = project_path
        except IOError:
            project = Project(project_path)
        return project
    from_directory = classmethod(from_directory)

    def __init__(self, path):
        self.path = path
        self.new_tests_directory = "tests"
        self.points_of_entry = {}
        self._modules = {}

        self._find_new_tests_directory()

    def _get_pickle_path(self):
        return get_pickle_path(self.path)

    def _get_points_of_entry_path(self):
        return get_points_of_entry_path(self.path)

    def _find_new_tests_directory(self):
        for path in directories_under(self.path):
            if re.search(r'[_-]?tests?([_-]|$)', path):
                self.new_tests_directory = path

    def save(self):
        # Try pickling the project first, because if this fails, we shouldn't
        # save any changes at all.
        pickled_project = cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)

        # To avoid inconsistencies try to save all project's modules first. If
        # any of those saves fail, the pickle file won't get updated.
        for module in self.get_modules():
            module.save()

        write_string_to_file(pickled_project, self._get_pickle_path())

    def find_module_by_full_path(self, path):
        subpath = self._extract_subpath(path)
        return self[subpath]

    def ensure_point_of_entry(self, path):
        name = self._extract_point_of_entry_subpath(path)
        if name not in self.points_of_entry:
            poe = PointOfEntry(project=self, name=name)
            self.points_of_entry[name] = poe
        return self.points_of_entry[name]

    def remove_point_of_entry(self, name):
        poe = self.points_of_entry.pop(name)
        poe.clear_previous_run()

    def create_module(self, path, **kwds):
        """Create a module for this project located under given path.

        If there already was a module with given subpath, it will get replaced
        with a new instance using the _replace_references_to_module method.

        Returns the new Module object.
        """
        module = Module(subpath=self._extract_subpath(path), project=self, **kwds)

        if module.subpath in self._modules.keys():
            self._replace_references_to_module(module)

        self._modules[module.subpath] = module

        return module

    def create_test_module_from_name(self, test_name):
        """Create a module with given name in project tests directory.

        If the test module already exists, ModuleNeedsAnalysis exception will
        be raised.
        """
        test_path = self._path_for_test(test_name)
        if os.path.exists(test_path):
            raise ModuleNeedsAnalysis(test_path)
        return self.create_module(test_path)

    def remove_module(self, subpath):
        """Remove a module from this Project along with all references to it
        from other modules.
        """
        module = self[subpath]
        for test_case in self.iter_test_cases():
            try:
                test_case.associated_modules.remove(module)
            except ValueError:
                pass
        del self._modules[subpath]

    def _replace_references_to_module(self, module):
        """Remove a module with the same subpath as given module from this
        Project and replace all references to it with the new instance.
        """
        old_module = self[module.subpath]
        for test_case in self.iter_test_cases():
            try:
                test_case.associated_modules.remove(old_module)
                test_case.associated_modules.append(module)
            except ValueError:
                pass

    def _extract_point_of_entry_subpath(self, path):
        """Takes the file path and returns subpath relative to the
        points of entry path.

        Assumes the given path is under points of entry path.
        """
        return extract_subpath(path, self._get_points_of_entry_path())

    def _extract_subpath(self, path):
        """Takes the file path and returns subpath relative to the
        project.

        Assumes the given path is under Project.path.
        """
        return extract_subpath(path, self.path)

    def iter_test_cases(self):
        for module in self.iter_modules():
            for test_case in module.test_cases:
                yield test_case

    def _path_for_test(self, test_module_name):
        """Return a full path to test module with given name.
        """
        return os.path.join(self.path, self.new_tests_directory, test_module_name)

    def __getitem__(self, module):
        for mod in self.iter_modules():
            if module in [mod.subpath, mod.locator]:
                return mod
        raise ModuleNotFound(module)

    def get_modules(self):
        return self._modules.values()

    def iter_modules(self):
        return self._modules.values()

    def iter_classes(self):
        for module in self.iter_modules():
            for klass in module.classes:
                yield klass

    def iter_functions(self):
        for module in self.iter_modules():
            for function in module.functions:
                yield function

    def iter_generator_objects(self):
        for module in self.iter_modules():
            for generator in module.generators:
                for gobject in generator.calls:
                    yield gobject

    def find_object(self, type, name, modulepath):
        modulename = self._extract_subpath(modulepath)
        try:
            for obj in all_of_type(self[modulename].objects, type):
                if obj.name == name:
                    return obj
        except ModuleNotFound:
            pass

# :: ObjectWrapper | [ObjectWrapper] -> bool
def can_be_constructed(object):
    if isinstance(object, list):
        return all(map(can_be_constructed, object))
    return object.can_be_constructed

class ObjectWrapper(object):
    def get_type(self):
        raise NotImplementedError("Can't get the type of %s" % self)

    def get_name(self):
        return self.get_type().__name__

    def get_module_name(self):
        return self.get_type().__module__

class Value(ObjectWrapper):
    """Wrapper of an object, which can be pickled, so we can save its real
    value.
    """
    can_be_constructed = True

    def __init__(self, object):
        self.value = object

    def get_type(self):
        return self.value.__class__

    def __eq__(self, other):
        return isinstance(other, Value) and self.value == other.value

    def __hash__(self):
        # Dictionary itself is not hashable, but set of its keys must be.
        if isinstance(self.value, dict):
            return hash(tuple(self.value.keys()))
        return hash(self.value)

    def __repr__(self):
        return "Value(%r)" % self.value

class Type(ObjectWrapper):
    """Placeholder for an object that cannot be pickled, thus have to be
    remembered as type only.
    """
    can_be_constructed = False

    def __init__(self, object):
        self.type = type(object)

    def get_type(self):
        return self.type

    def __eq__(self, other):
        return isinstance(other, Type) and self.type == other.type

    def __hash__(self):
        return hash(self.type)

    def __repr__(self):
        return "Type(%r)" % self.type

class Repr(ObjectWrapper):
    """Placeholder for an object which cannot be pickled and which type
    cannot be pickled as well, so it is remembered as its string representation
    only.
    """
    can_be_constructed = False

    def __init__(self, object):
        self.repr = repr(object)

    def __eq__(self, other):
        return isinstance(other, Repr) and self.repr == other.repr

    def __hash__(self):
        return hash(self.repr)

    def __repr__(self):
        return "Repr(%s)" % self.repr

def is_pickable(object):
    try:
        cPickle.dumps(object)
        return True
    except (cPickle.PicklingError, TypeError):
        return False

def wrap_object(object):
    if is_pickable(object):
        return Value(object)
    elif is_pickable(type(object)):
        return Type(object)
    else:
        return Repr(object)

def wrap_call_arguments(input):
    new_input = {}
    for key, value in input.iteritems():
        new_input[key] = wrap_object(value)
    return new_input

class Call(object):
    """Stores information about a single function or method call.

    Includes reference to the caller, all call arguments, references to
    other calls made inside this one and finally an output value.

    There's more to function/method call than arguments and outputs.
    They're the only attributes for now, but information on side effects
    will be added later.

    __eq__ and __hash__ definitions provided for Function.get_unique_calls()
    and LiveObject.get_external_calls().
    """
    def __init__(self, definition, input, output=None, exception=None):
        if [value for value in input.values() if not isinstance(value, ObjectWrapper)]:
            raise ValueError("All input values should be instances of ObjectWrapper class.")
        if output and exception:
            raise ValueError("Call should have a single point of return.")
        if not isinstance(definition, Definition):
            raise ValueError("Call definition object should be an instance of Definition.")

        self.definition = definition
        self.input = input
        self.output = output
        self.exception = exception

        self.caller = None
        self.subcalls = []

    def add_subcall(self, call):
        if call.caller is not None:
            raise TypeError("This Call already has a caller.")
        call.caller = self
        self.subcalls.append(call)

    def raised_exception(self):
        return self.exception is not None

    def set_output(self, output):
        self.output = wrap_object(output)

    def set_exception(self, exception):
        self.exception = wrap_object(exception)

    def clear_exception(self):
        self.exception = None

    def is_testable(self):
        return True

    def __eq__(self, other):
        return self.definition == other.definition and \
               self.input == other.input and \
               self.output == other.output and \
               self.exception == other.exception

    def __hash__(self):
        return hash((self.definition.name,
                     tuple(self.input.iteritems()),
                     self.output,
                     self.exception))

    def __repr__(self):
        return "%s(definition=%s, input=%r, output=%r, exception=%r)" % \
               (self.__class__.__name__, self.definition.name, self.input,
                self.output, self.exception)

class FunctionCall(Call):
    def __init__(self, point_of_entry, function, input, output=None, exception=None):
        Call.__init__(self, function, input, output, exception)
        self.point_of_entry = point_of_entry

class MethodCall(Call):
    pass

class Definition(object):
    def __init__(self, name, code=None, is_generator=False):
        if code is None:
            code = EmptyCode()
        self.name = name
        self.code = code
        self.is_generator = is_generator

class Callable(object):
    def __init__(self, calls=None):
        if calls is None:
            calls = []
        self.calls = calls

    def add_call(self, call):
        self.calls.append(call)

    def get_generator_object(self, unique_id):
        def is_matching_gobject(call):
            return isinstance(call, GeneratorObject) and call.unique_id == unique_id
        return findfirst(is_matching_gobject, self.calls)

    def remove_calls_from(self, point_of_entry):
        self.calls = [call for call in self.calls if call.point_of_entry is not point_of_entry]

class Function(Definition, Callable):
    def __init__(self, name, code=None, calls=None, is_generator=False):
        Definition.__init__(self, name, code, is_generator)
        Callable.__init__(self, calls)

    def is_testable(self):
        return not self.name.startswith('_')

    def get_unique_calls(self):
        return set(self.calls)

    def __repr__(self):
        return "Function(name=%r, calls=%r)" % (self.name, self.calls)

# Methods are not Callable, because they cannot be called by itself - they
# need a bound object. We represent this object by LiveObject class, which
# gathers all MethodCalls for given instance.
class Method(Definition):
    pass

class GeneratorObject(Call):
    """Representation of a generator object - a callable with on input and many
    outputs (here called "yields").

    Although a generator object execution is not a single call, but consists of
    a series of suspensions and resumes, we make it conform to the Call interface
    for simplicity.
    """
    def __init__(self, id, generator, point_of_entry, input, yields=None, exception=None):
        if yields is None:
            yields = []
        Call.__init__(self, generator, input, yields, exception)

        self.id = id
        self.point_of_entry = point_of_entry
        self.unique_id = (point_of_entry.name, id)

    def set_output(self, output):
        self.output.append(wrap_object(output))

    def is_testable(self):
        return self.raised_exception() or self.output

    def __hash__(self):
        return hash((self.definition.name,
                     tuple(self.input.iteritems()),
                     tuple(self.output),
                     self.exception))

    def __repr__(self):
        return "GeneratorObject(id=%d, generator=%r, yields=%r)" % \
               (self.id, self.definition.name, self.output)

class LiveObject(Callable):
    """Representation of an object which creation and usage was traced
    during dynamic inspection.

    Note that the LiveObject.id is only unique to a given point of entry.
    In other words, it is possible to have two points of entry holding
    separate live objects with the same id. Use LiveObject.unique_id for
    identification purposes.
    """
    def __init__(self, id, klass, point_of_entry):
        Callable.__init__(self)

        self.id = id
        self.klass = klass
        self.point_of_entry = point_of_entry

        self.unique_id = (point_of_entry.name, id)

    def add_call(self, call):
        # Don't add the same GeneratorObject more than once.
        if isinstance(call, GeneratorObject) and call in self.calls:
            return
        Callable.add_call(self, call)

    def get_init_call(self):
        """Return a call to __init__ or None if it wasn't called.
        """
        return findfirst(lambda call: call.definition.name == '__init__', self.calls)

    def get_external_calls(self):
        """Return all calls to this object made from the outside.

        Note: __init__ is considered an internal call.
        """
        def is_not_init_call(call):
            return call.definition.name != '__init__'
        def is_external_call(call):
            return (not call.caller) or (call.caller not in self.calls)
        return filter(is_not_init_call, filter(is_external_call, self.calls))

    def __repr__(self):
        return "LiveObject(id=%d, klass=%r, calls=%r)" % (self.id, self.klass.name, self.calls)

class Class(object):
    def __init__(self, name, methods=[], bases=[]):
        self.name = name
        self.methods = methods
        self.bases = bases
        self.live_objects = {}

    def is_testable(self):
        ignored_superclasses = ['Exception', 'unittest.TestCase']
        for klass in ignored_superclasses:
            if klass in self.bases:
                return False
        return True

    def add_live_object(self, live_object):
        self.live_objects[live_object.unique_id] = live_object

    def remove_live_objects_from(self, point_of_entry):
        # We're removing elements, so iterate over a shallow copy.
        for id, live_object in self.live_objects.copy().iteritems():
            if live_object.point_of_entry is point_of_entry:
                del self.live_objects[id]

    def get_traced_method_names(self):
        traced_method_names = set()
        for live_object in self.live_objects.values():
            for call in live_object.calls:
                traced_method_names.add(call.definition.name)
        return traced_method_names

    def get_untraced_methods(self):
        traced_method_names = self.get_traced_method_names()
        def is_untraced(method):
            return method.name not in traced_method_names
        return filter(is_untraced, self.methods)

    def find_method_by_name(self, name):
        for method in self.methods:
            if method.name == name:
                return method

class TestCase(object):
    """A single test object, possibly contained within a test suite (denoted
    as parent attribute).
    """
    def __init__(self, name, code=None, parent=None):
        if code is None:
            code = EmptyCode()
        self.name = name
        self.code = code
        self.parent = parent

    def replace_itself_with(self, new_test_case):
        self.parent.replace_test_case(self, new_test_case)

class TestSuite(TestCase):
    """A test objects container.

    Keeps both test cases and other test suites in test_cases attribute.
    """
    allowed_test_case_classes = []

    def __init__(self, name, code=None, parent=None, test_cases=[], imports=None):
        TestCase.__init__(self, name, code, parent)

        if imports is None:
            imports = []

        self.changed = False
        self.test_cases = []
        self.imports = imports

    def add_test_cases(self, test_cases, append_code=True):
        for test_case in test_cases:
            self.add_test_case(test_case, append_code)

    def add_test_case(self, test_case, append_code=True):
        self._check_test_case_type(test_case)

        test_case.parent = self
        self.test_cases.append(test_case)

        if append_code:
            self._append_test_case_code(test_case.code)
            self.mark_as_changed()

    def replace_test_case(self, old_test_case, new_test_case):
        self._check_test_case_type(new_test_case)
        if old_test_case not in self.test_cases:
            raise ValueError("Given test case is not part of this test suite.")

        self.test_cases.remove(old_test_case)

        # The easiest way to get the new code inside the AST is to call
        # replace() on the old test case code.
        # It is destructive, but since we're discarding the old test case
        # anyway, it doesn't matter.
        old_test_case.code.replace(new_test_case.code)

        self.add_test_case(new_test_case, False)
        self.mark_as_changed()

    def mark_as_changed(self):
        self.changed = True
        if self.parent:
            self.parent.mark_as_changed()

    def ensure_imports(self, imports):
        "Make sure that all required imports are present."
        for imp in imports:
            self._ensure_import(imp)
        if self.parent:
            self.parent.ensure_imports(imports)

    def _ensure_import(self, import_desc):
        if not self._contains_import(import_desc):
            self.imports.append(import_desc)

    def _contains_import(self, import_desc):
        return import_desc in self.imports

    def _check_test_case_type(self, test_case):
        if not isinstance(test_case, tuple(self.allowed_test_case_classes)):
            raise TypeError("Given test case isn't allowed to be added to this test suite.")

class TestMethod(TestCase):
    pass

class TestClass(TestSuite):
    """Testing class, either generated by Pythoscope or hand-writen by the user.

    Each test class contains a set of requirements its surrounding must meet,
    like the list of imports it needs, contents of the "if __name__ == '__main__'"
    snippet or specific setup and teardown instructions.

    associated_modules is a list of Modules which this test class exercises.
    """
    allowed_test_case_classes = [TestMethod]

    def __init__(self, name, code=None, parent=None, test_cases=[],
                 imports=None, main_snippet=None, associated_modules=None):
        TestSuite.__init__(self, name, code, parent, test_cases, imports)

        if associated_modules is None:
            associated_modules = []

        self.main_snippet = main_snippet
        self.associated_modules = associated_modules

        # Code of test cases passed to the constructor is already contained
        # within the class code.
        self.add_test_cases(test_cases, False)

    def _append_test_case_code(self, code):
        """Append to the right node, so that indentation level of the
        new method is good.
        """
        if self.code.children and is_node_of_type(self.code.children[-1], 'suite'):
            remove_trailing_whitespace(code)
            suite = self.code.children[-1]
            # Prefix the definition with the right amount of whitespace.
            node = find_last_leaf(suite.children[-2])
            ident = get_starting_whitespace(suite)
            # There's no need to have extra newlines.
            if node.prefix.endswith("\n"):
                node.prefix += ident.lstrip("\n")
            else:
                node.prefix += ident
            # Insert before the class contents dedent.
            suite.insert_child(-1, code)
        else:
            self.code.append_child(code)
        self.mark_as_changed()

    def find_method_by_name(self, name):
        for method in self.test_cases:
            if method.name == name:
                return method

    def is_testable(self):
        return False

class Localizable(object):
    """An object which has a corresponding file belonging to some Project.

    Each Localizable has a 'path' attribute and an information when it was
    created, to be in sync with its file system counterpart. Path is always
    relative to the project this localizable belongs to.
    """
    def __init__(self, project, subpath, created=None):
        self.project = project
        self.subpath = subpath
        if created is None:
            created = time.time()
        self.created = created

    def _get_locator(self):
        return re.sub(r'(%s__init__)?\.py$' % re.escape(os.path.sep), '', self.subpath).\
            replace(os.path.sep, ".")
    locator = property(_get_locator)

    def is_out_of_sync(self):
        """Is the object out of sync with its file.
        """
        return get_last_modification_time(self.get_path()) > self.created

    def is_up_to_date(self):
        return not self.is_out_of_sync()

    def get_path(self):
        """Return the full path to the file.
        """
        return os.path.join(self.project.path, self.subpath)

    def write(self, new_content):
        """Overwrite the file with new contents and update its created time.

        Creates the containing directories if needed.
        """
        ensure_directory(os.path.dirname(self.get_path()))
        write_string_to_file(new_content, self.get_path())
        self.created = time.time()

    def exists(self):
        return os.path.isfile(self.get_path())

class Module(Localizable, TestSuite):
    allowed_test_case_classes = [TestClass]

    def __init__(self, project, subpath, code=None, objects=None, imports=None,
                 main_snippet=None, errors=[]):
        if objects is None:
            objects = []
        test_cases = get_test_objects(objects)

        Localizable.__init__(self, project, subpath)
        TestSuite.__init__(self, self.locator, code, None, test_cases, imports)

        self.objects = objects
        self.main_snippet = main_snippet
        self.errors = errors

        # Code of test cases passed to the constructor is already contained
        # within the module code.
        self.add_test_cases(test_cases, False)

    def _get_testable_objects(self):
        return [o for o in self.objects if o.is_testable()]
    testable_objects = property(_get_testable_objects)

    def _get_classes(self):
        return all_of_type(self.objects, Class)
    classes = property(_get_classes)

    def _get_functions(self):
        return all_of_type(self.objects, Function)
    functions = property(_get_functions)

    def _get_test_classes(self):
        return all_of_type(self.objects, TestClass)
    test_classes = property(_get_test_classes)

    def add_test_case(self, test_case, append_code=True):
        TestSuite.add_test_case(self, test_case, append_code)

        self.ensure_imports(test_case.imports)
        self._ensure_main_snippet(test_case.main_snippet)

    # def replace_test_case:
    #   Using the default definition. We don't remove imports or main_snippet,
    #   because we may unintentionally break something.

    def get_content(self):
        return regenerate(self.code)

    def get_test_cases_for_module(self, module):
        """Return all test cases that are associated with given module.
        """
        return [tc for tc in self.test_cases if module in tc.associated_modules]

    def _ensure_main_snippet(self, main_snippet, force=False):
        """Make sure the main_snippet is present. Won't overwrite the snippet
        unless force flag is set.
        """
        if not main_snippet:
            return

        if not self.main_snippet:
            self.main_snippet = main_snippet
            self.code.append_child(main_snippet)
            self.mark_as_changed()
        elif force:
            self.main_snippet.replace(main_snippet)
            self.main_snippet = main_snippet
            self.mark_as_changed()

    def _ensure_import(self, import_desc):
        # Add an extra newline separating imports from the code.
        if not self.imports:
            self.code.insert_child(0, Newline())
            self.mark_as_changed()
        if not self._contains_import(import_desc):
            self._add_import(import_desc)

    def _add_import(self, import_desc):
        self.imports.append(import_desc)
        self.code.insert_child(0, create_import(import_desc))
        self.mark_as_changed()

    def _append_test_case_code(self, code):
        # If the main_snippet exists we have to put the new test case
        # before it. If it doesn't we put the test case at the end.
        if self.main_snippet:
            self._insert_before_main_snippet(code)
        else:
            self.code.append_child(code)
        self.mark_as_changed()

    def _insert_before_main_snippet(self, code):
        for i, child in enumerate(self.code.children):
            if child == self.main_snippet:
                self.code.insert_child(i, code)
                break

    def save(self):
        # Don't save the test file unless it has been changed.
        if self.changed:
            if self.is_out_of_sync():
                raise ModuleNeedsAnalysis(self.subpath, out_of_sync=True)
            try:
                self.write(self.get_content())
            except DirectoryException, err:
                raise ModuleSaveError(self.subpath, err.message)
            self.changed = False

class PointOfEntry(Localizable):
    """Piece of code provided by the user that allows dynamic analysis.

    In add_method_call/add_function_call if we can't find a class or function
    in Project, we don't care about it. This way we don't record any information
    about thid-party and dynamically created code.
    """
    def __init__(self, project, name):
        poes_subpath = project._extract_subpath(project._get_points_of_entry_path())
        # Points of entry start with created attribute equal to 0, as they are
        # not up-to-date until they're run. See finalize_inspection().
        Localizable.__init__(self, project, os.path.join(poes_subpath, name), created=0)

        self.name = name
        # After an inspection run, this will be a reference to the top level call.
        self.call_graph = None

        self._preserved_objects = []
        self._gobjects = []

    def get_path(self):
        return os.path.join(self.project._get_points_of_entry_path(), self.name)

    def get_content(self):
        return read_file_contents(self.get_path())

    def clear_previous_run(self):
        for klass in self.project.iter_classes():
            klass.remove_live_objects_from(self)
        for function in self.project.iter_functions():
            function.remove_calls_from(self)
        self.call_graph = None

    def create_method_call(self, name, classname, modulepath, object, input, code, frame):
        try:
            live_object, method = self._retrieve_live_object_for_method(object, name, classname, modulepath)
            if is_generator_code(code):
                call = self._retrieve_generator_object(live_object, method, input, code, frame)
            else:
                call = MethodCall(method, wrap_call_arguments(input))
            live_object.add_call(call)
            return call
        except LookupError:
            pass

    def create_function_call(self, name, modulepath, input, code, frame):
        function = self.project.find_object(Function, name, modulepath)
        if function:
            if is_generator_code(code):
                return self._retrieve_generator_object(function, function, input, code, frame)
            else:
                call = FunctionCall(self, function, wrap_call_arguments(input))
                function.add_call(call)
                return call

    def finalize_inspection(self):
        # We can release preserved objects now.
        self._preserved_objects = []
        # Mark the point of entry as up-to-date.
        self.created = time.time()
        # Fix output of generator objects.
        self._fix_generator_objects()

    def _retrieve_live_object_for_method(self, object, name, classname, modulepath):
        klass = self.project.find_object(Class, classname, modulepath)
        if not klass:
            raise LookupError("Couldn't find class %s in %s." %\
                                  (classname, modulepath))

        method = klass.find_method_by_name(name)
        if not method:
            raise LookupError("Couldn't find method %s in %s:%s." %\
                                  (name, modulepath, classname))

        live_object = self._retrieve_live_object(object, klass)

        return live_object, method

    def _retrieve_generator_object(self, callable, generator, input, code, frame):
        gobject = callable.get_generator_object((self.name, id(code)))

        if not gobject:
            gobject = GeneratorObject(id(code), generator, self, wrap_call_arguments(input))
            callable.add_call(gobject)
            self._gobjects.append(gobject)
            self._preserve(code)

            # Generator objects return None to the tracer when stopped. That
            # extra None we have to filter out manually (see
            # _fix_generator_objects method). The only way to distinguish
            # between active and stopped generators is to ask garbage collector
            # about them. So we temporarily save the generator frame inside the
            # GeneratorObject, so it can be inspected later.
            gobject._frame = frame

        return gobject

    def _retrieve_live_object(self, object, klass):
        try:
            live_object = klass.live_objects[(self.name, id(object))]
        except KeyError:
            live_object = LiveObject(id(object), klass, self)
            klass.add_live_object(live_object)
            self._preserve(object)
        return live_object

    def _preserve(self, object):
        """Preserve an object from garbage collection, so its id won't get
        occupied by any other object.
        """
        self._preserved_objects.append(object)

    def _fix_generator_objects(self):
        """Remove last yielded values of generator objects, as those are
        just bogus Nones placed on generator stop.
        """
        for gobject in self._gobjects:
            if not contains_active_generator(gobject._frame) \
                   and gobject.output \
                   and gobject.output[-1] == Value(None):
                gobject.output.pop()
            # Once we know if the generator is active or not, we can discard
            # the frame.
            del gobject._frame

        self._gobjects = []
