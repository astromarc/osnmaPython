#HMAC bruteforce tester
import hmac
import binascii

#Usage: call with a file of keys in text format (one key per line) and data in binary format
def brute_hmac(keyfile, data):
    with open(keyfile) as kf:
        for line in kf:
            key_str = line.strip()[2:-1]
            key_bin = binascii.unhexlify(key_str)
            tag_bin = hmac.digest(key_bin, data, 'sha256')
            tag_str = binascii.hexlify(tag_bin)
            print('Trying key: ' + key_str + " Tag: " +  str(tag_str))

testdata = bytearray([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
#Example call
brute_hmac('../test_data/data_mataro3.key', testdata)