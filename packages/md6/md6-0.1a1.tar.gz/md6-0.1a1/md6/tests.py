import unittest

from md6 import md6

class TestMD6(unittest.TestCase):

    def test_md6_256(self):
        self._test(md6, 256)

    def _test(self, factory, digest_size):
        m = factory()
        self.assertEqual(m.digest_size, digest_size)

        m.update("abc")
        m.hexdigest()
        m.digest()
        m.update("def")
        
        m2 = factory()
        m2.update("abcdef")

        m3 = factory("abcdef")

        self.assertEqual(m.hexdigest(), m2.hexdigest())
        self.assertEqual(m.hexdigest(), m3.hexdigest())
        self.assertEqual(m.digest(), m2.digest())
        self.assertEqual(m.digest(), m3.digest())

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMD6))
    unittest.TextTestRunner(verbosity=2).run(suite)
