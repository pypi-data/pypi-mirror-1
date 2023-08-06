import unittest
from binascii import unhexlify

from md6 import md6

class TestMD6(unittest.TestCase):

    def test_md6_256(self):
        self._test(md6, 256)
        
    def assertHash(self, factory, hex, result):
        hash = factory(unhexlify(hex)).hexdigest().upper()
        self.assertEqual(hash, result)

    def _test(self, factory, digest_size):
        m = factory()
        self.assertEqual(m.digest_size, digest_size)

        m.update("abc")
        m.digest()
        m.update("def")
        
        m2 = factory()
        m2.update("abcdef")

        m3 = factory("abcdef")

        self.assertEqual(m.hexdigest(), m2.hexdigest())
        self.assertEqual(m.hexdigest(), m3.hexdigest())
        self.assertEqual(m.digest(), m2.digest())
        self.assertEqual(m.digest(), m3.digest())

        # values taken from http://groups.csail.mit.edu/cis/md6/revision-2009-04-15/KAT_MCT/ShortMsgKAT_256.txt        
        self.assertHash(factory, "",
            "BCA38B24A804AA37D821D31AF00F5598230122C5BBFC4C4AD5ED40E4258F04CA")
        self.assertHash(factory, "CC",
            "F5B3D76FE6D1B0854D4E516C64F21C57DE91F39534E1D94AE0FBBFCE3A55BAB6")
        self.assertHash(factory, "41FB",
            "8477ED8F7D650542B803DC007EAE62D0AB5FA132544230A3A4F37B6A1A9C50BD")
        self.assertHash(factory,
            "9F2FCC7C90DE090D6B87CD7E9718C1EA6CB21118FC2D5DE9F97E5DB6AC1E9C10",
            "C5B384E7C49795B400D39184C57165948D6FE2EC1E99B72A0BE4165057023246")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMD6))
    unittest.TextTestRunner(verbosity=2).run(suite)
