""" DEPRECATED -- Python 2.6 includes a class for fractions."""
from powers import *
class fixed(object):
    __slots__ = ("scale","value")
    bits_lut = []

    def __init__(self, n, scale = 8):
        int.__init__(n)
        self.scale = scale
        if type(n) == float:
            self.value = n * self.bits_lut[self.scale]
            print self.value
        else:
            if (type(n) == int or type(n) == long):
                self.value = n
            else:
                if type(n) == str:
                    # num/denom
                    #optionally support extended syntax int+fracnum/denom
                    s = n.split("/")
                    self.scale = intToExponent(int(s[1]))
                    self.value = int(s[0])
                else:
                    raise TypeError, "Invalid input to fixed(): %r" % (n,)
        
    def __float__(self):
        return float(self.value) / self.bits_lut[self.scale]

    def __repr__(self):
        return 'fixed("%s")' % (self.__str__(),)

    def __str__(self):
        return "%d/%d" % ( self.value , pow(2,self.scale))

    def __int__(self):
        return self.value >> self.scale

    def __mul__(self,y):
        """Multiply a fixed point value by a fixed point or integer value.
           When multiplying fixed point numbers, calculates in the higher precision of the two operands"""
        if type(y) == type(self):
            ls = abs(y.scale - self.scale)
            
            if y.scale > self.scale:
                rs = y.scale - ls
                return fixed( ( (self.value << ls ) * y.value) >> rs,y.scale)
            
            else:
                rs = self.scale - ls
                return fixed( (self.value * (y.value << ls)) >> rs,self.scale)
            
        else:
            return fixed(self.value * y, self.scale)

    def __rmul__(self,y):
        return self.__mul__(y)

    def __div__(self,y):
        """Divides a fixed-point value by a fixed or integer value.
           Calculates and expresses the result in the higher precision when dividing two fixed-point numbers."""
        if type(y) == type(self):

            ls = abs(y.scale - self.scale)
            if y.scale > self.scale:
                return fixed( ( (self.value << ls) / y.value) << y.scale, y.scale)
            else:
                return fixed( ( self.value / (y.value << ls)) << self.scale, self.scale)
        else:
            return fixed( self.value * y, self.scale)
    

    def __add__(self,y):
        if type(y) == type(self):
            return fixed(self.value.__add__(y.value),self.scale)
        else:
            return fixed(self.value.__add__(y),self.scale)

    def __radd__(self,y):
        return self.__add__(y)
    
    def __sub__(self,y):
        return self.value.__sub__(y)

    def __rsub__(self,y):
        return self.__sub__(y)

    def rescale(self,newscale):
        """Returns a version of this number scaled to a different precision."""
        newscale = int_to_power(newscale)
        if (newscale < self.scale):
            v = self.value >> (self.scale - newscale)
        else:
            v = self.value << (newscale - self.scale)
        return fixed(v, newscale)

#    def __coerce__(self,other):
#        print "coercing"
#        if type(other) == int or type(other) == long:
#            return self,fixed(other,self.scale)



for i in xrange(0,128):
    fixed.bits_lut.append( int( pow( 2,i ) ) )
   
   
a= fixed("1023/64")

# the following line says i cannot perform that operation, though
# i have add implemented. Perhaps coerce is required?
# EDIT: solved -- add needs to handle it.
a= a + 63
print a,a.value,int(a),float(a), a * 2
print 2 + a
print 2 * a
print a * fixed("63/256")
print fixed(" 16/8") / fixed("16/16")

