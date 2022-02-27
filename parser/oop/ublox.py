
class UbloxParser:
    def __init__(self, page_reader, page_processor):
        self.__page_reader = page_reader
        self.__page_processor = page_processor
    def process_page(self):
        inav = self.__page_reader()
        inav = inav.split(',')
        svid = int(inav[2])
        word1 = int(inav[9])
        word2 = int(inav[10])
        word3 = int(inav[11])
        word4 = int(inav[12])
        word5 = int(inav[13])
        word6 = int(inav[14])
        word7 = int(inav[15])
        word8 = int(inav[16])

        res1= (word5 & 0x00003FFF)  << 26
        res2 = (word6 & 0xFFFFFFC0) >> 6
        osnma = res1 | res2
        page_type = (word1 & 0x3F000000) >> 24
        data_word = ((0x3FFFFFFF & word1) <<  98) | (word2 << 66) | (word3 << 34) | (((word4 & 0xFFFFC000) >> 14) << 16) | ((word5 & 0x3FFFC000) >> 14)

        self.__page_processor(svid, page_type, osnma, data_word.to_bytes(16, 'big'))