# coding=utf-8
from print_r import print_r
import unittest, logging
logging.basicConfig(level=logging.DEBUG)
class Test:
    mylist = [1, 2, 3]
    myvar = 123
    def func():
        pass

class Sometests(unittest.TestCase):

    def setUp(self):
        self.test = Test()
        self.test.myvar = 456
        self.mylist = [[1, 2, 3, [4, (7, 8, 9), {"a":1, "b":"cde"}]]]
        self.tests = [Test, self.test, self.mylist, 123, [1, 1]]

    def testa(self):
        print_r(self.tests)
    def testc(self):
        import datetime, math, os, pickle
        print_r(datetime)

    def testb(self):
        self.assert_(print_r(123), "123")
        self.assert_(print_r([1], "1 = 1"))

unittest.main()
