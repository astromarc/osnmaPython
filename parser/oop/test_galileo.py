import unittest
import galileo

class TestSubframeProcessor(unittest.TestCase):
    def new_subframe(self, inav, osnma):
        self.assertTrue(self.__its_time, "new subframe called when all frames are received")
        self.__its_time = False
        self.assertEqual(osnma, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
        self.assertEqual(inav, ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'])
    def testNominal(self):
        self.__its_time = False
        sp = galileo.SubframeProcessor(23)
        sp.subscribeSubframeReceiver(self)
        sp.proccessPage(2, 1, 'A')
        sp.proccessPage(4, 2, 'B')
        sp.proccessPage(6, 3, 'C')
        sp.proccessPage(7, 4, 'D')
        sp.proccessPage(10, 5, 'E')
        sp.proccessPage(0, 6, 'F')
        sp.proccessPage(0, 7, 'G')
        sp.proccessPage(0, 8, 'H')
        sp.proccessPage(0, 9, 'I')
        sp.proccessPage(0, 10, 'J')
        sp.proccessPage(1, 11, 'K')
        sp.proccessPage(3, 12, 'L')
        sp.proccessPage(5, 13, 'M')
        sp.proccessPage(0, 14, 'N')
        self.__its_time = True
        sp.proccessPage(0, 15, 'O')

if __name__ == "__main__":
    unittest.main()