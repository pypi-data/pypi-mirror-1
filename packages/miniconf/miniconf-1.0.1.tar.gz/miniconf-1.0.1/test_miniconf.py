#!/usr/bin/env python

from test import test_support
import miniconf
import unittest
import sys

class LoadTestCase(unittest.TestCase):
    # Test loading

    src_unloadable = 'while 1: pass # The loop of death'
    
    def test_empty(self):
        # Test empty load
        data = miniconf.load('')
        self.assertEqual(data, {})
    
    def test_comment_trimming(self):
        # Test empty load
        data = miniconf.load('# Nothing to see there, move along')
        self.assertEqual(data, {})

    def test_spurious_source(self):
        # Test a source with syntax error
        self.assertRaises(SyntaxError, miniconf.load, 'arrg!')
        
    def test_unloadable_structure(self):
        # Test on unloadable object
        data = miniconf.load(self.src_unloadable)
        self.assertEqual(data, {})

    def test_unloadable_structure_pedantic(self):
        # Test on unloadable object, pedantic mode
        self.assertRaises(TypeError, miniconf.load,
                          self.src_unloadable, pedantic = True)

    def test_trivial_load(self):
        # Try to load a trivial value
        data = miniconf.load('spam = 1')
        self.assertEqual(data, {'spam': 1})

    def test_all_around_flat_load(self):
        # Test the load a single value of each supported type
        for value in (dict(), list(), tuple(),
                      int(), float(), str(), unicode(), bool(), None):
            data = miniconf.load('spam = %s' % repr(value))
            self.assertEqual(data['spam'], value)

    def test_recursive_load(self):
        # Test the load of an arbitrary, nested structure
        val = [0, {1: [2, (3, 4)]}]
        data = miniconf.load('spam = %s' % repr(val))
        self.assertEqual(data['spam'], val)
        
class DumpTestCase(unittest.TestCase):
    # Test dumping()

    class MyInt(int): pass
    
    def test_empty(self):
        # Test an empty dump
        out = miniconf.dump({})
        self.assertEqual(out, '')

    def test_invalid_data(self):
        # Test on a non-dictionary data
        self.assertRaises(TypeError, miniconf.dump, None)

    def test_subclass_dump_pedantic(self):
        # Test a subclass dump, in pedantic mode
        self.assertRaises(TypeError, miniconf.dump,
                          {'spam' : self.MyInt(1)})

    def test_subclass_dump_non_pedantic(self):
        # Test a subclass dump, in non-pedantic mode
        out = miniconf.dump({'spam' : self.MyInt(1)}, pedantic=False)
        self.assertEqual(out, 'spam = 1')

    def test_invalid_identifier(self):
        # Test passing an invalid Python identifier
        self.assertRaises(ValueError, miniconf.dump,
                          {'?invalid_id' : None })

    def test_comment(self):
        # Test generation of a single comment
        out = miniconf.dump({}, comments = {'--top--': 'Egg'})
        self.assertEqual(out, '# Egg')

    def test_invalid_comment(self):
        # Test rejection of an invalid comment
        self.assertRaises(TypeError, miniconf.dump,
                          {}, comments = {'--top--': None})

    def test_all_around_flat_dump(self):
        # Test the dump a single value of each supported type
        for value in (dict(), list(), tuple(),
                      int(), float(), str(), unicode(), bool(), None):
            out = miniconf.dump({'spam': value})
            self.assertEqual(out, 'spam = %s' % repr(value))

    def test_recursive_dump(self):
        # Test the dump of an arbitrary, nested structure 
        val = [0, {1: [2, (3, 4)]}]
        out = miniconf.dump({ 'spam': val})
        self.assertEqual(out, 'spam = %s' % repr(val))

class ValuesTestCase(unittest.TestCase):
    # Test dump(load(val)) more extensively (some ideas and code borrowed from
    # test_marshal.py)
    
    def test_ints(self):
        # Test the full range of Python ints 
        n = sys.maxint
        while n:
            for expected in (-n, n):
                s = miniconf.dump({'spam' : expected})
                got = miniconf.load(s)['spam']
                self.assertEqual(expected, got)
            n = n >> 1

    def test_bool_and_none(self):
        # Test booleans and None
        for expected in (True, False, None):
            s = miniconf.dump({'spam': expected})
            got = miniconf.load(s)['spam']
            self.assertEqual(expected, got)

    def test_float(self):
        # Test a few floats
        small = 1e-25
        n = sys.maxint * 3.7e250
        while n > small:
            for expected in (-n, n):
                f = float(expected)
                s = miniconf.dump({'spam': f})
                got = miniconf.load(s)['spam']
                self.assertEqual(f, got)
            n /= 123.4567

        n = sys.maxint * 3.7e-250
        while n < small:
            for expected in (-n, n):
                f = float(expected)

                s = miniconf.dump({'spam': f})
                got = miniconf.load(s)['spam']
            n *= 123.4567

    def test_string(self):
        # Test some random plain and unicode strings
        for expected in [ "", 'Test \xcb', '-' * 400 ]:
            s = miniconf.dump({'spam': expected})
            got = miniconf.load(s)['spam']
            self.assertEqual(expected, got)

    def test_unicode(self):
         # Test some random plain and unicode strings
        for expected in [ u"", u'Test \xcb', u'-' * 400 ]:
            s = miniconf.dump({'spam': expected})
            got = miniconf.load(s)['spam']
            self.assertEqual(expected, got)

class StressTestCase(unittest.TestCase):
    def test_stress(self):
        # Test if we can sucessfully dump, then reload a collection of
        # relatively complex nested objects composed of every
        # supported types.
        
        def create(rank = 0, it = 1):
            # This is the object creation function: return a data
            # dictionary suitable to be fed to dump().
            def ident(iterable):
                for k, v in enumerate(iterable):
                    yield 'spam_%d' % k, v
        
            types = (dict, list, tuple, int, float, str, unicode, bool)

            if rank < 30:
                for i in xrange(it):
                    t = types[(rank + i)% len(types)]
                    if t in types[:3]:
                        size = (rank % 5) + 5
                        if t is dict:
                            var = t(ident(create(rank + i + 1, size)))
                        else:
                            var = t(create(rank + i + 1, size))
                        yield var
                    else:
                        yield t(rank + i)
            else:
                yield None

        expected = list(create())[0]
        s = miniconf.dump(expected)
        got = miniconf.load(s)
        self.assertEqual(got, expected)

def test_main():
    test_support.run_unittest(LoadTestCase,
                              DumpTestCase,
                              ValuesTestCase,
                              StressTestCase)

if __name__ == "__main__":
    test_main()
