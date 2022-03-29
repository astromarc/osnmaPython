from bitarray import bitarray



class svKrootOsnmaMack:
    def __init__(self):
        self.__CID = bytearray()
        self.__DSMBlockId = bytearray()
        self.__DSMId = bytearray()
        self.__CDPKS = bytearray()
        self.__hkroot = []
        self.__mack = []
        self.__NMAS = bytearray()
    def osnmaSubFrame2hkRootMack(self, osnmaSubFrame=[]):
        self.__hkroot = []
        self.__mack = []
        for osnmapage in osnmaSubFrame:
            a = bitarray()
            a.frombytes(osnmapage)
            self.__hkroot.append(a[0:8].tobytes)
            self.__mack.append(a[-32:].tobytes)
        a1 = self.__hkroot[0]
        print(a1)
        # a = bitarray()
        # a.frombytes(a1)
        # b1 = self.__hkroot[1]
        # b = bitarray()
        # b.frombytes(b1)
        # self.__CID = a[2:4].tobytes
        # self.__NMAS = a[0:2].tobytes
        # self.__CDPKS = a[4:7].tobytes
        # self.__DSMId = b[0:4].tobytes
    def getCID(self):
        return self.__CID
    def getDSMBlockId(self):
        return self.__DSMBlockId
    def getDSMId(self):
        return self.__DSMId
    def getDSKPKS(self):
        return self.__DSKPKS
    def getDSKPKS(self):
        return self.__DSKPKS
    def getHkroot(self):
        return self.__hkroot
    def getMack(self):
        return self.__mack