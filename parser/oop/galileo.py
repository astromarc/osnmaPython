import collections
import enum
import logging
from bitarray import bitarray
from bitarray.util import ba2int
from math import floor

word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]

class SubframeProcessingStates(enum.Enum):
    OUT_OF_SYNC = 1
    PROCESSING_SUBFRAME = 2
    COMPLETING_SUBFRAME = 3

# Page processor which receives page information, including data words, osnma per a given SVID
# and ends up building OSNMA and NAV data grouped in subrafmes.
# For each complete subframe received, for a given SV ID, an object of this class may output:
#  - All the words forming the subframe
#  - The 15 OSNMA words
#  - TBD: SAR and other page information.
#
# The code is also responsible for filtering out incomplete subframe data.
# An instance of this object may be made by each SV ID so that a specific state machine is kept
# by each satellite.
# States OUT_OF_SYNC, PROCESSING_SUBFRAME, FRAME_COMPLETE
class SubframeProcessorSvid:
    def __init__(self, svid):
        self.__state = SubframeProcessingStates.OUT_OF_SYNC
        self.__word_counter = 0
        self.__inav_data = []
        self.__osnma_data = []
        self.__subframe_receivers = []
        self.__svid = svid
    def subscribeSubframeReceiver (self, receiver):
        self.__subframe_receivers.append(receiver)
    # State machine entry point
    def process_page(self, word_type, osnma, inav_data):
        # Execute the function corresponding to the current state and get the next state
        logging.debug('Processing page for satellite ID ' + str(self.__svid))
        if self.__state == SubframeProcessingStates.OUT_OF_SYNC:
            self.out_of_sync_state(word_type, osnma, inav_data)
        elif self.__state == SubframeProcessingStates.PROCESSING_SUBFRAME:
            self.processing_subframe(word_type, osnma, inav_data)
        elif self.__state == SubframeProcessingStates.COMPLETING_SUBFRAME:
            self.completing_subframe(word_type, osnma, inav_data)
        else:
            raise Exception("Invalid state")
    # Out of sync state function. Skip words until word type becomes the desired one. Then change state to processing
    def out_of_sync_state(self, word_type, osnma, inav_data):
        if word_type not in word_types_sequence[self.__word_counter]:
            return SubframeProcessingStates.OUT_OF_SYNC
        else:
            return self.processing_subframe(word_type, osnma, inav_data)
    # Processing state function. Accumulate data and output values
    def processing_subframe(self, word_type, osnma, inav_data):
        if word_type not in word_types_sequence[self.__word_counter]:
            return SubframeProcessingStates.OUT_OF_SYNC
        else:
            self.__osnma_data.append(osnma)
            self.__inav_data.append(inav_data)
            if self.__word_counter == 14:
                return self.completing_subframe(word_type, osnma, inav_data)
            else:
                self.__word_counter += 1
                return SubframeProcessingStates.PROCESSING_SUBFRAME
    # Completing state. Output accumulated data, clean buffers
    def completing_subframe(self, word_type, osnma, inav_data):
        for receiver in self.__subframe_receivers:
            receiver.new_subframe(self.__inav_data, self.__osnma_data)
        self.__word_counter = 0
        self.__inav_data = []
        self.__osnma_data = []
        logging.debug('Subframe complete for SV ID ' + str(self.__svid))
        return SubframeProcessingStates.PROCESSING_SUBFRAME

# This class is an aggregator of SubframeProcessorSvid for all satellites in view
class SubframeProcessorConstellation:
    def __init__(self):
        self.__svids = {}
    def process_page(self, svid, word_type, osnma_word, inav_data):
        if svid not in self.__svids:
            self.__svids[svid] = SubframeProcessorSvid(svid)
        self.__svids[svid].process_page (word_type, osnma_word, inav_data)

def parse_mack_msg(msg):
    mbytes = bitarray()
    for i in range(15):
        mbytes.frombytes(int(msg[i]).to_bytes(4,'big'))
    parsed_mack_msg = {}
    parsed_mack_msg["Tag0"] = mbytes[0:40]  #Fixed to 40 bits (5 bytes) but should be variable depending on TS value in DSM-KROOT message
    parsed_mack_msg["MACSEQ"] = mbytes[40:52]
    num_tags = floor((480-128)/(40+16)) - 1 # Key(128) and tag(40) sizes shall be extracted from DSM-KROOT
    tags_and_info = []
    next_index = 56
    for i in range(num_tags):
        ti = {}
        ti["Tag"] = mbytes[next_index:next_index+40]
        ti["Tag-Info"] = mbytes[next_index+40:next_index+56]
        ti["PRN"] = ba2int(ti["Tag-Info"][0:8])
        ti["ADKD"] = ba2int(ti["Tag-Info"][8:12])
        tags_and_info.append(ti)
        next_index +=56
    parsed_mack_msg["TagsAndInfo"] = tags_and_info
    parsed_mack_msg["Key"] = mbytes[next_index:next_index+128]
    return parsed_mack_msg

# Class responsible for processing MACK message from different satellites,
# Parssing it and storing it for furhter use. It interfaces (via subscription) with
# SubframeProcessorSvid.
class MackMessageProcessor:
    def __init__(self):
        pass
    def new_subframe(self, inav_data, osnma_data):
        pass
