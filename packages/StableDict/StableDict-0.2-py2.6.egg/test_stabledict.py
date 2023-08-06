#!/usr/bin/env python
# test_stabledict.py,v 1.11 2007/08/28 08:31:41 martin Exp
# This file is under the Python licence.
#
# This file was originally "test_dict.py" from the Python 2.5.1
# distribution.  I tweaked it to test the "StableDict" class derived
# from the builtin class "dict" instead. This basically meant
# replacing "dict" with "StableDict" and "{}" (empty dict literal)
# with the constructor call "StableDict()".
#
# NOTES:
#       Python before 2.5.1     "test_tuple_keyerror" will FAIL!
#       Python before 2.5       "test_missing" will give an ERROR!
#       Python before 2.3       "test_fromkeys" and "test_pop" will have ERROR!
#       Python before 2.2       will not compile (lacking generators etc.)

from __future__ import generators
import random, unittest, warnings
from test import test_support
from stabledict import StableDict, _WRNnoOrderArg, _WRNnoOrderKW

import sys, UserDict, cStringIO

# constants for Errors
_EsizeChanged = "changing StableDict size during iteration doesn't raise Error"
_EmayLoopForever = "StableDict iterator affected by mutations during iteration"

# XXX We want to skip tests known to fail. Ideally should be a no-op
# on anything but CPython. Unfortunately I don't know any _simple_
# test for the Python implementation; there is nothing like
# sys.implementation. We try to guess here:
runningCPython = False
try:
    import os
    if os.name in ( 'posix', 'nt', 'mac', 'os2', 'ce', 'riscos' ):
        runningCPython = True
except:
    pass

def needsCPython(*version):
    """Raise TestSkipped error when Python is older than version.

    Used to skip tests known to fail on older CPython versions."""
    if not runningCPython:
        return # continue with TestCase
    assert version
    if len(version) == 1 and isinstance(version[0], tuple):
        version = version[0]
    if sys.version_info < version:
        raise test_support.TestSkipped(
            "known to fail on CPython < %r" % (version,))


class DictTest(unittest.TestCase):
    def test_constructor(self):
        # calling built-in types without argument must return empty
        self.assertEqual(StableDict(), StableDict())
        self.assert_(StableDict() is not StableDict())

    def test_bool(self):
        self.assert_(not StableDict())
        self.assert_({1: 2})
        self.assert_(bool(StableDict()) is False)
        self.assert_(bool({1: 2}) is True)

    def test_keys(self):
        d = StableDict()
        self.assertEqual(d.keys(), [])
        d = {'a': 1, 'b': 2}
        k = d.keys()
        self.assert_(d.has_key('a'))
        self.assert_(d.has_key('b'))

        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = StableDict()
        self.assertEqual(d.values(), [])
        d = {1:2}
        self.assertEqual(d.values(), [2])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = StableDict()
        self.assertEqual(d.items(), [])

        d = {1:2}
        self.assertEqual(d.items(), [(1, 2)])

        self.assertRaises(TypeError, d.items, None)

    def test_has_key(self):
        d = StableDict()
        self.assert_(not d.has_key('a'))
        d = {'a': 1, 'b': 2}
        k = d.keys()
        k.sort()
        self.assertEqual(k, ['a', 'b'])

        self.assertRaises(TypeError, d.has_key)

    def test_contains(self):
        d = StableDict()
        self.assert_(not ('a' in d))
        self.assert_('a' not in d)
        d = {'a': 1, 'b': 2}
        self.assert_('a' in d)
        self.assert_('b' in d)
        self.assert_('c' not in d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        d = StableDict()
        self.assertEqual(len(d), 0)
        d = {'a': 1, 'b': 2}
        self.assertEqual(len(d), 2)

    def test_getitem(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        del d['b']
        self.assertEqual(d, {'a': 4, 'c': 3})

        self.assertRaises(TypeError, d.__getitem__)

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()

        d = StableDict()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = StableDict()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    def test_clear(self):
        d = {1:1, 2:2, 3:3}
        d.clear()
        self.assertEqual(d, StableDict())

        self.assertRaises(TypeError, d.clear, None)

    def test_update(self):
        d = StableDict()
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})

        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})

        self.assertRaises((TypeError, AttributeError), d.update, None)

        class SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, {1:1, 2:2, 3:3})

        class Exc(Exception): pass

        d.clear()
        class FailingUserDict:
            def keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        class badseq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        self.assertRaises(Exc, StableDict().update, badseq())

        self.assertRaises(ValueError, StableDict().update, [(1, 2, 3)])

    def test_fromkeys(self):
        needsCPython(2,3)
        self.assertEqual(StableDict.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = StableDict()
        self.assert_(not(d.fromkeys('abc') is d))
        self.assertEqual(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), StableDict())
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), {1:None})
        self.assertRaises(TypeError, StableDict().fromkeys, 3)
        class dictlike(StableDict): pass
        self.assertEqual(dictlike.fromkeys('a'), {'a':None})
        self.assertEqual(dictlike().fromkeys('a'), {'a':None})
        self.assert_(type(dictlike.fromkeys('a')) is dictlike)
        self.assert_(type(dictlike().fromkeys('a')) is dictlike)
        class mydict(StableDict):
            def __new__(cls):
                return UserDict.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assert_(isinstance(ud, UserDict.UserDict))
        self.assertRaises(TypeError, StableDict.fromkeys)

        class Exc(Exception): pass

        class baddict1(StableDict):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        self.assertRaises(Exc, StableDict.fromkeys, BadSeq())

        class baddict2(StableDict):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

    def test_copy(self):
        d = {1:1, 2:2, 3:3}
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        self.assertEqual(StableDict().copy(), StableDict())
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        d = StableDict()
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = {'a' : 1, 'b' : 2}
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    def test_setdefault(self):
        # StableDict.setdefault()
        d = StableDict()
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
        self.assertRaises(TypeError, d.setdefault)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])

    def test_popitem(self):
        # StableDict.popitem()
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(10):
                size = 2**log2size
                a = StableDict()
                b = StableDict()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assert_(not(copymode < 0 and ta != tb))
                self.assert_(not a)
                self.assert_(not b)

        d = StableDict()
        self.assertRaises(KeyError, d.popitem)

    def test_pop(self):
        needsCPython(2,3)
        # Tests for pop with specified key
        d = StableDict()
        k, v = 'abc', 'def'
        d[k] = v
        self.assertRaises(KeyError, d.pop, 'ghi')

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        # verify longs/ints get same value when key > 32 bits (for 64-bit archs)
        # see SF bug #689659
        x = 4503599627370496L
        y = 4503599627370496
        h = {x: 'anything', y: 'something else'}
        self.assertEqual(h[x], h[y])

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        self.assertRaises(TypeError, d.pop)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        d = StableDict()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
                assert len(d) < 10, _EmayLoopForever
        except RuntimeError:
            pass
        else:
            self.fail(_EsizeChanged)

    def test_repr(self):
        d = StableDict()
        self.assertEqual(repr(d), 'StableDict([])')
        d[1] = 2
        self.assertEqual(repr(d), 'StableDict([(1, 2)])')
        d = StableDict()
        d[1] = d
        self.assertEqual(repr(d), 'StableDict([(1, StableDict({...}))])')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = {1: BadRepr()}
        self.assertRaises(Exc, repr, d)

    def test_str(self):
        d = StableDict()
        self.assertEqual(str(d), 'StableDict({})')
        d[1] = 2
        self.assertEqual(str(d), 'StableDict({1: 2})')
        d = StableDict()
        d[1] = d
        self.assertEqual(str(d), 'StableDict({1: StableDict({...})})')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = {1: BadRepr()}
        self.assertRaises(Exc, str, d)

    def test_le(self):
        self.assert_(not (StableDict() < StableDict()))
        self.assert_(not ({1: 2} < {1L: 2L}))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()

        d1 = {BadCmp(): 1}
        d2 = {1: 1}
        try:
            d1 < d2
        except Exc:
            pass
        else:
            self.fail("< didn't raise Exc")

    def test_missing(self):
        needsCPython(2,5)
        # Make sure StableDict doesn't have a __missing__ method
        self.assertEqual(hasattr(StableDict, "__missing__"), False)
        self.assertEqual(hasattr(StableDict(), "__missing__"), False)
        # Test several cases:
        # (D) subclass defines __missing__ method returning a value
        # (E) subclass defines __missing__ method raising RuntimeError
        # (F) subclass sets __missing__ instance variable (no effect)
        # (G) subclass doesn't define __missing__ at a all
        class D(StableDict):
            def __missing__(self, key):
                return 42
        d = D({1: 2, 3: 4})
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assert_(2 not in d)
        self.assert_(2 not in d.keys())
        self.assertEqual(d[2], 42)
        class E(StableDict):
            def __missing__(self, key):
                raise RuntimeError(key)
        e = E()
        try:
            e[42]
        except RuntimeError, err:
            self.assertEqual(err.args, (42,))
        else:
            self.fail("e[42] didn't raise RuntimeError")
        class F(StableDict):
            def __init__(self):
                # An instance variable __missing__ should have no effect
                self.__missing__ = lambda key: None
        f = F()
        try:
            f[42]
        except KeyError, err:
            self.assertEqual(err.args, (42,))
        else:
            self.fail("f[42] didn't raise KeyError")
        class G(StableDict):
            pass
        g = G()
        try:
            g[42]
        except KeyError, err:
            self.assertEqual(err.args, (42,))
        else:
            self.fail("g[42] didn't raise KeyError")

    def test_tuple_keyerror(self):
        # SF #1576657
        needsCPython(2,5,1)
        d = StableDict()
        try:
            d[(1,)]
        except KeyError, e:
            self.assertEqual(e.args, ((1,),))
        else:
            self.fail("missing KeyError")


class StableDictTest(unittest.TestCase):
    """Test key sequence stability"""

    def test_stability(self):
        # __iter__ must preserve key insertion order
        for log2size in range(9):
            size = 2**log2size
            d = StableDict()
            keys = range(size)
            random.shuffle(keys)
            for k in keys:
                d[k] = -k
            self.assertEqual(keys, d.keys())                    # keys
            self.assertEqual(keys, [ k for k in d ])            # iter
            self.assertEqual(keys, [ k for k in d.iterkeys() ]) # iterkeys
            self.assertEqual(keys, [ -k for k in d.values() ])  # values
            self.assertEqual(keys, [ -k for k in d.itervalues() ]) # itervalues
            items = [ (k, -k) for k in keys ]
            self.assertEqual(items, d.items())                  # items
            self.assertEqual(items, [ i for i in d.iteritems() ]) # iteritems

            d2 = d.copy()
            self.assertEqual(keys, d2.keys())
            d.clear()
            self.assertEqual(keys, d2.keys())
            self.assertEqual([], d.keys())
            d.update(d2)
            self.assertEqual(keys, d.keys())
            morekeys = range(size, 2*size)
            random.shuffle(morekeys)
            for k in morekeys:
                d2[k] = -k
            d.update(d2)
            self.assertEqual(keys+morekeys, d.keys())

    def test_mutating_while_itervalues(self):
        d = StableDict()
        d[1] = 1
        try:
            for i in d.itervalues():
                d[i+1] = i+1
                assert len(d) < 10, _EmayLoopForever
        except RuntimeError:
            pass
        else:
            self.fail(_EsizeChanged)

    def test_mutating_while_iteritems(self):
        d = StableDict()
        d[1] = 1
        try:
            for i in d.iteritems():
                d[i[0]+1] = i[0]+1
                assert len(d) < 10, _EmayLoopForever
        except RuntimeError:
            pass
        else:
            self.fail(_EsizeChanged)


testClasses = [ DictTest, StableDictTest ]

try:
    from test import mapping_tests

    class GeneralMappingTests(mapping_tests.BasicTestMappingProtocol):
        type2test = StableDict

    class Dict(StableDict):
        pass

    class SubclassMappingTests(mapping_tests.BasicTestMappingProtocol):
        type2test = Dict

    testClasses += (GeneralMappingTests, SubclassMappingTests)
except:
    pass

def getTestSuite():
    """Return this module's test-suite."""
    # do not let expected warnings clutter testrun output
    warnings.filterwarnings("ignore", _WRNnoOrderArg)
    warnings.filterwarnings("ignore", _WRNnoOrderKW)
    return unittest.TestSuite(map(unittest.makeSuite, testClasses))

def test_main():
    """Run this module's test-suite."""
    test_support.run_suite(getTestSuite())

if __name__ == "__main__":
    test_main()

#EOF#
