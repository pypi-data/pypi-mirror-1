import sys

from nose import SkipTest

from pythoscope.inspector.dynamic import inspect_code_in_context, \
    inspect_point_of_entry
from pythoscope.serializer import ImmutableObject, MapObject, UnknownObject, \
    SequenceObject, BuiltinException
from pythoscope.store import Class, Execution, Function, \
    GeneratorObject, Method, UserObject, Project
from pythoscope.compat import all
from pythoscope.util import findfirst, generator_has_ended

from assertions import *
from helper import TestableProject, PointOfEntryMock, EmptyProjectExecution, \
    last_exception_as_string, IgnoredWarnings, putfile, TempDirectory


########################################################################
## Dynamic inspection test helpers.
##
class ClassMock(Class):
    """Class that has all the methods you try to find inside it via
    find_method_by_name().
    """
    def __init__(self, name):
        Class.__init__(self, name)
        self._methods = {}

    def find_method_by_name(self, name):
        if not self._methods.has_key(name):
            self._methods[name] = Method(name)
        return self._methods[name]

class ProjectMock(Project):
    """Project that has all the classes, functions and generators you try to
    find inside it via find_object().
    """
    ignored_modules = ["__builtin__", "exceptions"]

    def __init__(self, ignored_functions=[]):
        self.ignored_functions = ignored_functions
        self.path = "."
        self._classes = {}
        self._functions = {}

    def find_object(self, type, name, modulepath):
        if modulepath in self.ignored_modules:
            return None
        if type is Function and name in self.ignored_functions:
            return None

        object_id = (name, modulepath)
        container = self._get_container_for(type)

        if not container.has_key(object_id):
            container[object_id] = self._create_object(type, name)
        return container[object_id]

    def iter_callables(self):
        for klass in self._classes.values():
            for user_object in klass.user_objects:
                yield user_object
        for function in self._functions.values():
            yield function

    def get_callables(self):
        return list(self.iter_callables())

    def _get_container_for(self, type):
        if type is Class:
            return self._classes
        elif type is Function:
            return self._functions
        else:
            raise TypeError("Cannot store %r inside a module." % type)

    def _create_object(self, type, name):
        if type is Class:
            return ClassMock(name)
        else:
            return type(name)

def assert_equal_serialized(obj1, obj2):
    """Equal assertion that ignores UnknownObjects, SequenceObjects and
    MapObjects identity. For testing purposes only.
    """
    def unknown_object_eq(o1, o2):
        if not isinstance(o2, UnknownObject):
            return False
        return o1.partial_reconstructor == o2.partial_reconstructor
    def sequence_object_eq(o1, o2):
        if not isinstance(o2, SequenceObject):
            return False
        return o1.constructor_format == o2.constructor_format \
            and o1.contained_objects == o2.contained_objects
    def map_object_eq(o1, o2):
        if not isinstance(o2, MapObject):
            return False
        return o1.mapping == o2.mapping
    def builtin_exception_eq(o1, o2):
        if not isinstance(o2, BuiltinException):
            return False
        return o1.args == o2.args
    try:
        UnknownObject.__eq__ = unknown_object_eq
        SequenceObject.__eq__ = sequence_object_eq
        MapObject.__eq__ = map_object_eq
        BuiltinException.__eq__ = builtin_exception_eq
        assert_equal(obj1, obj2)
    finally:
        del UnknownObject.__eq__
        del SequenceObject.__eq__
        del MapObject.__eq__
        del BuiltinException.__eq__

def serialize_value(value):
    return EmptyProjectExecution().serialize(value)
def serialize_collection(collection):
    return map(serialize_value, collection)
def serialize_arguments(args):
    return EmptyProjectExecution().serialize_call_arguments(args)

def assert_serialized(expected_unserialized, actual_serialized):
    assert_equal_serialized(serialize_value(expected_unserialized), actual_serialized)
def assert_collection_of_serialized(expected_collection, actual_collection):
    assert_equal_serialized(serialize_collection(expected_collection), actual_collection)
def assert_call_arguments(expected_args, actual_args):
    assert_equal_serialized(serialize_arguments(expected_args), actual_args)

def assert_call(expected_input, expected_output, call):
    assert_call_arguments(expected_input, call.input)
    assert not call.raised_exception()
    assert_serialized(expected_output, call.output)

def assert_call_with_exception(expected_input, expected_exception_name, call):
    assert_call_arguments(expected_input, call.input)
    assert call.raised_exception()
    assert_equal(expected_exception_name, call.exception.type_name)

def assert_call_with_string_exception(expected_input, expected_string, call):
    assert_call_with_exception(expected_input, 'str', call)
    assert_serialized(expected_string, call.exception)

def assert_generator_object(expected_input, expected_yields, obj):
    assert_instance(obj, GeneratorObject)
    assert_call_arguments(expected_input, obj.input)
    assert_collection_of_serialized(expected_yields, obj.output)

def assert_one_element_and_return(collection):
    """Assert that the collection has exactly one element and return this
    element.
    """
    assert_length(collection, 1)
    return collection[0]

def call_graph_as_string(call_or_calls, indentation=0):
    def lines(call):
        yield "%s%s()\n" % (" "*indentation, call.definition.name)
        for subcall in call.subcalls:
            yield call_graph_as_string(subcall, indentation+4)

    if isinstance(call_or_calls, list):
        return "".join([call_graph_as_string(call) for call in call_or_calls])
    else:
        return "".join(lines(call_or_calls))

def inspect_returning_callables_and_execution(fun, ignored_functions):
    project = ProjectMock(ignored_functions or [])
    execution = Execution(project=project)

    try:
        inspect_code_in_context(fun, execution)
    # Don't allow any POEs exceptions to propagate to the testing code.
    # Catch both string and normal exceptions.
    except:
        print "Caught exception inside point of entry:", last_exception_as_string()

    return project.get_callables(), execution

def inspect_returning_callables(fun, ignored_functions=None):
    return inspect_returning_callables_and_execution(fun, ignored_functions)[0]

def inspect_returning_execution(fun):
    return inspect_returning_callables_and_execution(fun, None)[1]

def inspect_returning_single_callable(fun):
    callables = inspect_returning_callables(fun)
    return assert_one_element_and_return(callables)

def inspect_returning_single_call(fun):
    callables = inspect_returning_callables(fun)
    callable = assert_one_element_and_return(callables)
    return assert_one_element_and_return(callable.calls)

def is_function(obj):
    return isinstance(obj, Function)
def is_user_object(obj):
    return isinstance(obj, UserObject)

def find_first_with_name(name, collection):
    return findfirst(lambda f: f.name == name, collection)

########################################################################
## Functions for inspection.
##
was_run = False
def function_setting_was_run():
    global was_run
    was_run = True

def function_doing_nothing():
    pass

def function_calling_other_function():
    def other_function():
        pass
    other_function()
    other_function()

def function_calling_two_different_functions():
    def first_function():
        pass
    def second_function():
        pass
    first_function()
    second_function()

def function_calling_another_with_two_required_arguments():
    def function(x, y):
        return x + y
    function(7, 13)
    function(1, 2)
    function(42, 43)

def function_calling_another_with_optional_arguments():
    def function(x, y, w=4, z="!"):
        return x + " " + y + w * z
    function("Hello", "world")
    function("Bye", "world", 2)
    function("Humble", "hello", 1, ".")

def function_calling_another_with_keyword_arguments():
    def function(x, y=1):
        return x - y
    function(1)
    function(x=2)
    function(3, y=4)
    function(x=5, y=6)

def function_calling_another_with_varargs():
    def function(x, *rest):
        return list(rest) + [x]
    function(1)
    function(2, 3)
    function(4, 5, 6)

def function_calling_another_with_varargs_only():
    def function(*args):
        return len(args)
    function()

def function_calling_another_with_nested_arguments():
    def function((a, b), c):
        return [c, b, a]
    function((1, 2), 3)

def function_calling_another_with_varkw():
    def function(x, **kwds):
        return kwds.get(x, 42)
    function('a')
    function('b', a=1, b=2)
    function('c', y=3, w=4, z=5)

def function_calling_recursive_function():
    def fac(x):
        if x == 0:
            return 1
        return x * fac(x-1)
    fac(4)

def function_creating_new_style_class():
    class New(object):
        pass

def function_creating_old_style_class():
    class New:
        pass

def function_creating_class_with_function_calls():
    def function(x):
        return x + 1
    class New(object):
        function(42)

def function_calling_a_method():
    class Class(object):
        def method(self):
            pass
    Class().method()

def function_calling_methods_with_strangely_named_self():
    class Class(object):
        def strange_method(s):
            pass
        def another_strange_method(*args):
            pass
    Class().strange_method()
    Class().another_strange_method()

def function_calling_two_methods_with_the_same_name_from_different_classes():
    class FirstClass(object):
        def method(self):
            pass
    class SecondClass(object):
        def method(self):
            pass
    FirstClass().method()
    SecondClass().method()

def function_calling_other_which_uses_name_and_module_variables():
    def function():
        try:
            __name__
            __module__
        except:
            pass
    function()

def function_calling_method_which_calls_other_method():
    class Class(object):
        def method(self):
            self.other_method()
        def other_method(self):
            pass
    Class().method()

def function_changing_its_argument_binding():
    def function((a, b), c):
        a = 7
        return (c, b, a)
    function((1, 2), 3)

def function_with_nested_calls():
    def top():
        obj = Class()
        first(2)
        obj.do_something()
    class Class(object):
        def __init__(self):
            self._setup()
        def _setup(self):
            pass
        def do_something(self):
            self.do_this()
            self.do_that()
        def do_this(self):
            pass
        def do_that(self):
            pass
    def first(x):
        if x > 0:
            second(x)
    def second(x):
        first(x-1)
    top()

expected_call_graph_for_function_with_nested_calls = """top()
    __init__()
        _setup()
    first()
        second()
            first()
                second()
                    first()
    do_something()
        do_this()
        do_that()
"""

def function_returning_function():
    def function(x):
        return lambda y: x + y
    function(13)

def function_with_ignored_function():
    def not_ignored_inner(x):
        return x + 1
    def ignored(y):
        return not_ignored_inner(y*2)
    def not_ignored_outer(z):
        return ignored(z-1) * 3
    not_ignored_outer(13)

def function_calling_generator():
    def generator(x):
        yield x
        yield x + 1
        yield x * 2
        yield x ** 3
    [x for x in generator(2)]

def function_calling_generator_that_yields_one():
    def generator():
        yield 1
    g = generator()
    g.next()

def function_calling_generator_that_yields_none():
    def generator():
        yield None
    g = generator()
    g.next()

def function_calling_empty_generator():
    def generator(x):
        if False:
            yield 'something'
    [x for x in generator(123)]

def function_calling_generator_that_doesnt_get_destroyed():
    def generator():
        yield 1
    g = generator()
    g.next()
    globals()['__generator_yielding_one'] = g

def function_calling_generator_that_yields_none_and_doesnt_get_destroyed():
    def generator():
        yield None
    g = generator()
    g.next()
    globals()['__generator_yielding_none'] = g

def function_calling_generator_method():
    class Class(object):
        def genmeth(self):
            yield 0
            yield 1
            yield 0
    [x for x in Class().genmeth()]

def function_calling_function_that_uses_generator():
    def generator(x):
        yield x
        yield x + 1
        yield x * 2
        yield x ** 3
    def function(y):
        return [x for x in generator(y)]
    function(2)

def function_calling_functions_that_use_the_same_sequence_object():
    def producer():
        return []
    def consumer(lst):
        lst.append(1)
    consumer(producer())

def function_calling_function_that_uses_the_same_user_object():
    class Something(object):
        pass
    def compare(x, y):
        return x is y
    obj = Something()
    compare(obj, obj)

########################################################################
## Actual tests.
##
class TestTraceFunction:
    "trace_function"

    def test_runs_given_function(self):
        inspect_returning_callables(function_setting_was_run)

        assert was_run, "Function wasn't executed."

    def test_returns_empty_list_when_no_calls_to_other_functions_were_made(self):
        callables = inspect_returning_callables(function_doing_nothing)

        assert_equal([], callables)

    def test_returns_a_list_with_a_single_element_when_calls_to_a_single_functions_were_made(self):
        callables = inspect_returning_callables(function_calling_other_function)

        assert_length(callables, 1)

    def test_returns_a_list_with_function_objects(self):
        callables = inspect_returning_callables(function_calling_two_different_functions)

        assert all(map(is_function, callables))

    def test_returns_function_objects_corresponding_to_functions_that_were_called(self):
        callables = inspect_returning_callables(function_calling_two_different_functions)

        assert_equal_sets(['first_function', 'second_function'],
                          [f.name for f in callables])

    def test_returns_function_objects_with_all_calls_recorded(self):
        function = inspect_returning_single_callable(function_calling_other_function)

        assert_length(function.calls, 2)

    def test_returns_function_objects_with_calls_that_use_required_arguments(self):
        function = inspect_returning_single_callable(function_calling_another_with_two_required_arguments)

        assert_call({'x':7,  'y':13},  20, function.calls[0])
        assert_call({'x':1,  'y':2},    3, function.calls[1])
        assert_call({'x':42, 'y':43},  85, function.calls[2])

    def test_returns_function_objects_with_calls_that_use_optional_arguments(self):
        function = inspect_returning_single_callable(function_calling_another_with_optional_arguments)

        assert_call({'x': "Hello",  'y': "world", 'w': 4, 'z': "!"}, "Hello world!!!!", function.calls[0])
        assert_call({'x': "Bye",    'y': "world", 'w': 2, 'z': "!"}, "Bye world!!",     function.calls[1])
        assert_call({'x': "Humble", 'y': "hello", 'w': 1, 'z': "."}, "Humble hello.",   function.calls[2])

    def test_returns_function_objects_with_calls_that_use_keyword_arguments(self):
        function = inspect_returning_single_callable(function_calling_another_with_keyword_arguments)

        assert_call({'x': 1, 'y': 1},  0, function.calls[0])
        assert_call({'x': 2, 'y': 1},  1, function.calls[1])
        assert_call({'x': 3, 'y': 4}, -1, function.calls[2])
        assert_call({'x': 5, 'y': 6}, -1, function.calls[3])

    def test_returns_function_objects_with_calls_that_use_varargs(self):
        function = inspect_returning_single_callable(function_calling_another_with_varargs)

        assert_call({'x': 1, 'rest': ()},     [1],     function.calls[0])
        assert_call({'x': 2, 'rest': (3,)},   [3,2],   function.calls[1])
        assert_call({'x': 4, 'rest': (5, 6)}, [5,6,4], function.calls[2])

    def test_returns_function_objects_with_calls_that_use_varargs_only(self):
        call = inspect_returning_single_call(function_calling_another_with_varargs_only)

        assert_call({'args': ()}, 0, call)

    def test_returns_function_objects_with_calls_that_use_nested_arguments(self):
        call = inspect_returning_single_call(function_calling_another_with_nested_arguments)

        assert_call({'a': 1, 'b': 2, 'c': 3}, [3, 2, 1], call)

    def test_returns_function_objects_with_calls_that_use_varkw(self):
        function = inspect_returning_single_callable(function_calling_another_with_varkw)

        assert_call({'x': 'a', 'kwds': {}},                       42, function.calls[0])
        assert_call({'x': 'b', 'kwds': {'a': 1, 'b': 2}},          2, function.calls[1])
        assert_call({'x': 'c', 'kwds': {'y': 3, 'w': 4, 'z': 5}}, 42, function.calls[2])

    def test_interprets_recursive_calls_properly(self):
        function = inspect_returning_single_callable(function_calling_recursive_function)

        assert_call({'x': 4}, 24, function.calls[0])
        assert_call({'x': 3}, 6, function.calls[1])
        assert_call({'x': 2}, 2, function.calls[2])
        assert_call({'x': 1}, 1, function.calls[3])
        assert_call({'x': 0}, 1, function.calls[4])

    def test_ignores_new_style_class_creation(self):
        callables = inspect_returning_callables(function_creating_new_style_class)

        assert_equal([], callables)

    def test_ignores_old_style_class_creation(self):
        callables = inspect_returning_callables(function_creating_old_style_class)

        assert_equal([], callables)

    def test_traces_function_calls_inside_class_definitions(self):
        call = inspect_returning_single_call(function_creating_class_with_function_calls)

        assert_call({'x': 42}, 43, call)

    def test_returns_a_list_with_user_objects(self):
        callables = inspect_returning_callables(function_calling_a_method)

        assert all(map(is_user_object, callables))

    def test_handles_methods_with_strangely_named_self(self):
        callables = inspect_returning_callables(function_calling_methods_with_strangely_named_self)

        assert_length(callables, 2)
        assert all(map(is_user_object, callables))
        assert_equal_sets(['strange_method', 'another_strange_method'],
                          [obj.calls[0].definition.name for obj in callables])

    def test_distinguishes_between_methods_with_the_same_name_from_different_classes(self):
        callables = inspect_returning_callables(function_calling_two_methods_with_the_same_name_from_different_classes)

        assert_equal_sets([('FirstClass', 1, 'method'), ('SecondClass', 1, 'method')],
                          [(obj.klass.name, len(obj.calls), obj.calls[0].definition.name) for obj in callables])

    def test_distinguishes_between_classes_and_functions(self):
        function = inspect_returning_single_callable(function_calling_other_which_uses_name_and_module_variables)
        assert is_function(function)

    def test_creates_a_call_graph_of_execution_for_user_objects(self):
        user_object = inspect_returning_single_callable(function_calling_method_which_calls_other_method)

        assert_instance(user_object, UserObject)
        assert_length(user_object.calls, 2)

        external_call = assert_one_element_and_return(user_object.get_external_calls())
        assert_equal('method', external_call.definition.name)

        subcall = assert_one_element_and_return(external_call.subcalls)
        assert_equal('other_method', subcall.definition.name)

    def test_creates_a_call_graph_of_execution_for_nested_calls(self):
        execution = inspect_returning_execution(function_with_nested_calls)

        assert_equal(expected_call_graph_for_function_with_nested_calls,
                     call_graph_as_string(execution.call_graph))

    def test_handles_functions_that_change_their_argument_bindings(self):
        call = inspect_returning_single_call(function_changing_its_argument_binding)

        assert_call({'a': 1, 'b': 2, 'c': 3}, (3, 2, 7), call)

    def test_saves_function_objects_as_types(self):
        function = inspect_returning_single_callable(function_returning_function)
        call = assert_one_element_and_return(function.calls)

        assert_equal('types.FunctionType', call.output.type_name)

    def test_correctly_recognizes_interleaved_ignored_and_traced_calls(self):
        callables = inspect_returning_callables(function_with_ignored_function, ['ignored'])

        assert_length(callables, 2)

        outer_function = find_first_with_name("not_ignored_outer", callables)
        inner_function = find_first_with_name("not_ignored_inner", callables)

        assert_length(outer_function.calls, 1)
        assert_length(inner_function.calls, 1)

        assert_call({'z': 13}, 75, outer_function.calls[0])
        assert_call({'x': 24}, 25, inner_function.calls[0])

class TestGenerators:
    def test_handles_yielded_values(self):
        generator = inspect_returning_single_callable(function_calling_generator)

        assert_instance(generator, Function)
        gobject = assert_one_element_and_return(generator.calls)

        assert_generator_object({'x': 2}, [2, 3, 4, 8], gobject)

    def test_handles_single_yielded_value(self):
        generator = inspect_returning_single_callable(function_calling_generator_that_yields_one)

        assert_instance(generator, Function)
        gobject = assert_one_element_and_return(generator.calls)

        assert_generator_object({}, [1], gobject)
        assert not gobject.raised_exception()

    def test_handles_yielded_nones(self):
        if hasattr(generator_has_ended, 'unreliable'):
            raise SkipTest

        gobject = inspect_returning_single_call(function_calling_generator_that_yields_none)

        assert_generator_object({}, [None], gobject)

    def test_handles_empty_generators(self):
        gobject = inspect_returning_single_call(function_calling_empty_generator)

        assert_generator_object({'x': 123}, [], gobject)

    def test_handles_generator_objects_that_werent_destroyed(self):
        gobject = inspect_returning_single_call(function_calling_generator_that_doesnt_get_destroyed)

        assert_generator_object({}, [1], gobject)

    def test_handles_generator_objects_that_yield_none_and_dont_get_destroyed(self):
        if hasattr(generator_has_ended, 'unreliable'):
            raise SkipTest

        gobject = inspect_returning_single_call(function_calling_generator_that_yields_none_and_doesnt_get_destroyed)

        assert_generator_object({}, [None], gobject)

    def test_handles_generator_methods(self):
        user_object = inspect_returning_single_callable(function_calling_generator_method)
        assert_instance(user_object, UserObject)

        gobject = assert_one_element_and_return(user_object.calls)
        assert_generator_object({}, [0, 1, 0], gobject)

    def test_handles_generators_called_not_from_top_level(self):
        callables = inspect_returning_callables(function_calling_function_that_uses_generator)

        assert_length(callables, 2)

        function = find_first_with_name("function", callables)

        fcall = assert_one_element_and_return(function.calls)

        gobject = assert_one_element_and_return(fcall.subcalls)
        assert_generator_object({'x': 2}, [2, 3, 4, 8], gobject)

class TestObjectsIdentityPreservation:
    def test_handles_passing_sequence_objects_around(self):
        callables = inspect_returning_callables(function_calling_functions_that_use_the_same_sequence_object)

        assert_length(callables, 2)

        producer = find_first_with_name("producer", callables)
        producer_call = assert_one_element_and_return(producer.calls)

        consumer = find_first_with_name("consumer", callables)
        consumer_call = assert_one_element_and_return(consumer.calls)

        assert_instance(producer_call.output, SequenceObject)
        assert_instance(consumer_call.input['lst'], SequenceObject)
        assert producer_call.output is consumer_call.input['lst']

    def test_handles_passing_user_objects_around(self):
        callables = inspect_returning_callables(function_calling_function_that_uses_the_same_user_object)

        assert_length(callables, 2)

        user_object = findfirst(is_user_object, callables)

        function = findfirst(is_function, callables)
        call = assert_one_element_and_return(function.calls)

        assert_instance(call.output, ImmutableObject)
        assert_equal(ImmutableObject(True), call.output)
        assert call.input['x'] is call.input['y'] is user_object

class TestRaisedExceptions(IgnoredWarnings):
    def test_handles_functions_which_raise_exceptions(self):
        def function_raising_an_exception():
            def function(x):
                raise ValueError()
            function(42)
        call = inspect_returning_single_call(function_raising_an_exception)

        assert_call_with_exception({'x': 42}, 'ValueError', call)

    def test_handles_functions_which_handle_other_function_exceptions(self):
        def function_handling_other_function_exception():
            def other_function(x):
                if not isinstance(x, int):
                    raise TypeError
                return x + 1
            def function(number):
                try:
                    return other_function(number)
                except TypeError:
                    return other_function(int(number))
            function("123")
        callables = inspect_returning_callables(function_handling_other_function_exception)
        function = find_first_with_name("function", callables)
        other_function = find_first_with_name("other_function", callables)

        assert_call_with_exception({'x': "123"}, 'TypeError', other_function.calls[0])
        assert_call({'x': 123}, 124, other_function.calls[1])
        assert_call({'number': "123"}, 124, function.calls[0])

    def test_handles_functions_which_raise_user_defined_exceptions(self):
        def function_raising_a_user_defined_exception():
            class UserDefinedException(Exception):
                pass
            def function(x):
                raise UserDefinedException()
            function(42)
        callables = inspect_returning_callables(function_raising_a_user_defined_exception)
        function = findfirst(is_function, callables)

        assert_call_with_exception({'x': 42}, 'UserDefinedException', function.calls[0])

    def test_handles_exceptions_raised_by_the_interpreter_like_index_error(self):
        def causes_interpreter_to_raise_index_error():
            def raising_index_error(): return [][0]
            try: raising_index_error()
            except: pass

        call = inspect_returning_single_call(causes_interpreter_to_raise_index_error)
        assert_call_with_exception({}, 'IndexError', call)

    def test_handles_exceptions_raised_by_the_interpreter_like_name_error(self):
        def causes_interpreter_to_raise_name_error():
            def raising_name_error(): return foobar
            try: raising_name_error()
            except: pass

        call = inspect_returning_single_call(causes_interpreter_to_raise_name_error)
        assert_call_with_exception({}, 'NameError', call)

    def test_handles_multiargument_exceptions_raised_by_the_interpreter_like_syntax_error(self):
        def causes_interpreter_to_raise_syntax_error():
            def raising_syntax_error(): exec 'a b c'
            try: raising_syntax_error()
            except: pass
        # Versions of Python up to 2.4 used None for a filename in syntax
        # errors invoked by exec.
        if sys.version_info >= (2, 5):
            filename = '<string>'
        else:
            filename = None
        syntax_error_exc_args = ('invalid syntax', (filename, 1, 3, 'a b c'))

        call = inspect_returning_single_call(causes_interpreter_to_raise_syntax_error)
        assert_call_with_exception({}, 'SyntaxError', call)

        exc = call.exception
        assert_instance(exc, BuiltinException)
        assert_collection_of_serialized(syntax_error_exc_args, exc.args)

    def test_handles_string_exceptions_without_values(self):
        # String exceptions were removed in Python 2.6.
        if sys.version_info >= (2, 6):
            raise SkipTest

        def raises_string_exception():
            def raising_string_exception():
                raise "deprecated"
            raising_string_exception()
        function = inspect_returning_single_callable(raises_string_exception)
        call = assert_one_element_and_return(function.calls)

        assert_call_with_string_exception({}, "deprecated", call)

    def test_handles_string_exceptions_with_values(self):
        # String exceptions were removed in Python 2.6.
        if sys.version_info >= (2, 6):
            raise SkipTest

        def raises_string_exception():
            def raising_string_exception():
                raise "this is not a drill", True
            raising_string_exception()
        function = inspect_returning_single_callable(raises_string_exception)
        call = assert_one_element_and_return(function.calls)

        assert_call_with_string_exception({}, "this is not a drill", call)

class TestExceptionsPassedAsValues:
    def test_builtin_exceptions_are_serialized_as_builin_exception_type_with_args_attribute(self):
        exc = serialize_value(AttributeError("foo", "bar"))

        assert_instance(exc, BuiltinException)
        assert_collection_of_serialized(("foo", "bar"), exc.args)

    def test_handles_passing_standard_exception_objects_as_arguments(self):
        def function_passing_eof_error():
            def error_printer(exc):
                pass
            error_printer(EOFError("The end", 101))
        call = inspect_returning_single_call(function_passing_eof_error)

        assert_call({'exc': EOFError("The end", 101)}, None, call)

    def test_handles_using_standard_exception_objects_as_return_values(self):
        def function_returning_os_error():
            def error_factory(num):
                return OSError(num)
            error_factory(42)
        call = inspect_returning_single_call(function_returning_os_error)

        assert_call({'num': 42}, OSError(42), call)

    def test_handles_catching_and_returning_interpreter_exceptions(self):
        def function():
            def returning_name_error():
                try:
                    no_such_variable # raises NameError
                except NameError, e:
                    return e
            returning_name_error()
        call = inspect_returning_single_call(function)

        assert_call({}, NameError("global name 'no_such_variable' is not defined"), call)

    def test_handles_exceptions_containing_user_objects(self):
        def function():
            class Something(object):
                pass
            def returning_exception_with_something():
                return OverflowError(Something())
            returning_exception_with_something()
        callables = inspect_returning_callables(function)
        function = findfirst(is_function, callables)
        user_object = findfirst(is_user_object, callables)

        call = assert_one_element_and_return(function.calls)
        user_object_in_exc = assert_one_element_and_return(call.output.args)
        assert user_object is user_object_in_exc

class TestTraceExec:
    "trace_exec"
    def test_returns_function_objects_with_all_calls_recorded(self):
        function = inspect_returning_single_callable("f = lambda x: x + 1; f(5); f(42)")

        assert_call({'x': 5},  6,  function.calls[0])
        assert_call({'x': 42}, 43, function.calls[1])

class TestInspectPointOfEntry(TempDirectory):
    def _init_project(self, module_code="", poe_content=""):
        self.project = TestableProject(self.tmpdir)
        putfile(self.project.path, "module.py", module_code)
        self.poe = PointOfEntryMock(self.project, content=poe_content)

    def test_properly_gathers_all_input_and_output_values_of_a_function_call(self):
        self._init_project("def function(x):\n  return x + 1\n",
                           "from module import function\nfunction(42)\n")

        inspect_point_of_entry(self.poe)

        assert_length(self.project["module"].functions, 1)
        assert_length(self.project["module"].functions[0].calls, 1)
        assert_call({'x': 42}, 43, self.project["module"].functions[0].calls[0])

    def test_properly_gathers_all_input_and_output_values_of_a_method_call(self):
        self._init_project("class SomeClass:\n  def some_method(self, x): return x + 1\n",
                           "from module import SomeClass\nSomeClass().some_method(42)\n")
        method = Method("some_method")
        klass = Class("SomeClass", methods=[method])
        self.project["module"].objects = [klass]

        inspect_point_of_entry(self.poe)

        user_object = assert_one_element_and_return(klass.user_objects)
        call = assert_one_element_and_return(user_object.calls)
        assert_call({'x': 42}, 43, call)

    def test_properly_wipes_out_imports_from_sys_modules(self):
        self._init_project(poe_content="import module")

        inspect_point_of_entry(self.poe)

        assert 'module' not in sys.modules
