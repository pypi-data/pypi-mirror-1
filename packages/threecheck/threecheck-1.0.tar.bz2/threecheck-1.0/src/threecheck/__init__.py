import inspect
import sys
import types

__author__ = ("Mattia Belletti <mattia@thick.foschia.info>")

__doc__ = '''
A simple typechecking package for Python 3000 through annotations.

Features:
- base type checking (int, float, str, ...)
- list, set, dict and tuple nested type checking (e.g.: list of int)
- contract checkers: callables, iterables, generic attribute checker
- boolean operators: and, or, not, xor (e.g.: int or float)
- support for *varargs and **kwargs
- fixed value check
- clear interface for extending with new checkers: criteria checker and more
  powerful Checker class subclassing

Planned features now missing:
- iterators management
- haskell-like type variables like on typecheck package
'''


#######################
# TYPECHECKING ENGINE #
#######################

def make_checker(description):
    '''
    Make an argument checker from a description.

    Parameters:
        description - the description from which is built the checker

    Return:
        The requested checker.
    '''
    if description is not None:
        if isinstance(description, Checker):
            return description
        elif isinstance(description, list) and len(description) > 0:
            assert len(description) == 1
            return List(description[0])
        elif isinstance(description, tuple):
            return Tuple(*description)
        elif isinstance(description, set) and len(description) > 0:
            assert len(description) == 1
            for x in description:
                return Set(x)
            assert False
        elif isinstance(description, dict) and len(description) > 0:
            assert len(description) == 1
            for key, value in description.items():
                return Dict(key, value)
            assert False
        elif isinstance(description, type):
            return Type(description)
        elif hasattr(description, '__call__'):
            return Criteria(description)
        else:
            raise TypeCheckFailed({'description':
                'description %s is not between known types' % repr(description)})
    else:
        return Any

def _make_argvalues_checker(func):
    '''
    Make a function which can check the arguments of the function.

    Parameters:
        func - the function to make a checker for.

    Return:
        A checker function.
    '''
    fas = inspect.getfullargspec(func)
    checkers = []
    for argument in fas.args:
        ann = None
        if argument in fas.annotations:
            ann = fas.annotations[argument]
        c = make_checker(ann)
        assert isinstance(c, Checker), \
            'annotation %s produces a %s' % (repr(ann), repr(c))
        checkers.append((argument, c))
    checkers_dict = dict(checkers)
    varargchecker = None
    if fas.varargs is not None:
        ann = fas.annotations.get(fas.varargs)
        varargchecker = make_checker(ann)
        assert isinstance(varargchecker, Checker), \
            'annotation %s produces a %s' % (repr(ann), repr(c))
    varkwchecker = None
    if fas.varkw is not None:
        ann = fas.annotations.get(fas.varkw)
        varkwchecker = make_checker(ann)
        assert isinstance(varkwchecker, Checker), \
            'annotation %s produces a %s' % (repr(ann), repr(c))
    def checker(*args, **kwargs):
        # standard non-keyword arguments
        for i in range(min(len(args), len(checkers))):
            e = checkers[i][1].error(args[i], args, kwargs)
            if e: raise TypeCheckFailed({fas.args[i]: e})
        # sovrannumerary arguments match with "*args"
        if len(args) > len(checkers):
            assert fas.varargs is not None
            e = varargchecker.error(args[len(fas.args):], args, kwargs)
            if e: raise TypeCheckFailed({fas.varargs: e})
        # keyword arguments
        skipped_kwargs = {}
        for name, value in kwargs.items():
            if name in checkers_dict:
                e = checkers_dict[name].error(value, args, kwargs)
                if e: raise TypeCheckFailed({name: e})
            else:
                skipped_kwargs[name] = value
        # **kwargs element
        if len(skipped_kwargs):
            assert varkwchecker is not None
            e = varkwchecker.error(skipped_kwargs, args, kwargs)
            if e: raise TypeCheckFailed({fas.varkw: e})
    return checker

def _make_retvalue_checker(func):
    '''
    Make a function which can check the return value of the function.

    Parameters:
        func - the function to make a checker for.

    Return:
        A checker function.
    '''
    fas = inspect.getfullargspec(func)
    anns = fas.annotations
    c = make_checker(anns.get('return'))
    assert isinstance(c, Checker), \
        'annotation return produces a ' % repr(c)
    def checker(retvalue):
        e = c.error(retvalue, (), {})
        if e: raise TypeCheckFailed({'return value': e})
    return checker

def typecheck(func):
    '''
    Decorator to apply typechecking to a function with decorators.
    '''
    checker = _make_argvalues_checker(func)
    retchecker = _make_retvalue_checker(func)
    def checker_function(*args, **kwargs):
        checker(*args, **kwargs)
        retvalue = func(*args, **kwargs)
        if isinstance(retvalue, types.GeneratorType):
            generator = retvalue    # let's name it properly
            def mygenerator():
                tosend = None
                v = next(generator)
                retchecker(v)
                tosend = yield v
                while True:
                    value = generator.send(tosend)
                    retchecker(value)
                    tosend = yield value
            return mygenerator()
        else:
            retchecker(retvalue)
            return retvalue
    checker_function.__annotations__ = func.__annotations__
    return checker_function

class TypeCheckFailed(Exception):
    '''
    A type check has failed.
    '''
    def __init__(self, errors: {str: str}):
        '''
        Create a new TypeCheckFailed exception.

        Parameters:

            errors - a map between argument names and error descriptions
        '''
        self.errors = errors
        Exception.__init__(self, str(self))

    def __str__(self):
        return 'type check failed; ' + '\n'.join([
            '%s: %s' % (argument, error)
            for argument, error
            in self.errors.items()
        ])

class Checker:
    '''
    An argument checker. This is the base class for all the checkers, and the
    place where to look for making a new, complete checker. Subclassers need to
    implement the following methods of the object:

        - error
        - ok_message
        - __eq__
        - __str__ optionally
    '''

    def error(self, value, args, kwargs):
        '''
        Check whether a value respect this checker's criteria.

        Parameters:
            value - the value to check
            args - the non-keyword arguments to the function
            kwargs - the keyword arguments to the function

        Return:
            Empty string if no error is found, or a string containing an error
            description otherwise.
        '''
        raise NotImplementedError()

    def ok_message(self):
        '''
        Produce a message which tells the reason why a check can succeeded for
        this class. E.g.: if we have a type check for int, it would produce
        the message "is an int". Typical use case for this method is in the
        error method of compound, negative checkers like 'Not' and 'Xor'.

        Return:
            An ok message.
        '''
        raise NotImplementedError()

    def __or__(c1, c2):
        return Or(c1, c2)

    def __and__(c1, c2):
        return And(c1, c2)

    def __invert__(self):
        return Not(self)

    def __xor__(c1, c2):
        return Xor(c1, c2)

    def __eq__(c1, c2):
        raise NotImplementedError()

    def __str__(self):
        return '*'


################
# TYPECHECKERS #
################

class _Any(Checker):
    '''
    A checker which is always satisfied. Mainly used by the internal machinery,
    rarely needed outside.
    '''
    def error(self, value, args, kwargs):
        return ''
    def ok_message(self):
        return 'is a value'
    def __eq__(c1, c2):
        return isinstance(c2, _Any)
    def __str__(self):
        return 'Any'
Any = _Any()

class Type(Checker):
    '''
    A checker which checks the type of values. The shorthand for this checker
    understood by the make_checker method is just the type itself; that is:

    >>> Type(int) == make_checker(int)
    True

    You can also use a string to create a type; in this case the symbol name
    given in the string will be lazily resolved at execution time. This is
    useful for resolving mutual references::

    >>> F2 = Type("F2")
    >>> class F1:
    ...   def m2(self: Self, f2: F2):
    ...     pass
    ...
    >>> class F2:
    ...   def m1(self: Self, f1: F1):
    ...     pass
    ...

    Also the inline style is supported::

    >>> class F1:
    ...   def m2(self: Self, f2: Type("F2")):
    ...     pass
    ...
    >>> class F2:
    ...   def m1(self: Self, f1: F1):
    ...     pass
    ...
    '''
    def __init__(self, t: [type, str]):
        '''
        Create a new Type.

        Parameters:

            t - the type the values must belong to according to the
                `isinstance` method.
        '''
        self._type = t
        self._frame = None
        if isinstance(t, str):
            self._frame = sys._getframe(1)
            if '__locals__' in self._frame.f_locals:
                # in class definition, using the inline form: go back one more
                # step
                self._frame = sys._getframe(2)
    def _lazy_initialize(self):
        # cause the lazy initialization of the super class (Type) if needed
        # taken and adapted from the 'typecheck' project:
        # http://oakwinter.com/code/typecheck/
        if self._frame is not None:
            assert isinstance(self._type, str)
            cname = self._type
            frame = self._frame
            for f_dict in (frame.f_locals, frame.f_globals):
                if cname in f_dict and self is not f_dict[cname]:
                    self._frame = None  # for garbage collection
                    self._type = f_dict[cname]
                    break
            else:
                raise NameError("name '%s' is not defined" % cname)
    def error(self, value, args, kwargs):
        self._lazy_initialize()
        if isinstance(value, self._type): return ''
        else:
            return '%s not of type %s.%s' % (
                repr(value),
                self._type.__module__,
                self._type.__name__)
    def ok_message(self):
        self._lazy_initialize()
        return 'is of type %s.%s' % (
            self._type.__module__,
            self._type.__name__)
    def __eq__(a, b):
        a._lazy_initialize()
        return isinstance(b, Type) and a._type is b._type
    def __str__(self):
        if self._frame is None:
            m = self.type.__module__
            n = self.type.__name__
        else:
            m = self._frame.f_locals['__name__']
            n = self._type
        return 'Type(%s.%s)' % (m, n)

class Attrs(Checker):
    '''
    A checker which checks that values have some set of attributes. Look also
    at Callable and Iterable.
    '''
    def __init__(self, *attributes): # attributes: [Or(str, {str: Any})]
        self._attributes = {}
        for a in attributes:
            if isinstance(a, str):
                self._attributes[a] = Any
            elif isinstance(a, dict):
                for attr, checker in a.items():
                    self._attributes[attr] = make_checker(checker)
                    assert isinstance(self._attributes[attr], Checker)
            else:
                raise TypeCheckFailed({'attributes': \
                    "attributes can only be str or dict, not %s" % type(a)})
    def error(self, value, args, kwargs):
        for attr, checker in self._attributes.items():
            if not hasattr(value, attr):
                return '%s has no attribute %s' % (repr(value), attr)
            else:
                e = checker.error(getattr(value, attr), args, kwargs)
                if e: return e
        return ''
    def ok_message(self):
        return 'has attribute(s) %s' % \
            ', '.join([
                '%s (and it was true that %s)' % (attr, checker.ok_message())
                for attr, checker
                in self._attributes])
    def __eq__(a, b):
        return isinstance(b, Attrs) and \
            set(a._attributes.keys()) == set(b._attributes.keys())
    def __str__(self):
        return 'Attrs(%s)' % ', '.join(self._attributes)

class Value(Checker):
    '''
    A checker which checks that the parameter has an exact value.
    '''
    def __init__(self, value):
        self._value = value
    def error(self, value, args, kwargs):
        return '' if value == self._value else '%s != %s' % (repr(value), repr(self._value))
    def ok_message(self):
        return 'is %s' % repr(self._value)
    def __eq__(a, b):
        return isinstance(b, Value) and a._value == b._value
    def __str__(self):
        return 'Value(%s)' % repr(self._value)

class Range(Checker):
    '''
    A checker which checks that the parameter falls within a certain range.
    '''
    def __init__(self, min = None, max = None):
        '''
        Create a new range checker.

        Parameters:
            min - the minimum value for the range; if None, there's no lower
                  bound
            max - the maximum value for the range; if None, there's no upper
                  bound
        '''
        self._min = min
        self._max = max
    def error(self, value, args, kwargs):
        if ((self._min is None or value >= self._min) and
            (self._max is None or value <= self._max)):
            return ''
        else:
            return '%s not in [%s;%s]' % (
                repr(value), repr(self._min), repr(self._max))
    def ok_message(self):
        return 'is in [%s;%s]' % (repr(self._min), repr(self._max))
    def __eq__(a, b):
        return isinstance(b, Range) and a._min == b._min and a._max == b._max
    def __str__(self):
        return 'Range(%s,%s)' % (repr(self._min), repr(self._max))

class Criteria(Checker):
    '''
    A checker which checks that some specific criteria is respected. The
    shorthand for this is just the callable object itself. E.g.:

    >>> def even(x): return x % 2 == 0
    >>> make_checker(even) == Criteria(even)
    True
    '''
    def __init__(self, criteria):
        '''
        Create a new criteria checker.

        Parameters:
            criteria - the callable used to check for the criteria; if returns
                       a true value, then the criteria is considered as passed,
                       otherwise it is raised an error; the __name__ of the
                       criteria object is used in the error message, if
                       present.
        '''
        self._criteria = criteria
    def error(self, value, args, kwargs):
        if not self._criteria(value):
            return 'value %s do not satisfy criteria %s' % (
                repr(value),
                getattr(self._criteria, '__name__', ''))
        else:
            return ''
    def ok_message(self):
        return 'satisfy criteria %s' % (
            getattr(self._criteria, '__name__', ''))
    def __eq__(a, b):
        return a._criteria == b._criteria
    def __str__(self):
        return 'Criteria(%s)' % getattr(self._criteria, '__name__', '')

class And(Checker):
    '''
    A checker which is satisfied only if all the subcheckers are. The '&'
    bitwise operator defaults to this checker. E.g.:

    >>> Callable & Iterable == And(Callable, Iterable)
    True
    '''
    def __init__(self, *checkers):
        checkers = list(map(make_checker, checkers))
        self._checkers = checkers
    def error(self, value, args, kwargs):
        for checker in self._checkers:
            e = checker.error(value, args, kwargs)
            if e: return e
        return ''
    def ok_message(self):
        return ' and '.join([c.ok_message() for c in self._checkers])
    def __eq__(a, b):
        if not isinstance(b, And): return False
        if len(a._checkers) != len(b._checkers): return False
        for a_checker in a._checkers:
            found = False
            for b_checker in b._checkers:
                if a_checker == b_checker:
                    found = True
                    break
            if not found: return False
        return True
    def __str__(self):
        return ' && '.join(['(%s)' % str(ch) for ch in self._checkers])

class Or(Checker):
    '''
    A checker which is satisfied if at least one subchecker is. The '|' bitwise
    operator defaults to this checker. E.g.:

    >>> Callable | Iterable == Or(Callable, Iterable)
    True
    '''
    def __init__(self, *checkers):
        checkers = list(map(make_checker, checkers))
        self._checkers = checkers
    def error(self, value, args, kwargs):
        es = []
        for checker in self._checkers:
            e = checker.error(value, args, kwargs)
            if not e: return ''
            else: es.append(e)
        return ' and '.join(es)
    def ok_message(self):
        return ' or '.join([c.ok_message() for c in self._checkers])
    def __eq__(a, b):
        if not isinstance(b, Or): return False
        if len(a._checkers) != len(b._checkers): return False
        for a_checker in a._checkers:
            found = False
            for b_checker in b._checkers:
                if a_checker == b_checker:
                    found = True
                    break
            if not found: return False
        return True
    def __str__(self):
        return ' || '.join(['(%s)' % str(ch) for ch in self._checkers])

def Xor(*checkers):
    '''
    A checker which is satisfied if only one subchecker is. The '^' bitwise
    operator defaults to this checker. E.g.:

    >>> Callable ^ Iterable == Xor(Callable, Iterable)
    True
    '''
    # e.g.: |(&(C1, -C2, -C3), &(C2, -C1, -C3), &(C3, -C1, -C2))
    return Or(*[
        And(*([checker] + [
            Not(checker2)
            for checker2
            in checkers
            if checker is not checker2]))
        for checker
        in checkers])

class Not(Checker):
    '''
    A checker which is satisfied only if its subchecker is not. The bitwise '~'
    operator defaults to this checker. E.g.:

    >>> ~Callable == Not(Callable)
    True
    '''
    def __init__(self, checker):
        self._checker = make_checker(checker)
    def error(self, value, args, kwargs):
        e = self._checker.error(value, args, kwargs)
        if e: return ''
        else: return 'for %s was true that %s' % (repr(value), self._checker.ok_message())
    def ok_message():
        return 'it is not true that %s' % self._checker.ok_message()
    def __eq__(a, b):
        return isinstance(b, Not) and a._checker == b._checker
    def __str__(self):
        return '!(%s)' % str(self._checker)

def NotNone(checker = Any):
    '''
    A checker which is the same of the passed checker, but exclude the None
    value.
    '''
    if not isinstance(checker, Checker):
        checker = make_checker(checker)
    return checker & ~Value(None)

def Nullable(checker = Any):
    '''
    A checker which is the same of the passed checker, but allow the None
    value.
    '''
    if not isinstance(checker, Checker):
        checker = make_checker(checker)
    return checker | Value(None)

Positive = (Type(int) | Type(float)) & Range(min=0)

class Iterable(Or):
    '''
    A checker which checks if a value can be iterated, that is, can be argument
    of a 'for'.
    '''
    def __init__(self, subtype = None):
        Or.__init__(self, Attrs({'__iter__': Callable}),
           Attrs({'__getitem__': Callable}),
           Attrs({'next': Callable}))
        self._subchecker = make_checker(subtype)
    def error(self, value, args, kwargs):
        e = Or.error(self, value, args, kwargs)
        if e: return e
        else:
            for v in value:
                e = self._subchecker.error(v, args, kwargs)
                if e: return e
        return ''
    def ok_message(self):
        return 'is a sequence and every element %s' % (
            repr(value),
            self._subchecker.ok_message())
    def __eq__(a, b):
        return isinstance(b, Iterable) and Or.__eq__(a, b) and \
            a._subchecker == b._subchecker
    def __str__(self):
        return 'Iterable(%s)' % str(self._subchecker)

def List(subtype = None):
    '''
    A checker which checks if a value is a list, optionally containing only
    values respecting certain checkers. The shorthand for this operator is the
    list constructor itself. E.g.:

    >>> make_checker([int]) == List(Type(int))
    True
    '''
    return Iterable(subtype) & Type(list)

class Dict(Type):
    def __init__(self, keys, values):
        Type.__init__(self, dict)
        self._key_checker = make_checker(keys)
        self._value_checker = make_checker(values)
    def error(self, value, args, kwargs):
        e = Type.error(self, value, args, kwargs)
        if e: return e
        else:
            for key, value in value.items():
                e = self._key_checker.error(key, args, kwargs)
                if e: return e
                e = self._value_checker.error(value, args, kwargs)
                if e: return e
        return ''
    def ok_message(self):
        return 'is a dictionary where every key %s and every value %s' % (
            self._key_checker.ok_message(),
            self._value_checker.ok_message())
    def __eq__(a, b):
        return Type.__eq__(a, b) and a._key_checker == b._key_checker and \
            a._value_checker == b._value_checker
    def __str__(self):
        return 'Dict(%s->%s)' % (str(self._key_checker), str(self._value_checker))

def Set(subtype = None):
    return Type(set) & Iterable(subtype)

def VarTuple(subtype = None):
    return Type(tuple) & Iterable(subtype)

class Tuple(Type):
    def __init__(self, *subtypes):
        Type.__init__(self, tuple)
        self._subcheckers = list(map(make_checker, subtypes))
    def error(self, value, args, kwargs):
        e = Type.error(self, value, args, kwargs)
        if e: return e
        elif len(self._subcheckers):
            if len(value) != len(self._subcheckers):
                return 'tuple has %d elements instead of %d' % (
                    len(value), len(self._subcheckers))
            else:
                for value, checker in zip(value, self._subcheckers):
                    e = checker.error(value, args, kwargs)
                    if e: return e
        return ''
    def ok_message(self):
        e = 'is a tuple'
        if len(self._subcheckers):
            e = e + ' where %s' % \
                ' and '.join([
                    'element %s %s' % (n, m.ok_message())
                    for n, m
                    in zip(range(2**64), self._subcheckers)])
        return e
    def __eq__(a, b):
        return isinstance(b, Tuple) and \
            all([ch1 == ch2 for ch1, ch2 in zip(a._subcheckers, b._subcheckers)])
    def __str__(self):
        return 'Tuple(%s)' % ', '.join([str(c) for c in self._subcheckers])

Callable = Attrs('__call__')

Number = Or(int, float, complex)

class _SelfClass(Checker):
    def error(self, value, args, kwargs):
        t = type(args[0])
        if isinstance(value, t):
            return ''
        else:
            return '%s not of type %s' % (value, t.__name__)
    def ok_message(self):
        'is of the same type of the containing class'
    def __eq__(a, b):
        return isinstance(b, _SelfClass)
    def __str__(self):
        'SelfClass'
SelfClass = _SelfClass()

# generator management

class Generation(Checker):
    '''
    An abstract base class to produce checkers which keeps track also of the
    number of times it was called. To use tipically with generators.

    This class is instantiated by giving a generator of checker methods, which
    will be used one after the other to implement the 'error' method. The error
    method signature is:

    >>> error(self, num, value, args, kwargs)

    Where 'num' is the number of the call (0-based), and the other arguments
    are the same of the 'error' method in the Checker class.
    '''
    def __init__(self, checkerGenerator):
        '''
        Create a new Generation instance.

        :Parameters:
            checkerGenerator : generator(callable)
                A generator which produce the checker method to use, one after
                the other.
        '''
        self._checkerGenerator = checkerGenerator
        self._num = 0
    def error(self, value, args, kwargs):
        try:
            checker = next(self._checkerGenerator)
            ret = checker(self._num, value, args, kwargs)
            self._num += 1
            return ret
        except StopIteration:
            return "this generator/function should have returned no more values"
    def ok_message(self):
        return 'the value %d is correct' % self._num
    def __eq__(a, b):
        return (isinstance(b, Generation) and
                a._num == b._num and
                a._checkerGenerator == b._checkerGenerator)
    def __str__(self):
        return 'Generation(%s)@%d' % (self._checkerGenerator, self._num)

class _SequenceBase(Generation):
    '''
    Represents a generation of a finite set of values, which can indefinitely
    loop or be accepted just one time (after which an error happens).
    '''
    def __init__(self, loop: bool, types: list):
        '''
        Create a new sequence.
        '''
        # create the checker functions
        checkers = [
            lambda num, value, args, kwargs: ch(value, args, kwargs)
            for ch
            in map(make_checker, types)]
        # create the generator of checker functions
        generator = iter(checkers)
        if loop: generator = itertools.cycle(generator)
        # initialize
        super().__init__(generator)
