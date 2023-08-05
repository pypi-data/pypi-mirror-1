import unittest

class GeneralTest(unittest.TestCase):
    def testGeneral(self):
        self.assertEquals(1, 1)

    def testSomething(self):
        self.assertEquals(2, 2)

    def testSomethingOther(self):
        self.assertEquals(3, 3)

class GeneralTest2(unittest.TestCase):
    def testGeneral(self):
        self.assertEquals(1, 1)


