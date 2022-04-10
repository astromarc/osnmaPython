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
        sp = galileo.SubframeProcessorSvid(23)
        sp.subscribeSubframeReceiver(self)
        sp.process_page(2, 1, 'A')
        sp.process_page(4, 2, 'B')
        sp.process_page(6, 3, 'C')
        sp.process_page(7, 4, 'D')
        sp.process_page(10, 5, 'E')
        sp.process_page(0, 6, 'F')
        sp.process_page(0, 7, 'G')
        sp.process_page(0, 8, 'H')
        sp.process_page(0, 9, 'I')
        sp.process_page(0, 10, 'J')
        sp.process_page(1, 11, 'K')
        sp.process_page(3, 12, 'L')
        sp.process_page(5, 13, 'M')
        sp.process_page(0, 14, 'N')
        self.__its_time = True
        sp.process_page(0, 15, 'O')

if __name__ == "__main__":
    unittest.main()