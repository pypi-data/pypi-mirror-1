import unittest
class DummyTest(unittest.TestCase):
    def runTest(self):
        self.failUnlessEqual(1, 0)

def Run(runner=None):
    testsuite = unittest.TestSuite()
    testsuite.addTest(DummyTest())

    if runner is None:
        runner = unittest.TextTestRunner()
    return runner.run(testsuite)

if __name__ == '__main__':
    Run()
