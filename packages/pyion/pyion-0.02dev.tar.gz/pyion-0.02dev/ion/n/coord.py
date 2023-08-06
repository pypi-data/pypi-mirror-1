""" Manipulation of Cartesian and Polar coordinates """
from math import cos, sin, sqrt, atan

class Grid:
    def __init__(self, width = 16, height = 16,
                 offsetx = 0, offsety = 0):
        self.w = width
        self.h = height
        self.offsetx = offsetx
        self.offsety = offsety

    def snap (self, *coord):
        """Return the specified coordinates snapped to the grid."""
        try:
            result = []
            for i in range (0, len(coord), 2):
                x, y = coord[i:i+2]
                x = ((x - self.offsetx + (self.w / 2 + 1)) / self.w) * self.w 
                y = ((y - self.offsety + (self.h / 2 + 1)) / self.h) * self.h 
                x += self.offsetx
                y += self.offsety
                result.append ((x, y))
            return result
        except TypeError:
            raise TypeError ('coords (%r) are of wrong type' % coords)
    def cell (self, *coord):
        """Return the specified coordinates transformed into cell indices."""
        try:
            result = []
            for i in range (0, len(coord), 2):
                x, y = coord[i:i+2]
                x = (x - self.offsetx) / self.w
                y = (y - self.offsety) / self.h
                result.append ((x, y))
            return result
        except TypeError:
            raise TypeError ('coords (%r) are of wrong type' % (coord,))

    def cellspan (self, *cells):
        """Return slices corresponding to the area of the given cells.
        
        returns (yslice, xslice). 
        """
        result = []
        for cellx, celly in cells:
            x = (cellx * self.w) + self.offsetx
            y = (celly * self.h) + self.offsety
            x2 = x + self.w
            y2 = y + self.h
            result.append ((slice (y, y2), slice (x, x2)))
        return result

        #0..15 == cell 0, 16 ..31 == cell 1

    def cell_full (self, *cells):
        "Return True for each cell where there is some content, else False."
        return [True] * len (cells)

    def __repr__ (self):
        return '%s (%d, %d, %d, %d)' % (self.__class__.__name__,
                                        self.w, self.h,
                                        self.offsetx, self.offsety)


def subdivide (values, n = 1):
    """ Subdivide the array-like 'values'.
        for example
        >>> subdivide ([0, 1])
        [0, 0.5, 1]
        
        Linear subdivision is always available.
        Quadratic (n=2), cubic (n = 3) and
        quintic (n = 5) subdivision is only available if scipy is.
        
        Returns an array-like object (always an array if numpy is available)
    """
    assert len(values) > 1
    finalsize = (len (values) * 2) - 1
    try:
        import numpy
        if n == 1:
            result = numpy.zeros(shape = (finalsize,))
            result[0::2] = values
            result[1::2] = (values[0:-1] + values [1:]) / 2.0
            return result
        else:
            from scipy.interpolate import InterpolatedUnivariateSpline as SPL
            x = list (range (len (values)))
            y = values
            samplepoints = subdivide (x, n = 1)
            spline = SPL (x, y, n = n)
            return spline (samplepoints)
    except:
        assert (n == 1)
        result = [0] * finalsize
        result[0::2] = values
        result[1::2] = [(a + b) / 2.0 \
                        for a, b in zip (values[0:-1], values[1:])]
        return result

def iSpline (x, y, k = 3, check = None):
    """ Sanitized spline-fitting.
    
        Returns a InterpolatedUnivariateSpline, with certain guarantees about generated y-values.
        
        For example, on a segment like:
        [0, 300, 1000, -100, 300, 0, 1000, 50, 0],
        
        where values < 0 show up in the last segment (eg -398.59 at midpoint)
        we can subdivide using 'averageslope' (divide the greater value by the lesser value on each side, average these and add
        it to the lesser value)
        
        in this position, averageslope is ((1000 / 50) + ( 0 / 0 (assumed 0))) / 2, = 10.
        0 + 10 = 10
        
        a bad spot is still present between 50 and 10 (-23), so another averageslope subdiv:
        
        ((50 / 10) + (0 / 0 (assumed 0))) / 2. = 2.5
        10 + 2.5 = 12.5
        
        Solved!
        
        """

def polardistance (r1, t1, r2, t2):
    # per wikipedia 'polar distance'
    return sqrt( r1 ** 2 + r2 ** 2 - 2 * r1 * r2 * cos(t1 - t2) )

#@testing
def cartesian (rad, theta, roundness = 1.0):
    """
       Maps polar coordinates to cartesian in the range [-inf..0..+inf]
       ie. they probably need normalization to be usable as coordinates into an image.
       """
       
    x = rad * cos (theta)
    y = rad * sin (theta)
    return x, y

#@testing
def polar (x, y, roundness = 1.0):
    """Maps cartesian->polar coordinates.
       Expects values in the range [-inf..0..+inf], not [0..+inf].
       """
    # XXX simplify using atan2()
    if (x, y) == (0, 0):
        return (0, 0)
    elif x == 0:
        #
        #   90deg
        #   |
        #   |
        #   +---- 0deg
        #   |
        #   |
        #   -90deg
        #
        theta = -1.5707963267948966 * max (-1, min(y,1))
        return abs(y), theta
    rad = sqrt (x*x + y*y);
    theta = atan (y/x);
    return rad, theta


#
#    x
#   /\
#  /  \
# +----+
#y      z
#
#                                                           r a
# Given that the point o is the centre of the triangle, o = 0, 0 polar
#
# x = 1, 0
# y = 1,
# z = 1,
# a good depiction for color weighting is
#
#      x
#     x.x
#    x...x
#   y..%..z
#  y.......z
# yyyyyyzzzzz
#
# where xyz are the respective colors, . is the resultant color, and %
# is the triangle position of the weighting.
#
# 11x11 triangle
#
# .....x.....
# .....x.....
# ....x-x....
# ....x-x....
# ...x---x...
# ...x---x...
# ..y-----z..
# ..y--o--z.. 
# .y-------z.
# .y-------z.
# yyyyy~zzzzz
#
# 
# (x -> r3.5,a0; y -> r3.5, a240; z -> r3.5, a120 )
_twx = (1.0, 0)
_twy = (1.0, 2.0943951023931953)
_twz = (1.0, 4.1887902047863905)
#            x  yz    y  xz    z  xy 
_twordermap = {0:(1,2), 1:(0,2), 2:(0,1)}

def triangle_weighting (radius, theta, *xyz):
    """Convert polar coords relative to the center of a triangle, to weights.

    Parameters
    ----------
    radius: float
           in range [0.0..1.0]
    theta: float
           angle in radians

    Returns
    ----------
    xweight: float
             represents the weight of the topmost triangle vertex value
    yweight: float
             represents the weight of the leftmost triangle vertex value
    zweight: float
             represents the weight of the rightmost triangle vertex value
    
    Notes
    -----
    Intended for equilateral triangles with line Y->Z along real x axis, and
    X position being at 0 degrees to the triangle center (ie. directly up)
    
    """
    if radius == 0:
        return (1, 1, 1)
    # first, find the point that's furthest.
    disttocorners = [polardistance (radius, theta, r, t) \
                     for r,t in (_twx,_twy,_twz)]
    # for the two others, it's useful to also know their radial distance 
    # (ie distance if the point was on the edge of the triangle)
    raddistance = [polardistance (1.0, theta, r, t) \
                   for r,t in (_twx,_twy,_twz)]
    opposing = disttocorners.index (max (disttocorners))
    close, closest = _twordermap[opposing]
    if raddistance[close] > raddistance[closest]:
        close, closest = closest, close
    muls = [0, 0, 0]
    muls[close] = raddistance[close]
    muls[closest] = raddistance[closest]
    muls[opposing] = (1.0 - radius) * 0.5
    norm = 3.0 / (sum(muls))
    muls = [norm * v for v in muls]
    return muls


# TEST MATERIAL

#g = Grid(16,16,4,4)
#
#for i in [0,8,16,24,32,40,48]:
#    print((i+5,i+5),g.snap(i+1,i+1))

__ALL__ = ('triangle_weighting', 'polar', 'cartesian', 'polardistance', 'Grid')
