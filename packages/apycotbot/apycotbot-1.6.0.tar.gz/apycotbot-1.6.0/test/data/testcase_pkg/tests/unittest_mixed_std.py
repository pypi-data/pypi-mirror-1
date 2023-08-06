from unittest import TestCase, main

class DummyTest(TestCase):
    def test_ok(self):
        self.failUnlessEqual(1, 1)
    def test_ok2(self):
        pass

    def test_fail_0(self):
        self.assertEquals(1337, 0)

    def test_fail_1(self):
        self.assertEquals(1337, 1)

    def test_fail_2(self):
        self.assertEquals(1337, 2)

    def test_fail_3(self):
        self.assertEquals(1337, 3)

    def test_fail_4(self):
        self.assertEquals(1337, 4)

    def test_fail_5(self):
        self.assertEquals(1337, 5)

    def test_fail_6(self):
        self.assertEquals(1337, 6)

    def test_fail_7(self):
        self.assertEquals(1337, 7)

    def test_fail_8(self):
        self.assertEquals(1337, 8)

    def test_fail_9(self):
        self.assertEquals(1337, 9)

    def test_fail_10(self):
        self.assertEquals(1337, 10)

    def test_fail_11(self):
        self.assertEquals(1337, 11)

    def test_fail_12(self):
        self.assertEquals(1337, 12)

    def test_fail_13(self):
        self.assertEquals(1337, 13)

    def test_fail_14(self):
        self.assertEquals(1337, 14)


    def test_errors(self):
        int.dsqhgdlsjgjl


if __name__ == '__main__':
    main()

