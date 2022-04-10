import collections
import enum
import logging

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

class SubframeProcessorConstellation:
    def __init__(self):
        self.__svids = {}
    def process_page(self, svid, word_type, osnma_word, inav_data):
        if svid not in self.__svids:
            self.__svids[svid] = SubframeProcessorSvid(svid)
        self.__svids[svid].process_page (word_type, osnma_word, inav_data)