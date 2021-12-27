import csv
import logging

logging.basicConfig(level=logging.DEBUG)

def parse_nma_hdr(x):
    nmas_str = ["Reserved", "Test", "Operational", "Don't use"]
    cpks_str = ["Reserved", "Nominal", "End Of Chain (EOC)", "Chain Revoked (CREV)", "New Public Key (NPK)", "Public Key Revoked (PKREV)", "Reserved", "Reserved"]
    nmas = (x & 0xC0) >> 6
    chainID = (x & 0x30) >> 4
    cpks = (x & 0x0E) >> 1
    return "NMA HDR: " + nmas_str[nmas] + " | Chain ID: " + str(chainID) + " | CPKS: " + cpks_str[cpks]


class DSMMessage:
    def __init__(self, id):
        self.__dsm_id = id
        self.__dsm_blocks = [None for i in range(16)]
    def getDSMId(self):
        return self.__dsm_id
    def addBlock(self, index, block):
        assert (index < 16)
        self.__dsm_blocks[index] = block
    def isComplete(self):
        pass
    def __repr__(self):
        return str(self.__dsm_blocks)

page_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]
page_counters = {}
sv_dsm_buffers = {}
dsm_messages = {}
hkroot_sequence = ""

with open('../data_processed.csv') as csvfile:
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
                log_string += "[HKROOT HEADER BYTE] " + parse_nma_hdr(hkroot_byte)
            elif page_type == 4:
                log_string += "[DSM BLOCK HEADER BYTE] DSM ID = " + hex((hkroot_byte & 0xF0) >> 4) + " DSM BLOCK ID = " + hex(hkroot_byte & 0x0F)
                sv_dsm_buffers[row[1]] = [hkroot_byte]
                if ((hkroot_byte & 0xF0) >> 4) <= 11:
                    log_string += " (DSM-KROOT MESSAGE)"
                else:
                    log_string += " (DSM-PKR MESSAGE)"
            else:
                log_string += "[DSM BLOCK n byte] " + hex(hkroot_byte)
                if row[1] in sv_dsm_buffers:
                     sv_dsm_buffers[row[1]].append(hkroot_byte)
            
            if page_type not in page_types_sequence[page_counters[row[1]]]:
                log_string += " ¡¡ PAGE SEQUENCE BROKEN !! Expected page Type = " + str(page_counters[row[1]])
                #page_counters[row[1]] = 0
                sv_dsm_buffers[row[1]] = []
            
            if page_counters[row[1]] == 14:
                logging.info("SVID: " + row[1] + " BLOCK COMPLETE (" + hex(sv_dsm_buffers[row[1]][0]) + "): " + str(list(map(hex,sv_dsm_buffers[row[1]][1:]))))
                log_string += " ¡¡PAGE SQUENCE COMPLETE!! "
                log_string += str(bytearray(sv_dsm_buffers[row[1]]))
                dsm_id = (sv_dsm_buffers[row[1]][0] & 0xF0) >> 4
                block_id = sv_dsm_buffers[row[1]][0] & 0x0F
                if dsm_id not in dsm_messages:
                    dsm_messages[dsm_id] = DSMMessage(dsm_id)
                dsm_messages[dsm_id].addBlock(block_id, sv_dsm_buffers[row[1]][1:])
                sv_dsm_buffers[row[1]] = []
                page_counters[row[1]] = 0
            else:
                page_counters[row[1]] += 1

            log_string += " page_counters["+row[1]+"]= " + str(page_counters[row[1]])
            
            logging.debug(log_string)
            hkroot_sequence += hex(hkroot_byte) + ","
logging.debug("HKROOT Stream for SVID 27: " + hkroot_sequence)
logging.info (str(dsm_messages))