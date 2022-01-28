import csv
import logging
import time
import binascii
from math import floor
from console import fg, bg, fx
from console.screen import sc
from console.utils import cls, set_title

logging.basicConfig(filename='osnma.log', format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)

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

def unpack_mack_array(mack_array):
    arr = []
    for quad in mack_array:
        arr.append((quad & 0xFF000000) >> 24)
        arr.append((quad & 0x00FF0000) >> 16)
        arr.append((quad & 0x0000FF00) >> 8)
        arr.append(quad & 0x000000FF)
    return arr

def parse_mack_msg(msg, dsm_kroot):
    mbytes = unpack_mack_array(msg)
    parsed_mack_msg = {}
    parsed_mack_msg["Tag0"] = bytearray(mbytes[0:5])  #Fixed to 40 bits (5 bytes) but should be variable depending on TS value in DSM-KROOT message
    parsed_mack_msg["MACSEQ"] = (mbytes[5] << 4) | (mbytes[6] & 0xF0) >> 4
    num_tags = floor((480-128)/(40+16)) # Key(128) and tag(40) sizes shall be extracted from DSM-KROOT
    tags_and_info = []
    next_index = 7
    for i in range(num_tags):
        ti = {}
        ti["Tag"] = bytearray(mbytes[next_index:next_index+5])
        ti["Tag-Info"] = mbytes[next_index+5:next_index+7]
        ti["PRN"] = ti["Tag-Info"][0]
        ti["ADKD"] = (ti["Tag-Info"][1] & 0xF0) >> 4
        tags_and_info.append(ti)
        next_index +=7
    parsed_mack_msg["TagsAndInfo"] = tags_and_info
    parsed_mack_msg["Key"] = bytearray(mbytes[next_index:next_index+16])
    return parsed_mack_msg

class DSMMessage:
    def __init__(self, id):
        self.__dsm_id = id
        self.__dsm_blocks = [None for i in range(16)]
        self.__dsm_type = "DSM-PKR"
        self.__num_blocks = None
        self.__curr_blocks = 0
        if id <= 11:
            self.__dsm_type = "DSM-KROOT"
    def getDSMId(self):
        return self.__dsm_id
    def getDSMType(self):
        return self.__dsm_type
    def getNumBlocks(self):
        return self.__num_blocks
    def getCurrBlocks(self):
        return self.__curr_blocks
    def addBlock(self, index, block):
        assert (index < 16)
        if self.__dsm_blocks[index] == None:
            self.__curr_blocks += 1
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
sats_in_view = {}
block_stats = {"Complete": 0, "OOS": 0}
hkroot_sequence = ""
osnma_status = None

def setup_screen (title):
    set_title(title)

def update_screen (sv_list):
    cls()
    with sc.location(1,1):
        sv_list_str = ""
        for sv in sv_list:
            if sv_list[sv][1]:
                sv_list_str += fg.green + sv + fg.default + ', '
            else:
                sv_list_str += fg.red + sv + fg.default + ', '
        print ('[SV in View]\n')
        print(sv_list_str[:-2])
        print ('\n[Block Statistics]\n')
        print (fg.green + 'Complete Blocks: ' + str(block_stats["Complete"]) + fg.default)
        print (fg.red + 'Out of Sequence Blocks: ' + str(block_stats["OOS"]) + fg.default)
        for dsmid in dsm_messages:
            print('\n[DSM Blocks]\n')
            print('Type: ', dsm_messages[dsmid].getDSMType(), ' Blocks Available: ', str(dsm_messages[dsmid].getCurrBlocks()), '/', str(dsm_messages[dsmid].getNumBlocks()))
            if dsm_messages[dsmid].isComplete():
                parsed_dsm = parse_dsm_kroot_msg(dsm_messages[dsmid]) #avoid parsing at each iteration, to be cached
                print('\n\tHash Function: ', parsed_dsm["HF"])
                print('\tMAC Function: ', parsed_dsm["MF"])
                print('\tKey Size: ', parsed_dsm["KS"])
                print('\tTag Size: ', parsed_dsm["TS"])

setup_screen('OSNMA Processor')

with open('../data_mataro2.csv') as csvfile:
    parsed_data = csv.reader(csvfile, delimiter=',')
    first = True
    last_osnma = 0

    for row in parsed_data:
        time.sleep(0.3) #simulated delay
        if first:
            first=False
            continue
        sv_num = row[1]
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
        sats_in_view[sv_num] = (time.time(), osnma != 0)

        if osnma != 0 and last_osnma == osnma:  # Skip repeated OSNMA frames which are different from 0
            continue
        else:
            last_osnma = osnma
        if osnma != 0:
            if sv_num not in page_counters:
                page_counters[sv_num] = 0
            hkroot_byte = (osnma & 0xFF00000000) >> 32  # Take first byte (Starting from the end)
            log_string = "SVID: " + sv_num + " Page type (even): " + str(page_type) + " OSNMA field (40 bit): " + hex(osnma) + " HKROOT BYTE: " + hex(hkroot_byte) + " "
            if page_type == 2:
                page_counters[sv_num] = 0
                sv_mack_buffers[sv_num] = [osnma & 0x00FFFFFFFF]
                log_string += "[HKROOT HEADER BYTE] " + parse_nma_hdr(hkroot_byte)
            elif page_type == 4:
                log_string += "[DSM BLOCK HEADER BYTE] DSM ID = " + hex((hkroot_byte & 0xF0) >> 4) + " DSM BLOCK ID = " + hex(hkroot_byte & 0x0F)
                sv_dsm_buffers[sv_num] = [hkroot_byte]
                if sv_num in sv_mack_buffers:
                    sv_mack_buffers[sv_num].append(osnma & 0x00FFFFFFFF)
                if ((hkroot_byte & 0xF0) >> 4) <= 11:
                    log_string += " (DSM-KROOT MESSAGE)"
                else:
                    log_string += " (DSM-PKR MESSAGE)"
            else:
                log_string += "[DSM BLOCK n byte] " + hex(hkroot_byte)
                if sv_num in sv_dsm_buffers:
                     sv_dsm_buffers[sv_num].append(hkroot_byte)
                if sv_num in sv_mack_buffers:
                     sv_mack_buffers[sv_num].append(osnma & 0x00FFFFFFFF)
            
            if page_type not in page_types_sequence[page_counters[sv_num]]:
                block_stats["OOS"] += 1
                log_string += " ¡¡ PAGE SEQUENCE BROKEN !! Expected page Type = " + str(page_counters[sv_num])
                page_counters[sv_num] = 0
                sv_dsm_buffers[sv_num] = []
                sv_mack_buffers[sv_num] = []
            
            if page_counters[sv_num] == 14:
                block_stats["Complete"] += 1
                logging.debug("SVID: " + sv_num + "DSM/MACK BLOCK COMPLETE (" + hex(sv_dsm_buffers[sv_num][0]) + "): " + str(list(map(hex,sv_dsm_buffers[sv_num][1:]))) + " | " + str(list(map(hex,sv_mack_buffers[sv_num]))))
                #mack = parse_mack_msg(convert_mack_words_to_bytearray(sv_mack_buffers[sv_num]), None)
                #logging.info("KEY: " + binascii.hexlify(mack['Key']))
                log_string += " ¡¡PAGE SQUENCE COMPLETE!! "
                log_string += str(bytearray(sv_dsm_buffers[sv_num]))
                dsm_id = (sv_dsm_buffers[sv_num][0] & 0xF0) >> 4
                block_id = sv_dsm_buffers[sv_num][0] & 0x0F
                logging.info("SVID: " + sv_num + "DSM/MACK BLOCK COMPLETE (" + str(block_id) + ")")
                if dsm_id not in dsm_messages:
                    dsm_messages[dsm_id] = DSMMessage(dsm_id)
                dsm_messages[dsm_id].addBlock(block_id, sv_dsm_buffers[sv_num][1:])
                if dsm_messages[dsm_id].isComplete():
                    log_string += "¡¡¡DSM MESSAGE COMPLETE!!! " + dsm_messages[dsm_id].__repr__() # Take care that no different SV buffers used for the same DSM Message (Assumming all sats transmit equally)
                    logging.info(log_string)
                sv_dsm_buffers[sv_num] = []
                page_counters[sv_num] = 0
            else:
                page_counters[sv_num] += 1

            log_string += " page_counters["+sv_num+"]= " + str(page_counters[sv_num])
            
            logging.debug(log_string)
            hkroot_sequence += hex(hkroot_byte) + ","
        else:
            logging.debug("0 OSNMA WORD for SVID: " + sv_num)
        update_screen(sats_in_view)
logging.info (str(dsm_messages))
dsm_kr = parse_dsm_kroot_msg(dsm_messages[3])
logging.info(str(dsm_kr))
logging.info(str(sv_mack_buffers))
logging.info(str(parse_mack_msg(sv_mack_buffers['14'], dsm_kr)))