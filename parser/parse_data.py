import csv
import logging

logging.basicConfig(level=logging.INFO)

def parse_nma_hdr(x):
    nmas_str = ["Reserved", "Test", "Operational", "Don't use"]
    cpks_str = ["Reserved", "Nominal", "End Of Chain (EOC)", "Chain Revoked (CREV)", "New Public Key (NPK)", "Public Key Revoked (PKREV)", "Reserved", "Reserved"]
    nmas = (x & 0xC0) >> 6
    chainID = (x & 0x30) >> 4
    cpks = (x & 0x0E) >> 1
    return "NMA HDR: " + nmas_str[nmas] + " | Chain ID: " + str(chainID) + " | CPKS: " + cpks_str[cpks]

def convert_mack_words_to_bytearray(words):
    last=0
    for i in words:
        last <<= 32
        last |= i
    return last

Nbdk_lookup = [None, 728, 832, 936, 1040, 1144, 1248, 1352, 1456, None, None, None, None, None, None, None]
HF_lookup = ["SHA-256", None, "SHA3-256", None]
MF_lookup = ["HMAC-SHA-256", "CMAC-AES", None, None]
KS_lookup = [96, 104, 112, 120, 128, 160, 192, 224, 256, None, None, None, None, None, None, None]
TS_lookup = [None, None, None, None, None, 20, 24, 28, 32, 40, None, None, None, None, None, None]

def parse_dsm_kroot_msg (msg):
    parsed_dsm_kroot = {}
    stream = msg.getDSMBytes()
    parsed_dsm_kroot["NBdk"] = Nbdk_lookup[(stream[0] & 0xF0) >> 4]
    parsed_dsm_kroot["PKID"] = stream[0] & 0x0F
    parsed_dsm_kroot["CIDKR"] = (stream[1] & 0xC0) >> 6
    parsed_dsm_kroot["Reserved1"] = (stream[1] & 0x30) >> 4
    parsed_dsm_kroot["HF"] = HF_lookup[(stream[1] & 0x0C) >> 2]
    parsed_dsm_kroot["MF"] = MF_lookup[stream[1] & 0x03]
    parsed_dsm_kroot["KS"] = KS_lookup[(stream[2] & 0xF0) >> 4]
    parsed_dsm_kroot["TS"] = TS_lookup[stream[2] & 0x0F]
    parsed_dsm_kroot["MACLT"] = stream[3]
    parsed_dsm_kroot["Reserved2"] = (stream[4] & 0xF0) >> 4
    parsed_dsm_kroot["WNk"] = ((stream[4] & 0x0F) << 8) |stream[5]
    parsed_dsm_kroot["TOWHk"] = stream[6]
    parsed_dsm_kroot["alfa"] = (stream[7] << 40) | (stream[8] << 32) | (stream[9] << 24) | (stream[10] << 16) | (stream[11] << 8) | stream[12]
    bytes_key = parsed_dsm_kroot["KS"] // 8
    parsed_dsm_kroot["KROOT"] = stream[13:13+bytes_key]
    parsed_dsm_kroot["DS+Padding"] = stream[13+bytes_key:]
    return parsed_dsm_kroot


def parse_dsm_pkr_msg (msg):
    parsed_dsm_pkr = {}

class DSMMessage:
    def __init__(self, id):
        self.__dsm_id = id
        self.__dsm_blocks = [None for i in range(16)]
        self.__dsm_type = "DSM-PKR"
        self.__num_blocks = None
        if id <= 11:
            self.__dsm_type = "DSM-KROOT"
    def getDSMId(self):
        return self.__dsm_id
    def addBlock(self, index, block):
        assert (index < 16)
        self.__dsm_blocks[index] = block
        if index == 0:
            self.__num_blocks = ((block[0] & 0xF0) >> 4) + 6
    def isComplete(self):
        if self.__num_blocks != None:
            if (16 - self.__dsm_blocks.count(None)) == self.__num_blocks:
                return True
        return False
    def getDSMBytes(self):
        if self.isComplete():
            return [b for block in self.__dsm_blocks[:self.__num_blocks] for b in block]
        return None
    def __repr__(self):
        return self.__dsm_type + " (Type: " + str(self.__dsm_id) + ") " + "Num blocks: " + str(self.__num_blocks) + " Blocks: " + str(self.__dsm_blocks)

page_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]
page_counters = {}
sv_dsm_buffers = {}
sv_mack_buffers = {}
dsm_messages = {}
hkroot_sequence = ""

with open('../data_mataro2.csv') as csvfile:
    parsed_data = csv.reader(csvfile, delimiter=',')
    first = True
    last_osnma = 0

    for row in parsed_data:
        if first:
            first=False
            continue
        word1=int(row[8])
        word2=int(row[9])
        word3=int(row[10])
        word4=int(row[11])
        word5=int(row[12])
        word6=int(row[13])
        word7=int(row[14])
        word8=int(row[15])

        res1= (word5 & 0x00003FFF)  << 26
        res2 = (word6 & 0xFFFFFFC0) >> 6
        osnma = res1 | res2
        page_type = (word1 & 0x3F000000) >> 24

        if osnma != 0 and last_osnma == osnma:  # Skip repeated OSNMA frames which are different from 0
            continue
        else:
            last_osnma = osnma
        if osnma != 0:
            if row[1] not in page_counters:
                page_counters[row[1]] = 0
            hkroot_byte = (osnma & 0xFF00000000) >> 32  # Take first byte (Starting from the end)
            log_string = "SVID: " + row[1] + " Page type (even): " + str(page_type) + " OSNMA field (40 bit): " + hex(osnma) + " HKROOT BYTE: " + hex(hkroot_byte) + " "
            if page_type == 2:
                page_counters[row[1]] = 0
                sv_mack_buffers[row[1]] = [osnma & 0x00FFFFFFFF]
                log_string += "[HKROOT HEADER BYTE] " + parse_nma_hdr(hkroot_byte)
            elif page_type == 4:
                log_string += "[DSM BLOCK HEADER BYTE] DSM ID = " + hex((hkroot_byte & 0xF0) >> 4) + " DSM BLOCK ID = " + hex(hkroot_byte & 0x0F)
                sv_dsm_buffers[row[1]] = [hkroot_byte]
                if row[1] in sv_mack_buffers:
                    sv_mack_buffers[row[1]].append(osnma & 0x00FFFFFFFF)
                if ((hkroot_byte & 0xF0) >> 4) <= 11:
                    log_string += " (DSM-KROOT MESSAGE)"
                else:
                    log_string += " (DSM-PKR MESSAGE)"
            else:
                log_string += "[DSM BLOCK n byte] " + hex(hkroot_byte)
                if row[1] in sv_dsm_buffers:
                     sv_dsm_buffers[row[1]].append(hkroot_byte)
                if row[1] in sv_mack_buffers:
                     sv_mack_buffers[row[1]].append(osnma & 0x00FFFFFFFF)
            
            if page_type not in page_types_sequence[page_counters[row[1]]]:
                log_string += " ¡¡ PAGE SEQUENCE BROKEN !! Expected page Type = " + str(page_counters[row[1]])
                page_counters[row[1]] = 0
                sv_dsm_buffers[row[1]] = []
                sv_mack_buffers[row[1]] = []
            
            if page_counters[row[1]] == 14:
                logging.debug("SVID: " + row[1] + "DSM/MACK BLOCK COMPLETE (" + hex(sv_dsm_buffers[row[1]][0]) + "): " + str(list(map(hex,sv_dsm_buffers[row[1]][1:]))) + " | " + str(list(map(hex,sv_mack_buffers[row[1]]))))
                logging.debug(hex(convert_mack_words_to_bytearray(sv_mack_buffers[row[1]])))
                log_string += " ¡¡PAGE SQUENCE COMPLETE!! "
                log_string += str(bytearray(sv_dsm_buffers[row[1]]))
                dsm_id = (sv_dsm_buffers[row[1]][0] & 0xF0) >> 4
                block_id = sv_dsm_buffers[row[1]][0] & 0x0F
                if dsm_id not in dsm_messages:
                    dsm_messages[dsm_id] = DSMMessage(dsm_id)
                dsm_messages[dsm_id].addBlock(block_id, sv_dsm_buffers[row[1]][1:])
                if dsm_messages[dsm_id].isComplete():
                    log_string += "¡¡¡DSM MESSAGE COMPLETE!!! " + dsm_messages[dsm_id].__repr__() # Take care that no different SV buffers used for the same DSM Message (Assumming all sats transmit equally)
                sv_dsm_buffers[row[1]] = []
                page_counters[row[1]] = 0
            else:
                page_counters[row[1]] += 1

            log_string += " page_counters["+row[1]+"]= " + str(page_counters[row[1]])
            
            logging.debug(log_string)
            hkroot_sequence += hex(hkroot_byte) + ","
        else:
            logging.debug("0 OSNMA WORD for SVID: " + row[1])
logging.info (str(dsm_messages))
logging.info(str(parse_dsm_kroot_msg(dsm_messages[4])))