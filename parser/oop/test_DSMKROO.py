from dataProcessingOsnma_DSM import DSMMessage
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
from bitarray import bitarray

DSM_Message = DSMMessage(1)
b = hex2ba("2150492104790025D3964DA3A2540A4830D139B710A4951D73C19DA22D3612E32DDC522FD248C7EA8DD271C757A35039F810405BDDE0528FFE261389A1643B879E1BDCB8ADB529333B42D6C387E41EB7DF91AE20889BC37CCE7B86BE3C023AFCD8D6E7C0EDC67D83")

DSM_Message.setDSM(b)


print("Num Blocks",DSM_Message.getNumBlocks())
print(ba2hex(DSM_Message.getPkid()))
print(DSM_Message.getTagSize())

print(ba2hex(DSM_Message.getMACTL()))
print(ba2hex(DSM_Message.getReseved()))
print(ba2hex(DSM_Message.getTOWHk()))
print("WN",ba2hex(DSM_Message.getWNk()))

print(ba2hex(DSM_Message.getAlpha()))
b = bitarray()
b.frombytes(DSM_Message.getKroot())

print(ba2hex(b))

b = bitarray()
b = DSM_Message.getDS()

print(ba2hex(b))

b = bitarray()
b = DSM_Message.getPdk()

print(ba2hex(b))

b = bitarray('01010010')

print(ba2hex(DSM_Message.getM(b)))


M = hex2ba('5250492104790025D3964DA3A2540A4830D139B710A4951D73C19DA22D')

print(ba2hex((M)))

if ba2hex(DSM_Message.getM(b)) == ba2hex((M)):
    print("suu")