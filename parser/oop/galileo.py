import collections

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


class Subframe:
    def __init__(self):
        pass
    def addWord(rxwords):
        pass