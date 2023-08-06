""" ion toplevel module

    ion includes general routines for common manipulations I use

    Most modules are entirely my own work.

    * maths (randomization, compression) 
    * i/o     
    * data (efficient/easy representations of simple, large scale types,
      such as taglists)

    Some modules have an additional related module -- eg ``n`` -> ``xn``.
    ``x`` modules contain experimental code; API MAY CHANGE AT ANY TIME.

"""

class LengthMismatch (ValueError):
    pass
        
def seqorsingle (value, datatype):
    """Return a sequence of 'scalar's from a scalar or sequence of scalars.
    
    Parameters
    ----------
    v : sequence or scalar
        The distinction is muddied by things like strings, which are
        technically sequences,  but more often treated as scalars.

    datatype : if ``type (v)`` matches this type, it is considered a scalar.
        can be a sequence, eg (int, float)
    
    Returns
    -------
    seq : sequence (or unmatched scalar)
    
    
    XXX could be apropos to numpy.alen / numpy.asarray
    """
    vtype = type (value)
    try:
        _ = datatype.__iter__
        for type in datatype:
            if vtype == type:
                return (value,)
        return value
    except AttributeError:
        if datatype == vtype:
            return (value,)
        return value

def limititer (iter, num = 1):
    """Iterates through the first of the items in an iterable.

    Parameters
    ----------
    iter : iterable
           Typically an infinite iterable without slicability
    num : integer
          the first ``num`` entries of the iterable are iterated
          through before iteration stops.
    """
    assert num > 0
    while num:
        yield iter.next()
        num -= 1

# XXX rename -> squeeze_split
def squeezeSplit (src, sep):
    """Return src splitted by sep and squeezed (removing ''s)"""
    splitted = src.split(sep)
    while '' in splitted:
        splitted.remove ('')
    return splitted

def bin (value):
    """Return the binary representation of the input number, MSB-first.

    Parameters
    ----------
    value : int or long
        Positive number to calculate the representation of

    Returns
    -------
    binstr : string
        A string with one character per bit in ``value``.
        len (bitstr) == min_nbits (value)

    Examples
    --------
    >>> bin (100)
    '1100100'

    >>> bin (0xffffffff)
    '11111111111111111111111111111111'
    
    Notes
    -------
    * Uses ``numpy.binary_repr`` if available (~68x speedup).
    * You should use ``binary_repr`` directly if you need to represent
      negative numbers.
    * Deprecated, will be obsolete in Python 3 vs the builtin ``bin()``
    """
    try:
        import numpy
        return numpy.binary_repr (value)
    except ImportError:
        t = []
        i = 1
        while value > 0:
            t.append (chr (value & 1 + 48))
            value >>= 1
        return ''.join(t)

def piz (v, n):
    """Split a series 
       a, b, c, d, a, b, c, d 
       -> 
       a, a | b, b | c, c | d, d
    
    useful for things such as coordinates:
    def foo(*coords):
        xc, yc = piz (coords, 2)
        # xc, yc are now matching lists of x and y coords

    Where passing them around as 2-tuples would be woefully inefficient, 
    but working with them needs them individualized.

    HMM

    perhaps could be replaced with tuple subclass
    Still, this is useful for other things
    Like separating out RGB channels
    
    """
    if (len (v) % n > 0):
        raise IndexError("piz() input sequence length doesn't match\
         number of fields")
    l = []
    i = 0
    while (i < n):
        l.append(v[i::n])
        i += 1
    return tuple (l)

def read_everything (filename, open = open):
    """Return a string containing the entirety of the file contents."""
    f = open (filename)
    rval = f.read()
    f.close()
    return rval

def read_everyline (filename, open = open):
    """Return a list containing every line in file."""
    f = open (filename)
    rval = f.readlines()
    f.close()
    return rval
    
def cycleiter (iter, startoffset, step = 1):
    """infinite cycling through rotations of a sequence.
    
    Parameters
    ----------
    iter : sequence or iterable
          if ``iter`` doesn't have __len__ attribute,
          it must iterate over the same number of items each time.
    startoffset : integer
    step : integer
          added to ``offset`` each iteration

    Examples
    --------
    
    >>> list (limititer (cycleiter ([0,1,2,3], 1, 1), 5))
    [1, 2, 3, 0], [2, 3, 0, 1], [3, 0, 1, 2], [0, 1, 2, 3]
    """
    try:
        nitems = len (iter)
    except AttributeError:
        nitems = len (list (iter))
        iter = iter.__iter__ ()
    offset = startoffset % nitems
    output = [None] * nitems
    while 1:
        output [:nitems] = foo
        # XXX complete this

# XXX turn this into an iterator with (seq, step, nsteps) parameters.
def cycle (v, n):
    """ cycle v by n steps. 01234 +1 -> 40123; -1 -> 12340"""
    n = n % len(v)
    if n == 0:
        return
    try:
        import numpy
        if issubclass (v.__class__, numpy.ndarray):
            return numpy.append (v[-n:], v[:-n])
        else:
            try:
                return v[-n:] + v[:-n]
            except:
                return cycleiter (v, n)
    except ImportError:
        try:
            return v[-n:] + v[:-n]
        except:
            return cycleiter (v, n)

def min_nbits (num):
    """Calculates the number of bits needed to store an integer or long

    Parameters
    ----------
    num : positive integer
    
    Examples
    --------
    >>> min_nbits ( 255)
    8
    
    >>> min_nbits ( 256)
    9
    
    
    """
    return int (round (notional_nbits (num) + 0.49999999999999))
#    v = 256
#    b = 8

    # bytes
#    while v < n:
#        v <<= 8
#        b += 8

    #bits
#    v >>= 7
#    b -= 7
#    n += 1

def notional_nbits (num):
    """Calculate the notional number of bits needed to store an integer value.

    Parameters
    ----------
    num : positive integer

    Returns
    ----------
    nbits : float
            A measure of bits per sized variable,
            suitable for calculating interface efficiency.

    Examples
    --------
    >>> notional_nbits (4)
    2.3219280948873622
    
    >>> notional_nbits (3)
    2.0
    
    """
    from math import log
    return log (num + 1, 2)

def setattrs (object, **kwargs):
    """Sets attributes on an object from keyword args.
    
    Parameters
    ----------
    object : instance
        An object supporting the specified attributes.
        If an object has a __dict__ attribute 
        (ie. the class is not limited via __slots__ or implemented in C)
        then any attribute may be set on it.
    kwargs : attribute=value pairs, optional
        for each attribute = value pair, set ``object.attribute = value``.
        
        Attribute names should be only valid Python symbol names.
        However, when expanding a dictionary into kwargs like::

          setattrs (obj, **{'spacy attribute': 1})

        it is possible to assign attributes that are only accessible with 
        ``obj.__dict__['attr']`` or ``getattr (obj, 'attr')``.
        This situation can only occur when attributes of ``object`` are freeform
        (ie. it has a __dict__ attribute.)
    
    Examples
    --------
    >>> import numpy as np
    >>> c = np.arange (16)
    >>> setattrs (c,
    ...           shape = (4,4),
    ...           dtype = 'f4')
    >>> c.shape, c.dtype
    ((4, 4), dtype('float32'))
    """
    for key, value in kwargs.items():
        setattr (object, key, value)


# note - the following line confuses IPython.
# it may be inappropriate behaviour for the top level of a package
#__all__ = ('tupled', )
