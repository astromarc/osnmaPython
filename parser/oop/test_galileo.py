import unittest
import galileo
from bitarray import bitarray
from bitarray.util import int2ba

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

class TestMackParser(unittest.TestCase):
    def test_real_data(self):
        mack=[0xE094B3FB, 0xA533A6A6, 0xB55DFED5, 0x05055EBE, 0xC4E3A8FF, 0x40B580AE, 0xB1511905, 0x78A85B87, 
        0x9301C6B3, 0xE3315F47, 0x1B0517B9, 0x8FD42A4A, 0xFD0EA36D, 0x1DA2DE40, 0x6B930000]

        parsed_mack = galileo.parse_mack_msg(mack)
        self.assertEqual(parsed_mack["Tag0"], int2ba(0xE094B3FBA5, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack["MACSEQ"], int2ba(0x33A, length=12, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][0]['Tag'], int2ba(0xA6B55DFED5, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][0]['PRN'], 5)
        self.assertEqual(parsed_mack['TagsAndInfo'][0]['ADKD'], 0)
        self.assertEqual(parsed_mack['TagsAndInfo'][1]['Tag'], int2ba(0x5EBEC4E3A8, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][1]['PRN'], 255)
        self.assertEqual(parsed_mack['TagsAndInfo'][1]['ADKD'], 4)
        self.assertEqual(parsed_mack['TagsAndInfo'][2]['Tag'], int2ba(0xB580AEB151, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][2]['PRN'], 25)
        self.assertEqual(parsed_mack['TagsAndInfo'][2]['ADKD'], 0)
        self.assertEqual(parsed_mack['TagsAndInfo'][3]['Tag'], int2ba(0x78A85B8793, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][3]['PRN'], 1)
        self.assertEqual(parsed_mack['TagsAndInfo'][3]['ADKD'], 12)
        self.assertEqual(parsed_mack['TagsAndInfo'][4]['Tag'], int2ba(0xB3E3315F47, length=40, endian='big', signed=False))
        self.assertEqual(parsed_mack['TagsAndInfo'][4]['PRN'], 27)
        self.assertEqual(parsed_mack['TagsAndInfo'][4]['ADKD'], 0)
        

if __name__ == "__main__":
    unittest.main()