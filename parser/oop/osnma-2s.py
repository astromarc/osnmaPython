import logging
import sys
from ublox import UbloxParser
from galileo import SubframeProcessorConstellation

class Preader:
    def __init__ (self, fname):
        self.__f= open (fname, 'r')
    def read_page (self):
        return self.__f.readline()

def main():
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)
    preader = Preader('../../test_data/data_mataro3.csv')
    sf = SubframeProcessorConstellation()
    ux = UbloxParser(preader, sf)
    while True:
        ux.process_page()
if __name__ == "__main__":
    main()