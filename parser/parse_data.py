import csv

def parse_nma_hdr(x):
    nmas_str = ["Reserved", "Test", "Operational", "Don't use"]
    cpks_str = ["Reserved", "Nominal", "End Of Chain (EOC)", "Chain Revoked (CREV)", "New Public Key (NPK)", "Public Key Revoked (PKREV)", "Reserved", "Reserved"]
    nmas = (x & 0xC0) >> 6
    chainID = (x & 0x30) >> 4
    cpks = (x & 0x0E) >> 1
    return "NMA HDR: " + nmas_str[nmas] + " | Chain ID: " + str(chainID) + " | CPKS: " + cpks_str[cpks]

page_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]
page_counters = {}

hkroot_sequence = ""

with open('../data_processed_04122021.csv') as csvfile:
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
                if ((hkroot_byte & 0xF0) >> 4) <= 11:
                    log_string += " (DSM-KROOT MESSAGE)"
                else:
                    log_string += " (DSM-PKR MESSAGE)"
            else:
                log_string += "[DSM BLOCK n byte] " + hex(hkroot_byte)
            
            if page_type not in page_types_sequence[page_counters[row[1]]]:
                log_string += " ¡¡ PAGE SEQUENCE BROKEN !! Expected page Type = " + str(page_counters[row[1]])
            
            if page_counters[row[1]] == 14:
                log_string += " ¡¡PAGE SQUENCE COMPLETE!!"
                page_counters[row[1]] = 0
            else:
                page_counters[row[1]] += 1
            
            print (log_string)
            hkroot_sequence += hex(hkroot_byte) + ","
print("HKROOT Stream for SVID 27: " + hkroot_sequence)
