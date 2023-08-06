from iontest import *

class testLimits (IonTestCase):
    def testInt (self):
        """integer dtype limit check"""
        from ion.n import limits
        for code, minv, maxv in (('c', 0, 255), 
                                 ('b', -128, +127), ('B', 0, 255), 
                                 ('h', -32768, +32767), ('H', 0, 65535),
                                 ('i', -2147483648, +2147483647), 
                                 ('I', 0, 4294967295L),
                                 ('q', -9223372036854775808L, 9223372036854775807),
                                 ('Q', 0, 18446744073709551615L),):
            result = limits (code)
            self.assertEqual ((minv, maxv), result)

if __name__ == "__main__":
    main()