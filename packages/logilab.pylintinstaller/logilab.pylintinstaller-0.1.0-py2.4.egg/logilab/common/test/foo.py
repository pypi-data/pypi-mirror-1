from logilab.common.testlib import TestCase, InnerTest, unittest_main

class MyTest(TestCase):

    def _check(self, i, j):
        self.assertEquals(i, j)
    
    def test_foo(self):
        for i in xrange(5):
            if i%2 == 0:
                yield InnerTest('even', self._check, i, i)
            else:
                yield InnerTest('odd', self._check, i, i)

    def test_bar(self):
        pass

    def test_foobar(self):
        pass

    def test_spam(self):
        pass
    


if __name__ == '__main__':
    unittest_main()

    
