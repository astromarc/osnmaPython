from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba

a = 0x011BA74CE15ACB1B001BDB92AA04C0
b = 0x96ACC108705502AAAAAA78C848BF40
c = int2ba(a,120)[2:114]
d = int2ba(b,120)[2:18]
print((c+d)[6:126])