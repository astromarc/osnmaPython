from dataProcessingGalileoFrame_inputDataTransformation import galPages2galParameters
from bitarray import bitarray
import unittest

a = 0x011BA74CE15ACB1B001BDB92AA04C0 #Even
b = 0x96ACC108705502AAAAAA78C848BF40 #Odd

evenPage = int2ba(a,120)
oddPage = int2ba(b,120)

transformer = galPages2galParameters()
evenEvenOdd, evenPagType, wordType, dataK, evenTail, evenGalileo = transformer.processEvenPage(evenPage)
oddEvenOdd, oddPagType, dataJ, osnma, SAR, spare, CRC, reserved2, oddTail, oddGalileo = transformer.processOddPage(oddPage)


if __name__ == "__main__":
    unittest.main()