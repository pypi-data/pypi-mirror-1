import unittest
import threecheck as tc
import types

class BaseTestCase(unittest.TestCase):
    def typeCheckFails(self, value, *args, **kwargs):
        self.assertRaises(tc.TypeCheckFailed,
            value, *args, **kwargs)

class TestTypeCheck(BaseTestCase):
    '''
    Test the base typechecking (int, str, ...).
    '''
    def _testWith(self, t, value, fails = False):
        @tc.typecheck
        def f(x: t): pass
        if fails:
            self.typeCheckFails(
                lambda: f(value))
        else:
            f(value)

    def testIntOk(self):
        self._testWith(int, 3)

    def testIntWithStr(self):
        self._testWith(int, '3', True)

    def testIntWithFloat(self):
        self._testWith(int, 3.0, True)

    def testIntWithObj(self):
        class Duck: pass
        self._testWith(int, Duck(), True)

    def testIntWithIntDerivedObj(self):
        class Duck(int): pass
        self._testWith(int, Duck())

    def testStrWithInt(self):
        self._testWith(str, 3, True)

    def testStrWithStr(self):
        self._testWith(str, '3')

    def testStrWithFloat(self):
        self._testWith(str, 3.0, True)

    def testStrWithObj(self):
        class Duck: pass
        self._testWith(str, Duck(), True)

    def testStrWithIntDerivedObj(self):
        class Duck(str): pass
        self._testWith(str, Duck())

    def testObjLazyOk(self):
        d = tc.Type('Duck')
        l = lambda: self._testWith(d, Duck())
        class Duck(int): pass
        l()

    def testObjLazyFail(self):
        d = tc.Type('Duck')
        l = lambda: self._testWith(d, 3, True)
        class Duck(int): pass
        l()

    def testObjLazyNameError(self):
        d = tc.Type('DDuck')
        l = lambda: self._testWith(d, Duck(), True)
        class Duck(int): pass
        self.assertRaises(NameError, l)

    def testObjLazyMutualInline(self):
        class F1:
            @tc.typecheck
            def m2(self, f2: tc.Type("F2")) -> tc.Type("F2"):
                return f2
        class F2:
            @tc.typecheck
            def m1(self, f1: F1) -> F1:
                return f1
        f1 = F1()
        f2 = F2()
        f1.m2(f2)
        f2.m1(f1)
        self.typeCheckFails(f1.m2, f1)
        self.typeCheckFails(f2.m1, f2)

    def testObjLazyMutualNotInline(self):
        F2 = tc.Type("F2")
        class F1:
            @tc.typecheck
            def m2(self, f2: F2) -> F2:
                return f2
        class F2:
            @tc.typecheck
            def m1(self, f1: F1) -> F1:
                return f1
        f1 = F1()
        f2 = F2()
        f1.m2(f2)
        f2.m1(f1)
        self.typeCheckFails(f1.m2, f1)
        self.typeCheckFails(f2.m1, f2)

class TestTypeCheckList(BaseTestCase):
    '''
    Test the list type.
    '''
    def testIntListOk(self):
        @tc.typecheck
        def f(a: [int]) -> [int]: return a
        f([1,2,3])
    def testIntListWithStr(self):
        @tc.typecheck
        def f(a: [int]) -> str: return a
        self.typeCheckFails(
            lambda: f('3'))
    def testIntListWithStrList(self):
        @tc.typecheck
        def f(a: [int]) -> [str]: return a
        self.typeCheckFails(
            lambda: f(['3', '4']))

class TestTypeCheckDict(BaseTestCase):
    '''
    Test the dict type.
    '''
    @tc.typecheck
    def f(self, a: {int: float}) -> {int: float}: return a
    def testIntFloatDictOk(self):
        self.f({1: 1.0, 2: 2.0, 3: 3.0})
    def testIntFloatDictWithStr(self):
        self.typeCheckFails(
            lambda: self.f('3'))
    def testIntFloatDictWithIntStrDict(self):
        self.typeCheckFails(
            lambda: self.f({1: '1', 2: '2'}))

class TestTypeCheckSet(BaseTestCase):
    '''
    Test the set type.
    '''
    @tc.typecheck
    def f(self, a: {int}) -> {float}:
        return set(map(float, a))
    def testIntSetOk(self):
        self.f({1, 2, 3})
    def testIntSetWithStr(self):
        self.typeCheckFails(
            lambda: self.f('3'))
    def testIntSetWithStrSet(self):
        self.typeCheckFails(
            lambda: self.f({'1', '2'}))

class TestCallable(BaseTestCase):
    '''
    Test the Callable check.
    '''
    @tc.typecheck
    def f(self, f: tc.Callable) -> tc.Callable:
        return lambda *args, **kwargs: f(*args, **kwargs)
    def testFunc(self):
        self.f(self.testFunc)
    def testLambda(self):
        self.f(lambda x: x*2)
    def testConstructor(self):
        class Duck: pass
        self.f(Duck)
    def testIntFail(self):
        self.typeCheckFails(lambda: self.f(3))
    def testListFail(self):
        self.typeCheckFails(lambda: self.f([1, 2]))

class TestOr(BaseTestCase):
    '''
    Test the 'or' condition between two other checks.
    '''
    @tc.typecheck
    def f(self, x: tc.Or(int, str)) -> tc.Or(float, str):
        if x == 999:
            return x    # to cause type check failure
        if isinstance(x, int):
            return float(x)
        else:
            return x
    def testTwoTypesWithInt(self):
        self.f(3)
    def testTwoTypesWithString(self):
        self.f('ciao')
    def testTwoTypesWithFloat(self):
        self.typeCheckFails(lambda: self.f(3.0))
    def testTwoTypesWith999(self):
        self.typeCheckFails(lambda: self.f(999))

class _TestAnd:
    class T1: pass
    class T2: pass
    class T12(T1, T2): pass
    class T11(T1): pass
    class T22(T2): pass
class TestAnd(BaseTestCase):
    '''
    Test the 'and' condition between two other checks.
    '''
    @tc.typecheck
    def f(self, x: tc.And(_TestAnd.T1, _TestAnd.T2)): return 4
    def testT1(self):
        self.typeCheckFails(lambda: self.f(_TestAnd.T1()))
    def testT2(self):
        self.typeCheckFails(lambda: self.f(_TestAnd.T2()))
    def testT11(self):
        self.typeCheckFails(lambda: self.f(_TestAnd.T11()))
    def testT22(self):
        self.typeCheckFails(lambda: self.f(_TestAnd.T22()))
    def testT12(self):
        self.f(_TestAnd.T12())

class TestAttrs(BaseTestCase):
    '''
    Test the Attrs checker.
    '''
    @tc.typecheck
    def f(self, x: tc.Attrs('__and__')): pass
    def testInt(self):
        self.f(3)
    def testStr(self):
        self.typeCheckFails(lambda: self.f('3'))

class TestIterable(BaseTestCase):
    '''
    Test the Iterable checker.
    '''
    @tc.typecheck
    def f(self, x: tc.Iterable()): pass
    @tc.typecheck
    def g(self, x: tc.Iterable(int)): pass
    def testInt(self):
        self.typeCheckFails(lambda: self.f(3))
        self.typeCheckFails(lambda: self.g(3))
    def testStrList(self):
        self.f(['3', '4'])
        self.typeCheckFails(lambda: self.g(['3', '4']))
    def testIntList(self):
        self.f([3, 4])
        self.g([3, 4])
    def testStrSet(self):
        self.f({'3', '4'})
        self.typeCheckFails(lambda: self.g({'3', '4'}))
    def testIntSet(self):
        self.f({3, 4})
        self.g({3, 4})
    def testStrGenerator(self):
        def gen():
            yield '3'
            yield '4'
        self.f(gen())
        self.typeCheckFails(lambda: self.g(gen()))
    def testIntGenerator(self):
        def gen():
            yield 3
            yield 4
        self.f(gen())
        self.g(gen())

class TestComplex(BaseTestCase):
    '''
    Test a complex type expression.
    '''
    @tc.typecheck
    def analyze(self, data: {str: {float: int}}) -> {float: {int: tc.Iterable(str)}}:
        ret = {}
        for testName, testData in data.items():
            for value, times in testData.items():
                if value not in ret:
                    ret[value] = {}
                if times not in ret[value]:
                    ret[value][times] = []
                ret[value][times].append(testName)
        return ret

    def testAnalyzeOk(self):
        self.analyze({
            'a': {
                4.0: 5,
                2.0: 6,
                3.0: 7,
                8.0: 9
            },
            'b': {
                3.0: 2,
                4.0: 5,
                1.2: 3,
                8.0: 7
            }
        })
    def testAnalyzeTimesError(self):
        self.typeCheckFails(lambda: self.analyze({
            'a': {
                4.0: 5,
                2.0: 6,
                3.0: '7',
                8.0: 9
            },
            'b': {
                3.0: 2,
                4.0: 5,
                1.2: 3,
                8.0: 7
            }
        }))
    def testAnalyzeValueError(self):
        self.typeCheckFails(lambda: self.analyze({
            'a': {
                4.0: 5,
                '2.0': 6,
                3.0: 7,
                8.0: 9
            },
            'b': {
                3.0: 2,
                4.0: 5,
                1.2: 3,
                8.0: 7
            }
        }))
    def testAnalyzeNameError(self):
        self.typeCheckFails(lambda: self.analyze({
            2: {
                4.0: 5,
                2.0: 6,
                3.0: 7,
                8.0: 9
            },
            'b': {
                3.0: 2,
                4.0: 5,
                1.2: 3,
                8.0: 7
            }
        }))

class TestTuple(BaseTestCase):
    @tc.typecheck
    def f(self, x: (int, str, float)) -> [(float, str, int)]:
        return [(x[2], x[1], x[0])] * 5
    def testTupleOk(self):
        self.f( (3, '3', 3.0) )
    def testTupleTooLong(self):
        self.typeCheckFails(lambda: self.f( (3, '3', 3.0, 4) ))
    def testTupleTooShort(self):
        self.typeCheckFails(lambda: self.f( (3, '3') ))
    def testTupleWrongType(self):
        self.typeCheckFails(lambda: self.f( (3, 3, 3.0) ))

class TestVarTuple(BaseTestCase):
    @tc.typecheck
    def f(self, x: tc.VarTuple(int)) -> [(int, float)]:
        if len(x):
            return [(x[0], float(x[0]))] * 5
        else:
            return []
    def testVarTupleOk(self):
        self.f( (3, 4, 5) )
    def testVarTupleWrongType(self):
        self.typeCheckFails(lambda: self.f( (3, 4, '5') ))
    def testVarTupleOk2(self):
        self.f( () )

class TestFixedValue(BaseTestCase):
    @tc.typecheck
    def f(self, x: tc.Value(4) | tc.Value(5) | tc.Value(6)) -> \
        tc.Value(8) | tc.Value(10):  # "12" is missing
        return x*2
    def testValue4(self):
        self.f(4)
    def testValue5(self):
        self.f(5)
    def testValue3(self):
        self.typeCheckFails(lambda: self.f(3))
    def testValue6(self):
        self.typeCheckFails(lambda: self.f(6))

class TestRange(BaseTestCase):
    @tc.typecheck
    def f(self, x: tc.Range(4, 8) | tc.Value(11)) -> \
        tc.Range(8, 15) | tc.Value(22):  # "16" is missing
        return x*2
    @tc.typecheck
    def g(self, x: tc.Range(max=8)) -> \
        tc.Range(max=15):  # "16" is missing
        return x*2
    @tc.typecheck
    def h(self, x: tc.Range(min=4)) -> \
        tc.Range(min=9):  # "8" is missing
        return x*2
    def testRange4(self):
        self.f(4)
        self.g(4)
        self.typeCheckFails(self.h, 4)
    def testRange5(self):
        self.f(5)
        self.g(5)
        self.h(5)
    def testRange7(self):
        self.f(7)
        self.g(7)
        self.h(7)
    def testRange3(self):
        self.typeCheckFails(self.f, 3)
        self.g(3)
        self.typeCheckFails(self.h, 3)
    def testRange8(self):
        self.typeCheckFails(self.f, 8)
        self.typeCheckFails(self.g, 8)
        self.h(8)
    def testRange11(self):
        self.f(11)
        self.typeCheckFails(self.g, 11)
        self.h(11)

class TestNot(BaseTestCase):
    @tc.typecheck
    def f(self, x: tc.Type(int) & ~tc.Value(10)) -> int:
        return x+1
    def testNotWithInt(self):
        self.f(3)
    def testNotWithInt10(self):
        self.typeCheckFails(lambda: self.f(10))
    def testNotWithStr(self):
        self.typeCheckFails(lambda: self.f('3'))

class _TestXor:
    class T1: pass
    class T2: pass
    class T12(T1, T2): pass
class TestXor(BaseTestCase):
    @tc.typecheck
    def f(self, x: tc.Xor(_TestXor.T1, _TestXor.T2)) -> int:
        return 3
    def testXorWithT1(self):
        self.f(_TestXor.T1())
    def testXorWithT2(self):
        self.f(_TestXor.T1())
    def testXorWithInt(self):
        self.typeCheckFails(lambda: self.f(3))
    def testXorWithT12(self):
        self.typeCheckFails(lambda: self.f(_TestXor.T12()))

class TestVarargsAndKwargs(BaseTestCase):
    '''
    Test the *args and **kwargs arguments.
    '''
    @tc.typecheck
    def f(self, x: int, *args: tc.VarTuple(int), **kwargs: {str: int}) -> int:
        return x + sum(args) + sum(kwargs.values())
    def testVOkKWOk(self):
        self.f(3, 45, 6, a=3, b=5)
    def testVOkKWWrong(self):
        self.typeCheckFails(lambda: self.f(3, 45, 6, a='3', b=5))
    def testVWrongKWOk(self):
        self.typeCheckFails(lambda: self.f(3, 45.0, 6, a=3, b=5))
    def testVWrongKWWrong(self):
        self.typeCheckFails(lambda: self.f(3, 45.0, 6, a='3', b=5))

class _TestSelf:
    class Rec:
        @tc.typecheck
        def __init__(self: tc.SelfClass, inner: tc.SelfClass | tc.Value(None)):
            self.inner = inner
class TestSelf(BaseTestCase):
    '''
    Test the SelfClass checker.
    '''
    def testNone(self):
        _TestSelf.Rec(None)
    def testInnerAndNone(self):
        r = _TestSelf.Rec(None)
        _TestSelf.Rec(r)
    def testInnerAndWrong(self):
        self.typeCheckFails(lambda: _TestSelf.Rec(3))

class TestGenerator(BaseTestCase):
    '''
    The the generators.
    '''
    def testGeneratorOk(self):
        @tc.typecheck
        def generatorOfInts(start, end) -> int:
            for i in range(start, end):
                yield i
        for x in generatorOfInts(3, 6):
            pass

    def testGeneratorNotOk(self):
        @tc.typecheck
        def generatorOfInts(start, end) -> int:
            for i in range(start, end):
                if i == (start+end)//2:
                    yield "a number"
                yield i
        def fail():
            for x in generatorOfInts(3, 6):
                pass
        self.typeCheckFails(fail)

    def testGeneratorWithSendNotOk(self):
        @tc.typecheck
        def coroutine(start: int) -> tc.Type(int) & ~tc.Value(33):
            seed = start
            while seed != 10:
                seed = yield (seed + 1)
        self.assert_(isinstance(coroutine, types.FunctionType),
            'coroutine is not a function, it is: %s' % repr(coroutine))
        c = coroutine(5)
        self.assert_(isinstance(c, types.GeneratorType),
            'coroutine(5) is not a generator, it is: %s' % repr(c))
        self.assertEquals(next(c), 6)
        self.assertEquals(c.send(4), 5)
        self.assertEquals(c.send(20), 21)
        self.typeCheckFails(c.send, 32)

    def testGeneratorWithSendOk(self):
        @tc.typecheck
        def coroutine(start: int) -> tc.Type(int) & ~tc.Value(33):
            seed = start
            while seed != 10:
                seed = yield (seed + 1)
        self.assert_(isinstance(coroutine, types.FunctionType),
            'coroutine is not a function, it is: %s' % repr(coroutine))
        c = coroutine(5)
        self.assert_(isinstance(c, types.GeneratorType),
            'coroutine(5) is not a generator, it is: %s' % repr(c))
        self.assertEquals(next(c), 6)
        self.assertEquals(c.send(4), 5)
        self.assertEquals(c.send(20), 21)
        self.assertRaises(StopIteration, c.send, 10)

class _TestOrdering:
    class T1: pass
    class T11(T1): pass
class TTestOrdering(BaseTestCase):
    '''
    Test the ordering between different checkers
    '''
    def _checkLess(self, a, b):
        # check assertion
        self.assert_(a < b,
            '%s not lesser than %s as expected' % (a, b))
        # check coherence with other assertions
        self.assert_(a <= b,
            '%s < %s, but it is not true that a<=b' % (a,b))
        self.assertFalse(a >= b,
            '%s < %s, but it is not false that a>=b' % (a,b))
    def _checkLessOrEqual(self, a, b):
        # check assertion
        self.assert_(a <= b,
            '%s not lesser or equal than %s as expected' % (a, b))
        # check coherence with other assertions
        self.assert_(a < b or a == b,
            '%s <= %s, but it is not true that a<b or a==b' % (a,b))
        self.assertFalse(a > b,
            '%s <= %s, but it is not false that a>b' % (a,b))
    def _checkEqual(self, a, b):
        # check assertion
        self.assert_(a == b,
            '%s not equal to %s as expected' % (a, b))
        # check coherence with other assertions
        self.assert_(a <= b,
            '%s == %s, but it is not true that a<=b' % (a,b))
        self.assertFalse(a < b,
            '%s == %s, but it is not false that a<b' % (a,b))
        self.assert_(a >= b,
            '%s == %s, but it is not true that a>=b' % (a,b))
        self.assertFalse(a > b,
            '%s == %s, but it is not false that a>b' % (a,b))
    def _checkIncomparable(self, a, b):
        # check assertion
        self.assertFalse(a == b,
            '%s not different to %s as expected' % (a, b))
        self.assertFalse(a <= b,
            '%s not incomparable to %s as expected (a<=b)' % (a,b))
        self.assertFalse(a < b,
            '%s not incomparable to %s as expected (a<b)' % (a,b))
        self.assertFalse(a >= b,
            '%s not incomparable to %s as expected (a>=b)' % (a,b))
        self.assertFalse(a > b,
            '%s not incomparable to %s as expected (a>b)' % (a,b))
        # check coherence with other assertions
        self.assert_(a != b,
            '%s==%s is false, but it is not true that a!=b' % (a, b))
    def testAnyWithAny(self):
        self._checkEqual(tc.Any, tc.Any)
    def testTypeWithType(self):
        self._checkEqual(tc.Type(int), tc.Type(int))
        self._checkIncomparable(tc.Type(int), tc.Type(str))
        self._checkLess(tc.Type(_TestOrdering.T11), tc.Type(_TestOrdering.T1))
    def testAttrsWithAttrs(self):
        self._checkEqual(tc.Attrs('a', 'b'), tc.Attrs('a', 'b'))
        self._checkLess(tc.Attrs('a', 'b', 'c'), tc.Attrs('a', 'b'))
    def testValueWithValue(self):
        self._checkEqual(tc.Value(3), tc.Value(3))
        self._checkIncomparable(tc.Value(3), tc.Value(4))
    def testCriteriaWithCriteria(self):
        def even(x): return x%2==0
        def odd(x): return x%2!=0
        self._checkEqual(tc.Criteria(even), tc.Criteria(even))
        self._checkIncomparable(tc.Criteria(even), tc.Criteria(odd))
    def testAnd(self):
        t1 = tc.Type(int)
        t2 = tc.Type(_TestOrdering.T11)
        t3 = tc.Type(_TestOrdering.T1)
        t4 = tc.Type(float)
        self._checkEqual(tc.And(t1, t2), tc.And(t1, t2))
        self._checkEqual(tc.And(t1, t2, t3), tc.And(t1, t2))
        self._checkLess(tc.And(t1, t2), t1)
        self._checkLess(tc.And(t1, t2), tc.And(t1, t3))
        self._checkIncomparable(tc.And(t2, t3), tc.And(t1, t3))
        self._checkIncomparable(tc.And(t2, t4), tc.And(t1, t3))
        self._checkIncomparable(tc.And(t2, t3, t4), tc.And(t1, t3))
        self._checkIncomparable(tc.And(t2, t4), tc.And(t1, t3, t4))
    def testOr(self):
        t1 = tc.Type(int)
        t2 = tc.Type(_TestOrdering.T11)
        t3 = tc.Type(_TestOrdering.T1)
        t4 = tc.Type(float)
        self._checkEqual(tc.Or(t1, t2), tc.Or(t1, t2))
        self._checkEqual(tc.Or(t1, t2, t3), tc.Or(t1, t3))
        self._checkLess(t1, tc.Or(t1, t2))
        self._checkLess(tc.Or(t1, t3), tc.Or(t1, t2))
        self._checkIncomparable(tc.Or(t2, t3), tc.Or(t1, t3))
        self._checkIncomparable(tc.Or(t2, t4), tc.Or(t1, t3))
        self._checkIncomparable(tc.Or(t2, t3, t4), tc.Or(t1, t3))
        self._checkIncomparable(tc.Or(t2, t4), tc.Or(t1, t3, t4))

def runAllTests():
    tl = unittest.TestLoader()
    suite = unittest.TestSuite(map(tl.loadTestsFromTestCase,
        [value
        for name, value
        in globals().items()
        if name.startswith('Test') and issubclass(value, unittest.TestCase)]
        ))
    unittest.TextTestRunner(verbosity=2).run(suite)
