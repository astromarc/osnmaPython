from bitarray import bitarray

class UbloxParser:
    # page_reader Arbitrary object containing the implementation of read_page() method from where pages are physically read (e.g. serial line)
    # page_processor Arbitrary object containing the implementation of process page method where pages are passed (e.g. Galileo Page Parser)
    def __init__(self, page_reader, page_processor):
        self.__page_reader = page_reader
        self.__page_processor = page_processor
    def process_page(self):
        inav = self.__page_reader.read_page()
        inav = inav.split(',')
        svid = int(inav[2])
        words = [bitarray () for x in range(8)]
        page = bitarray()
        for i in range(8):
            words[i].frombytes(int(inav[9+i]).to_bytes(4,'big'))
            page += words[i]
        
        osnma = page[147:180]
        word_type = bitarray('00') + page[2:8]
        data_word = page[2:32] + page[32:64] + page[64:96] + page[96:114] + page[130:146]
        self.__page_processor.process_page(svid, int.from_bytes(word_type.tobytes(),'big'), osnma.tobytes(), data_word.tobytes())
