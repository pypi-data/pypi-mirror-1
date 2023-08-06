import unittest

class DummyTest(unittest.TestCase):
    def runTest(self):
        values = set((1, 4, 1, 2, 5, 3, 7, 3, 12))
        for toto in ( val * 4  for val in values if val % 2):
            self.assertEqual(toto,toto)

def Run(runner=None):
    testsuite = unittest.TestSuite()
    testsuite.addTest(DummyTest())

    if runner is None:
        runner = unittest.TextTestRunner()
    return runner.run(testsuite)

if __name__ == '__main__':
    Run()

