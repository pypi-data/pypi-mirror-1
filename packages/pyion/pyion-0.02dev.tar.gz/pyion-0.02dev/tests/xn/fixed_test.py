import unittest
from ion.n.fixed import *
from ion.n.powers import * 
#intToExponent

class KnownValues(unittest.TestCase):
    
    knownvalues = (
        #         value,              fval,          ival
        (   "65535/256",      255.99609375,          255),
        (    "65535/16",     4095.93750000,         4095),
        (     "65535/4",    16383.75000000,        16383),
        (     "65535/2",    32767.50000000,        32767)
    )

    def testFloat(self):
        "convert to float"
        for value,fval,ival in self.knownvalues:
            result = float(fixed(value))
            self.assertAlmostEqual(result, fval, 2)

    def testInt(self):
        "convert to integer"
        for value, fval, ival in self.knownvalues:
            result = int(fixed(value))
            self.assertEqual(result, ival, 2)

    def testUnFloat(self):
        "convert from float"
        for value, fval, ival in self.knownvalues:
            #extract the scale from the value string
            bits = value.find("/")
            bits = value[bits+1:]
            bits = int(bits)
            print bits,fval
            result = str(fixed(fval,intToExponent(bits)))
            self.assertEqual(result, value)

    def testUnInt(self):
        "convert from int"
        for value, fval, ival in self.knownvalues:
            bits = value.find("/")
            bits = value[bits+1:]
            bits = int(bits)
            result = str(fixed(ival,intToExponent(bits)))
            self.assertEqual(result, "%s/%s" % (ival,bits) , 2)


#class Arithmetic(unittest.TestCase):
#    KnownValues = (
#
#    )
#    def testMul(self):
   #testDiv
   #testExtendedSyntax
   #test

if __name__ == "__main__":
    unittest.main()
