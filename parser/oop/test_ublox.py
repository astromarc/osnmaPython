import ublox
import unittest

rx_page = '18:14:13.7413,Galileo,3,1,0,9,4,2,0,86966039,4045406688,2282300530,2922020864,2863300608,42,2863298271,780091392,1'
rx_page_data_only_1 = '18:14:13.7413,Galileo,3,1,0,9,4,2,0,714440703,4294967295,4294967295,4294950912,359301120,0,0,0,1'

class TestUbloxParser(unittest.TestCase):
    def read_page(self):
        return rx_page_data_only_1
    def process_page (self, svid, page_type, osnma, inav_data):
        self.assertEqual(inav_data, bytearray([0xaa, 0x55, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x55, 0xaa]))
        self.assertEqual(svid, 3)
        self.assertEqual(osnma, b'\x00\x00\x00\x00\x00')
        self.assertEqual(page_type, 0x2a)
    def test_create(self):
        ubrx = ublox.UbloxParser(self, self)
        self.assertNotEqual(ubrx, None)
        ubrx.process_page()

if __name__ == "__main__":
    unittest.main()