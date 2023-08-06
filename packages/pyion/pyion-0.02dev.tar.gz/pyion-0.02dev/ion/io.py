# NumPy + SciPy can be tricky to compile on ubuntu, so don't require numpy 1.10,
# allow use of old numpy (1.02); provide the fromregex() function that
# we want in either case.

try:
    from numpy import fromregex as array_fromregex
except ImportError:
    import numpy as np
    import re
    #Ganked from numpy 1.10
    def array_fromregex (file, regexp, dtype):
        """
        Construct an array from a text file, using regular-expressions parsing.
        
        Array is constructed from all matches of the regular expression
        in the file. Groups in the regular expression are converted to fields.
        
        Parameters
        ----------
        file : str or file
                File name or file object to read.
        regexp : str or regexp
                Regular expression used to parse the file.
                Groups in the regular expression correspond to fields in the dtype.
        dtype : dtype or dtype list
                Dtype for the structured array

        Examples
        --------
        
        >>> f = open ('test.dat', 'w')
        >>> f.write ("1312 foo\\n1534  bar\\n444   qux")
        >>> f.close ()
        >>> np.fromregex ('test.dat', r"(\\d+)\\s+(...)",
        ...              [('num', np.int64), ('key', 'S3')])
        array([(1312L, 'foo'), (1534L, 'bar'), (444L, 'qux')],
                  dtype=[('num', '<i8'), ('key', '|S3')])

        """
        if not hasattr (file, "read"):
            file = open (file,'r')
        if not hasattr (regexp, 'match'):
            regexp = re.compile (regexp)
        if not isinstance (dtype, np.dtype):
            dtype = np.dtype (dtype)

        seq = regexp.findall (file.read ())
        if seq and not isinstance (seq[0], tuple):
            # make sure np.array doesn't interpret strings as binary data
            # by always producing a list of tuples
            seq = [ (x,) for x in seq]
        output = np.array (seq, dtype=dtype)
        return output

def array_toyaml (array, indent = 0):
    """Return (a pretty YAML representation of the array, a dictionary defining data types).
       Handles complex dtypes correctly.
       """
    dtypes = {}
    if not array.dtype.fields:
        return yaml.safe_dump (array), {array.dtype.name : array.dtype, 'Type': array.__class__}
    

def array_fromyaml (input):
    pass

__all__ = ('array_fromregex',)
