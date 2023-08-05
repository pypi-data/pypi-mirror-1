"""unittest module for logilab.comon.testlib"""

__revision__ = '$Id: unittest_testlib.py,v 1.5 2006-02-09 22:37:46 nico Exp $'

import unittest
import os
import sys
from os.path import join, dirname, isdir, isfile, abspath
from cStringIO import StringIO
import tempfile
import shutil

from logilab.common.compat import sorted

try:
    __file__
except NameError:
    __file__ = sys.argv[0]
    
from logilab.common.testlib import TestCase, TestSuite, SkipAwareTextTestRunner
from logilab.common.testlib import mock_object, NonStrictTestLoader, create_files
from logilab.common.testlib import capture_stdout, unittest_main, InnerTest

class MockTestCase(TestCase):
    def __init__(self):
        # Do not call unittest.TestCase's __init__
        pass

    def fail(self, msg):
        raise AssertionError(msg)

class UtilTC(TestCase):

    def test_mockobject(self):
        obj = mock_object(foo='bar', baz='bam')
        self.assertEquals(obj.foo, 'bar')
        self.assertEquals(obj.baz, 'bam')


    def test_create_files(self):
        chroot = tempfile.mkdtemp()
        path_to = lambda path: join(chroot, path)
        dircontent = lambda path: sorted(os.listdir(join(chroot, path)))
        try:
            self.failIf(isdir(path_to('a/')))
            create_files(['a/b/foo.py', 'a/b/c/', 'a/b/c/d/e.py'], chroot)
            # make sure directories exist
            self.failUnless(isdir(path_to('a')))
            self.failUnless(isdir(path_to('a/b')))
            self.failUnless(isdir(path_to('a/b/c')))
            self.failUnless(isdir(path_to('a/b/c/d')))
            # make sure files exist
            self.failUnless(isfile(path_to('a/b/foo.py')))
            self.failUnless(isfile(path_to('a/b/c/d/e.py')))
            # make sure only asked files were created
            self.assertEquals(dircontent('a'), ['b'])
            self.assertEquals(dircontent('a/b'), ['c', 'foo.py'])
            self.assertEquals(dircontent('a/b/c'), ['d'])
            self.assertEquals(dircontent('a/b/c/d'), ['e.py'])
        finally:
            shutil.rmtree(chroot)
            

class TestlibTC(TestCase):

    capture = True
    
    def setUp(self):
        self.tc = MockTestCase()

    def test_dict_equals(self):
        """tests TestCase.assertDictEquals"""
        d1 = {'a' : 1, 'b' : 2}
        d2 = {'a' : 1, 'b' : 3}
        d3 = dict(d1)
        self.assertRaises(AssertionError, self.tc.assertDictEquals, d1, d2)
        self.tc.assertDictEquals(d1, d3)
        self.tc.assertDictEquals(d3, d1)
        self.tc.assertDictEquals(d1, d1)

    def test_list_equals(self):
        """tests TestCase.assertListEquals"""
        l1 = range(10)
        l2 = range(5)
        l3 = range(10)
        self.assertRaises(AssertionError, self.tc.assertListEquals, l1, l2)
        self.tc.assertListEquals(l1, l1)
        self.tc.assertListEquals(l1, l3)
        self.tc.assertListEquals(l3, l1)

    def test_lines_equals(self):
        """tests assertLineEquals"""
        t1 = """some
        text
"""
        t2 = """some
        
        text"""
        t3 = """some
        text"""
        self.assertRaises(AssertionError, self.tc.assertLinesEquals, t1, t2)
        self.tc.assertLinesEquals(t1, t3)
        self.tc.assertLinesEquals(t3, t1)
        self.tc.assertLinesEquals(t1, t1)

    def test_xml_valid(self):
        """tests xml is valid"""
        valid = """<root>
        <hello />
        <world>Logilab</world>
        </root>"""
        invalid = """<root><h2> </root>"""
        self.tc.assertXMLStringWellFormed(valid)
        self.assertRaises(AssertionError, self.tc.assertXMLStringWellFormed, invalid)
        invalid = """<root><h2 </h2> </root>"""
        self.assertRaises(AssertionError, self.tc.assertXMLStringWellFormed, invalid)


    def test_set_equality_for_lists(self):
        l1 = [0, 1, 2]
        l2 = [1, 2, 3]
        self.assertRaises(AssertionError, self.tc.assertSetEqual, l1, l2)
        self.tc.assertSetEqual(l1, l1)
        self.tc.assertSetEqual([], [])
        l1 = [0, 1, 1]
        l2 = [0, 1]
        self.assertRaises(AssertionError, self.tc.assertSetEqual, l1, l2)
        self.tc.assertSetEqual(l1, l1)


    def test_set_equality_for_dicts(self):
        d1 = {'a' : 1, 'b' : 2}
        d2 = {'a' : 1}
        self.assertRaises(AssertionError, self.tc.assertSetEqual, d1, d2)
        self.tc.assertSetEqual(d1, d1)
        self.tc.assertSetEqual({}, {})

    def test_set_equality_for_iterables(self):
        self.assertRaises(AssertionError, self.tc.assertSetEqual, xrange(5), xrange(6))
        self.tc.assertSetEqual(xrange(5), range(5))
        self.tc.assertSetEqual([], ())

    def test_file_equality(self):
        foo = join(dirname(__file__), 'data', 'foo.txt')
        spam = join(dirname(__file__), 'data', 'spam.txt')        
        self.assertRaises(AssertionError, self.tc.assertFileEqual, foo, spam)
        self.tc.assertFileEqual(foo, foo)

    def test_stream_equality(self):
        foo = join(dirname(__file__), 'data', 'foo.txt')
        spam = join(dirname(__file__), 'data', 'spam.txt')        
        stream1 = file(foo)
        self.tc.assertStreamEqual(stream1, stream1)
        stream1 = file(foo)
        stream2 = file(spam)
        self.assertRaises(AssertionError, self.tc.assertStreamEqual, stream1, stream2)
        
    def test_text_equality(self):
        foo = join(dirname(__file__), 'data', 'foo.txt')
        spam = join(dirname(__file__), 'data', 'spam.txt')        
        text1 = file(foo).read()
        self.tc.assertTextEqual(text1, text1)
        text2 = file(spam).read()
        self.assertRaises(AssertionError, self.tc.assertTextEqual, text1, text2)


    def test_assert_raises(self):
        exc = self.tc.assertRaises(KeyError, {}.__getitem__, 'foo')
        self.failUnless(isinstance(exc, KeyError))
        self.assertEquals(exc.args, ('foo',))
        

    def test_default_datadir(self):
        expected_datadir = join(dirname(abspath(__file__)), 'data')
        self.assertEquals(self.datadir, expected_datadir)
        self.assertEquals(self.datapath('foo'), join(expected_datadir, 'foo'))

    def test_custom_datadir(self):
        class MyTC(TestCase):
            datadir = 'foo'
            def test_1(self): pass

        # class' custom datadir
        tc = MyTC('test_1')
        self.assertEquals(tc.datapath('bar'), join('foo', 'bar'))
        # instance's custom datadir
        tc.datadir = 'spam'
        self.assertEquals(tc.datapath('bar'), join('spam', 'bar'))        


    def test_cached_datadir(self):
        """test datadir is cached on the class"""
        class MyTC(TestCase):
            def test_1(self): pass
                
        expected_datadir = join(dirname(abspath(__file__)), 'data')
        tc = MyTC('test_1')
        self.assertEquals(tc.datadir, expected_datadir)
        # changing module should not change the datadir
        MyTC.__module__ = 'os'
        self.assertEquals(tc.datadir, expected_datadir)
        # even on new instances
        tc2 = MyTC('test_1')
        self.assertEquals(tc2.datadir, expected_datadir)
        


class GenerativeTestsTC(TestCase):
    
    def setUp(self):
        output = StringIO()
        self.runner = SkipAwareTextTestRunner(stream=output)

    def test_generative_ok(self):
        class FooTC(TestCase):
            def test_generative(self):
                for i in xrange(10):
                    yield self.assertEquals, i, i
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 10)
        self.assertEquals(len(result.failures), 0)
        self.assertEquals(len(result.errors), 0)


    def test_generative_half_bad(self):
        class FooTC(TestCase):
            def test_generative(self):
                for i in xrange(10):
                    yield self.assertEquals, i%2, 0
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 10)
        self.assertEquals(len(result.failures), 5)
        self.assertEquals(len(result.errors), 0)


    def test_generative_error(self):
        class FooTC(TestCase):
            def test_generative(self):
                for i in xrange(10):
                    if i == 5:
                        raise ValueError('STOP !')
                    yield self.assertEquals, i, i
                    
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 5)
        self.assertEquals(len(result.failures), 0)
        self.assertEquals(len(result.errors), 1)


    def test_generative_error2(self):
        class FooTC(TestCase):
            def test_generative(self):
                for i in xrange(10):
                    if i == 5:
                        yield self.ouch
                    yield self.assertEquals, i, i
            def ouch(self): raise ValueError('stop !')
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 6)
        self.assertEquals(len(result.failures), 0)
        self.assertEquals(len(result.errors), 1)


    def test_generative_setup(self):
        class FooTC(TestCase):
            def setUp(self):
                raise ValueError('STOP !')
            def test_generative(self):
                for i in xrange(10):
                    yield self.assertEquals, i, i
                    
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 1)
        self.assertEquals(len(result.failures), 0)
        self.assertEquals(len(result.errors), 1)


class ExitFirstTC(TestCase):
    def setUp(self):
        output = StringIO()
        self.runner = SkipAwareTextTestRunner(stream=output, exitfirst=True)

    def test_failure_exit_first(self):
        class FooTC(TestCase):
            def test_1(self): pass
            def test_2(self): assert False
            def test_3(self): pass
        tests = [FooTC('test_1'), FooTC('test_2')]
        result = self.runner.run(TestSuite(tests))
        self.assertEquals(result.testsRun, 2)
        self.assertEquals(len(result.failures), 1)
        self.assertEquals(len(result.errors), 0)
        

    def test_error_exit_first(self):
        class FooTC(TestCase):
            def test_1(self): pass
            def test_2(self): raise ValueError()
            def test_3(self): pass
        tests = [FooTC('test_1'), FooTC('test_2'), FooTC('test_3')]
        result = self.runner.run(TestSuite(tests))
        self.assertEquals(result.testsRun, 2)
        self.assertEquals(len(result.failures), 0)
        self.assertEquals(len(result.errors), 1)
        
    def test_generative_exit_first(self):
        class FooTC(TestCase):
            def test_generative(self):
                for i in xrange(10):
                    yield self.assert_, False
        result = self.runner.run(FooTC('test_generative'))
        self.assertEquals(result.testsRun, 1)
        self.assertEquals(len(result.failures), 1)
        self.assertEquals(len(result.errors), 0)


class TestLoaderTC(TestCase):
    ## internal classes for test purposes ########
    class FooTC(TestCase):
        def test_foo1(self): pass
        def test_foo2(self): pass
        def test_bar1(self): pass

    class BarTC(TestCase):
        def test_bar2(self): pass
    ##############################################

    def setUp(self):
        self.loader = NonStrictTestLoader()
        self.module = TestLoaderTC # mock_object(FooTC=TestLoaderTC.FooTC, BarTC=TestLoaderTC.BarTC)
        self.output = StringIO()
        self.runner = SkipAwareTextTestRunner(stream=self.output)
    
    def assertRunCount(self, pattern, module, expected_count, skipped=()):
        if pattern:
            suite = self.loader.loadTestsFromNames([pattern], module)
        else:
            suite = self.loader.loadTestsFromModule(module)
        self.runner.test_pattern = pattern
        self.runner.skipped_patterns = skipped
        result = self.runner.run(suite)
        self.runner.test_pattern = None
        self.runner.skipped_patterns = ()
        self.assertEquals(result.testsRun, expected_count)
        
    def test_collect_everything(self):
        """make sure we don't change the default behaviour
        for loadTestsFromModule() and loadTestsFromTestCase
        """
        testsuite = self.loader.loadTestsFromModule(self.module)
        self.assertEquals(len(testsuite._tests), 2)
        suite1, suite2 = testsuite._tests
        self.assertEquals(len(suite1._tests) + len(suite2._tests), 4)

    def test_collect_with_classname(self):
        self.assertRunCount('FooTC', self.module, 3)
        self.assertRunCount('BarTC', self.module, 1)

    def test_collect_with_classname_and_pattern(self):
        data = [('FooTC.test_foo1', 1), ('FooTC.test_foo', 2), ('FooTC.test_fo', 2),
                ('FooTC.foo1', 1), ('FooTC.foo', 2), ('FooTC.whatever', 0)
                ]
        for pattern, expected_count in data:
            yield self.assertRunCount, pattern, self.module, expected_count
        
    def test_collect_with_pattern(self):
        data = [('test_foo1', 1), ('test_foo', 2), ('test_bar', 2),
                ('foo1', 1), ('foo', 2), ('bar', 2), ('ba', 2),
                ('test', 4), ('ab', 0),
                ]
        for pattern, expected_count in data:
            yield self.assertRunCount, pattern, self.module, expected_count

    def test_tescase_with_custom_metaclass(self):
        class mymetaclass(type): pass
        class MyMod:
            class MyTestCase(TestCase):
                __metaclass__ = mymetaclass
                def test_foo1(self): pass
                def test_foo2(self): pass
                def test_bar(self): pass
        data = [('test_foo1', 1), ('test_foo', 2), ('test_bar', 1),
                ('foo1', 1), ('foo', 2), ('bar', 1), ('ba', 1),
                ('test', 3), ('ab', 0),
                ('MyTestCase.test_foo1', 1), ('MyTestCase.test_foo', 2),
                ('MyTestCase.test_fo', 2), ('MyTestCase.foo1', 1),
                ('MyTestCase.foo', 2), ('MyTestCase.whatever', 0)
                ]
        for pattern, expected_count in data:
            yield self.assertRunCount, pattern, MyMod, expected_count
            
        
    def test_collect_everything_and_skipped_patterns(self):
        testdata = [ (['foo1'], 3), (['foo'], 2),
                     (['foo', 'bar'], 0),
                     ]
        for skipped, expected_count in testdata:
            yield self.assertRunCount, None, self.module, expected_count, skipped
        

    def test_collect_specific_pattern_and_skip_some(self):
        testdata = [ ('bar', ['foo1'], 2), ('bar', [], 2),
                     ('bar', ['bar'], 0), ]
        
        for runpattern, skipped, expected_count in testdata:
            yield self.assertRunCount, runpattern, self.module, expected_count, skipped

    def test_skip_classname(self):
        testdata = [ (['BarTC'], 3), (['FooTC'], 1), ]
        for skipped, expected_count in testdata:
            yield self.assertRunCount, None, self.module, expected_count, skipped

    def test_skip_classname_and_specific_collect(self):
        testdata = [ ('bar', ['BarTC'], 1), ('foo', ['FooTC'], 0), ]
        for runpattern, skipped, expected_count in testdata:
            yield self.assertRunCount, runpattern, self.module, expected_count, skipped


    def test_nonregr_dotted_path(self):
        self.assertRunCount('FooTC.test_foo', self.module, 2)


    def test_inner_tests_selection(self):
        class MyMod:
            class MyTestCase(TestCase):
                def test_foo(self): pass
                def test_foobar(self):
                    for i in xrange(5):
                        if i%2 == 0:
                            yield InnerTest('even', lambda: None)
                        else:
                            yield InnerTest('odd', lambda: None)
                    yield lambda: None
                    
        data = [('foo', 7), ('test_foobar', 6), ('even', 3), ('odd', 2),
                ]
        for pattern, expected_count in data:
            yield self.assertRunCount, pattern, MyMod, expected_count

    def tests_nonregr_class_skipped_option(self):
        class MyMod:
            class MyTestCase(TestCase):
                def test_foo(self): pass
                def test_bar(self): pass
            class FooTC(TestCase):
                def test_foo(self): pass
        self.assertRunCount('foo', MyMod, 2)
        self.assertRunCount(None, MyMod, 3)
        self.loader.skipped_patterns = self.runner.skipped_patterns = ['FooTC']
        self.assertRunCount('foo', MyMod, 1)
        self.assertRunCount(None, MyMod, 2)
    

def bootstrap_print(msg, output=sys.stdout):
    """sys.stdout will be evaluated at function parsing time"""
    # print msg
    output.write(msg)

class OutErrCaptureTC(TestCase):
    
    def setUp(self):
        sys.stdout = sys.stderr = StringIO()
        self.runner = SkipAwareTextTestRunner(stream=StringIO(), exitfirst=True, capture=True)

    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_stdout_capture(self):
        class FooTC(TestCase):
            def test_stdout(self):
                print "foo"
                self.assert_(False)
        test = FooTC('test_stdout')
        result = self.runner.run(test)
        captured_out, captured_err = test.captured_output()
        self.assertEqual(captured_out.strip(), "foo")
        self.assertEqual(captured_err.strip(), "") 
       
    def test_stderr_capture(self):
        class FooTC(TestCase):
            def test_stderr(self):
                print >> sys.stderr, "foo"
                self.assert_(False)
        test = FooTC('test_stderr')
        result = self.runner.run(test)
        captured_out, captured_err = test.captured_output()
        self.assertEqual(captured_out.strip(), "")
        self.assertEqual(captured_err.strip(), "foo") 
        
        
    def test_both_capture(self):
        class FooTC(TestCase):
            def test_stderr(self):
                print >> sys.stderr, "foo"
                print "bar"
                self.assert_(False)
        test = FooTC('test_stderr')
        result = self.runner.run(test)
        captured_out, captured_err = test.captured_output()
        self.assertEqual(captured_out.strip(), "bar")
        self.assertEqual(captured_err.strip(), "foo") 
        
    def test_no_capture(self):
        class FooTC(TestCase):
            def test_stderr(self):
                print >> sys.stderr, "foo"
                print "bar"
                self.assert_(False)
        test = FooTC('test_stderr')
        # this runner should not capture stdout / stderr
        runner = SkipAwareTextTestRunner(stream=StringIO(), exitfirst=True)
        result = runner.run(test)
        captured_out, captured_err = test.captured_output()
        self.assertEqual(captured_out.strip(), "")
        self.assertEqual(captured_err.strip(), "") 
        

    def test_capture_core(self):
        # output = capture_stdout()
        # bootstrap_print("hello", output=sys.stdout)
        # self.assertEquals(output.restore(), "hello")
        output = capture_stdout()
        bootstrap_print("hello")
        self.assertEquals(output.restore(), "hello")
        

if __name__ == '__main__':
    unittest_main()

