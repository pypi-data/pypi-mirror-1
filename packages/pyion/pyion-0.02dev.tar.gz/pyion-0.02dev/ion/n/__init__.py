"""Common simple mathematical functions"""

def integer_polyval (arr, poly, func):
    """If numpy is available, use it to evaluate the polynomial describing ``func`` at points specified by ``arr``.
       Otherwise, use func to slowly evaluate the function at the given points.
       
       When numpy is available, returns a numpy array or scalar, in the smallest dtype possible. 
       (uint8 .. uint64, or float64)
       Otherwise, returns a list of integers or an integer.
       """
    try:
        import numpy as np
        result = np.polyval (poly, arr)
        result = result.round()
        if type (arr) == int:
            maxv = result
        else:
            maxv = result.max()
        dtype = 'Q'
        if maxv < 0x100:
            dtype = 'B'
        elif maxv < 0x10000:
            dtype = 'H'
        # I thought the following should be ' < 0x100000000'. however, that causes overflow sometimes (?).
        elif maxv <= 0x7fffffff: 
            dtype = 'I'
        elif maxv < 0x7fffffffffffffffL:
            dtype = 'Q'
        else:
            return result
        return result.astype (dtype)
    except ImportError:
        try:
            _ = len (arr)
            return [func(v) for v in arr]
        except TypeError:
            return func (arr)

def arithmetic_series(n):
    """Return the total of the terms 1 + 2 + 3 + 4 +5...n
    
    see ``integer_polyval()`` for info about acceptable kinds of n.
    """
    return integer_polyval (n, [ -1.46488726e-19,   5.00000000e-01,   5.00000000e-01, 1.03455022e-11],
                               lambda v: sum(xrange(1,v+1)))

def arithmetic_permutations(n):
    """Return the number of possible ways to arrange numbers 1..n in a sequence
       of n elements"""
    return integer_polyval (n, [  5.00000000e-01,  -1.84464202e-15,  -5.00000000e-01, -3.35227319e-09],
                               lambda v: sum([arithmetic_series(i) for i in range(1,n)]))

def round_to_nearestpower (num, base = 2):
    """Round up to the nearest power of ``base``.

       Parameters
       ----------
       num: scalar or array-like
       base: integer
             logarithm base
            
       Returns
       -------
       exp: integer or array-like
            base**exp == num.
    
    """
    return 2 ** round (int_to_exponent (num, base = base) + .5)

def int_to_exponent (num, base = 2):
    """Converts a power of `base` to its exponent.
       for example, int_to_exponent (256) == 8, because 2**8 == 256.
       
       Parameters
       ----------
       num: scalar or array-like
       base: integer
             logarithm base
            
       Returns
       -------
       exp: float or array-like
            base**exp == num.
    
       Notes
       -----
       Designed to reduce data footprint for logarithmic data; if maxval == 7 (2**(7+1)),
       that takes only 3 bits to store compared to the original 8 bits.
       
       For binary or base 10, numpy.log2/log10() are faster.
       
       From an array-like input, an array will be returned when possible. When numpy
       is not available, a list will be returned instead.
       
    """
    try:
        import numpy as np
        return np.emath.logn (base, num)
    except ImportError:
        from math import log
        try:
            _ = len (num)
            return [log (v, base) for v in num]
        except:
            return log (num, base)

def limits (kind):
    """Return minimum and maximum value of the specified data type.

    Parameters
    ----------    
    kind: python type, struct code, numpy dtype code, or numpy scalar dtype.
          python types supported: ``int`` , ``float``
          struct codes supported: one of the characters in ``'cbBhHiIlLqQfd'``
          dtype code: any code resolving to a scalar dtype
                      (eg 'f', 'D', 'F', 'g', 'G', 'u1','u2','u4','u8')
          scalar dtype: any but '?' (boolean)
    
    Returns
    -------
    minval: integer or float
    maxval: integer or float
    
    Notes
    -----
    If you want to get the limits of the 'd' NumPy data type, you will           
    need to pass ``numpy.dtype('d')``. This is because Python's and 
    NumPy's notion of doubles conflict.
    
    In the case of 'complex' kind of dtype (one of 'DFG'), 
    the precision of the basic dtype is returned.
    eg. 'F' type is 64bit, made up of 2 'f' parts, 
    so the precision of the 32bit 'f' parts is returned.
    
    Results for floating point data kinds may be 
    more accurate when NumPy is available.
    
    Examples
    --------
    >>> import numpy as np
    >>> dt = np.dtype ([('named', 'f'), ('fields', 'f')])
    >>> limits (dt)
    Traceback (most recent call last):
    ...
    ValueError: composite dtypes not supported
    """
    import string
    try:
        import numpy as np
    except ImportError:
        np = None
    if type (kind) == str and len (kind) == 1:
        if kind in 'cbBhHiIlLqQfd':
            if kind in 'cfd':
                if kind == 'c':
                    return 0,255
                elif kind == 'f':
                    if np:
                        info = np.finfo (kind)
                        return (info.max, info.min)
                    return (-3.40282346638528859812e+38, 
                            3.40282346638528859812e+38)
                elif kind == 'd':
                    if np:
                        info = np.finfo ('f8')
                        return (info.max, info.min)
                    return (-1.797693134862315708145274237317e+308, 
                            1.797693134862315708145274237317e+308)
            else:
                import struct
                bits = struct.calcsize(kind) * 8
                if kind in string.ascii_lowercase:
                    bits -= 1 
                    maxv = (2 ** bits) - 1
                    return -(maxv + 1), maxv
                return 0, (2 ** bits) - 1
        elif kind in 'DFgG':
            if np:
                info = np.finfo (kind)
                return (info.max, info.min)
            raise ValueError ('code %r is only available when NumPy is available' % kind)
    else:
        if np:
            dtype = np.dtype (kind)
            bits = dtype.itemsize * 8
            if dtype.kind == 'i':
                bits -= 1
                maxv = (2 ** bits) - 1
                return -(maxv + 1), maxv
            if dtype.kind == 'u':
                return 0, (2 ** bits) - 1
            try:
                info = np.finfo (kind)
            except ValueError:
                raise ValueError ('composite dtypes not supported')
            return info.min, info.max
    raise ValueError ('dtype not understood')

def common_denominator (src, dest):
    """ Find a common denominator between two numbers.

    Parameters
    ----------
    src : {integer, float}
           Must be <= dest
    dest : {integer, float}

    Returns
    -------
    common : {integer, float, None}
           src * n where n is an integer,
           such that common / dest is also an integer.
           After 256 iterations without success, bails out, returning None.

    Examples
    --------

    >>> common_denominator (6, 48)
    48

    thus, the second term can be expressed as 48/48, and the first as 6/48
    ; or as 8/8 and 1/8.
    
    """
    i = 1
    while i < 256:
        if (i * src) % dest == 0:
            return i * src
        i += 1
    return None

def factorial (value):
    """Return the factorial of an integer.

    Parameters
    ----------
    value: integer

    Returns
    -------
    factorial: {integer, long}
               Product of all the terms in the series
               N *  N - 1  *  N - 2 ... * 1 
    """
    i = 1
    curvalue = 1
    while i <= value:
        curvalue *= i
        i += 1
    return curvalue

def npermutations_new (nsamples, nitems):
    if (nitems < 1) or (nsamples < 0) or (nsamples > nitems):
        raise ValueError ('nitems out of range')
    return factorial (nitems) / factorial (nitems - nsamples)
    
    
def divisors (value):
    """Return all values that divide exactly into a target value.

    Parameters
    ----------
    value: integer

    Returns
    -------
    divisors: list of integers
              All integers less than ``value`` which divide into ``value``
              with no remainder.           
    """
    return [v for v in range (1, (value + 2) / 2) if (value % v) == 0]

import math
golden = golden_ratio = (1 + math.sqrt(5)) / 2
from math import pi

def subdivisions (length):
    """Return count of 'gaps between entries' for a given number of entries.

    Parameters
    ----------
    length: integer
            Number of entries

    Returns
    -------
    subdivisions: integer
            Number of gaps between entries.
            If the ends count as gaps, add 2 to this.
    """
    return length - 1

def interplog_factor (factor = .5, base = 2):
    """
    
    Parameters
    ----------
    factor: float
            interpolation factor between successive integers N**base
    base: integer
          logarithm base

    Returns
    -------
    logfactor: float
            factor converted to a logarithmic offset

    Examples
    --------
    
    You can produce the series 1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128,...
    from this factor by creating a interleaved sequence 0, 0+f, 1, 1+f, 2, 2+f, 3, 3+f...
    and raising 2 to the power of it
    >>> interplog_factor ()
    0.5849625007211563
    
    Using a single factor to describe such a scale allows space-saving comparable to 
    int_to_exponent. 
    """
    import math
    ifactor = 1.0 - factor
    logfactor = math.log(((base ** 1) * ifactor) + ((base ** 2) * factor), base) - 1.0
    return logfactor
