import collections
import enum
class SubframeBuffer:
    def __init__(self, size):
        self.__buffer = collections.deque(maxlen=size)
    def addSubframe(self, sf):
        self.__buffer.append(sf)
    def getSubframe(self, index):
        try:
            return self.__buffer[i]
        except:
            return None

word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]

class SubframeProcessingStates(enum.Enum):
    OUT_OF_SYNC = 1
    PROCESSING_FRAME = 2
    COMPLETING_SUBFRAME = 3

# Page processor which receives page information, including data words, osnma per SVID
# and ends up building subframes
# For each complete subframe received, for a given SV ID, an object of this class may output:
#  - All the words forming the subframe
#  - The 15 OSNMA words
#  - TBD: SAR and other page information.
#
# The code is also responsible for filtering out incomplete subframe data.
# An instance of this object may be made by each SV ID so that a specific state machine is kept
# by each satellite.
# States OUT_OF_SYNC, PROCESSING_FRAME, FRAME_COMPLETE
class SubframeProcessor:
    def __init__(self):
        self.__state = SubframeProcessingStates.OUT_OF_SYNC
        self.__inav_receivers = []
        self.__osnma_receivers = []
    def subscribeInavDataReceiver (self, receiver):
        self.__inav_receivers.append(receiver)
    def subscribeOSNMADataReceiver (self, receiver):
        self.__osnma_receivers.append(receiver)
    
    def proccessPage(svid, word_type, osnma, inav_data):
        switch(self.__state)
        if self.__state == SubframeProcessingStates.OUT_OF_SYNC:
            pass
        elif self.__state == SubframeProcessingStates.PROCESSING_FRAME:
            pass
        elif self.__state == SubframeProcessingStates.COMPLETING_SUBFRAME:
            pass
        else:
            raise AssertionError("Unknown state in Subframe processor")
