from iontest import *
from ion import min_nbits, notional_nbits

data = {
 'pow' : ((2, 3), (4, 15), (6, 63), (8, 0xff), (12, 0xfff), (16, 0xffff), 
          (20, 0xfffff), (24, 0xffffff), (28, 0xfffffff), (32, 0xffffffff)),
}
class testPowers (IonTestCase):
    def testStandard (self):
        """min_nbits (*Standard powers of two*) and notional_nbits (*Standard powers of two*)
        """
        for base, value in data['pow']:
            self.assertEqual (min_nbits (value), base)
            self.assertEqual (notional_nbits (value + 1), base)

if __name__ == "__main__":
    main()