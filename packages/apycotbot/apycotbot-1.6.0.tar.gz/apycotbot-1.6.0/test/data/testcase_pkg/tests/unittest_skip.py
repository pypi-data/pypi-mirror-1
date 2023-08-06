from logilab.common.testlib import TestCase, unittest_main

class DummyTest(TestCase):
    def runTest(self):
        self.skip("I'm singing in the rain")


if __name__ == '__main__':
    unittest_main()

