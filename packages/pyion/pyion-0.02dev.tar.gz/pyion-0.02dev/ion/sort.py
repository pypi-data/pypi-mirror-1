"""Advanced sorting.

   Use the module like this:
   import ion.sort as sort

   sort.bytemplate ()
   sort.byweighted_template ()
   sort.bycolor_template ()
"""


# templateSort requires gimp -- GimpRGBs have a .luminance() method.
def bycolor_template (template, colors):
    """Sort colors to match template. They must be of equal length.
    
    Currently hardcoded to sort by luminance.
    Returns a new list with the colors in sorted order."""
    return bytemplate (template, colors, lambda v: v.luminance())
    
    #RGB sort:
    #return templateSort2 (template, colors, lambda v: (v.r, v.g, v.b), weights)
    
    #HSL sort
    #def hslsort (v):
    #   tmp = v.to_hsl()
    #   return (tmp.h, tmp.s, tmp.l)
    #return templateSort2 (template, colors, hslsort, weights)
    

def byweighted_template (sequence, key, weight = (1, )):
    """Sort sequence using key (see templateSort2 for details);
       components are weighted by the weight tuple."""
    totalweight = float (sum (weight))
    def key2 (val):     
        return ( reduce ( lambda x, y: x+y, 
                          [weighs * v  for weighs, v in zip (weight, key (val))]
                          )) / totalweight
    seq = list (sequence)
    seq.sort (key = key2)
    return seq

def bytemplate (template, src, key, weight = (1, )):
    """Reorder sequence to closest match template.
    
    Parameters
    ----------
    template: sequence
              Each item must be of a type suitable to pass to ``key()``
    src: sequence
         Must also produce comparable values when items are passed to ``key()``
    key: function
         Must return
    weight: sequence
            each item must contain one or more weights, according to the 
            dimensionality of ``template`` and ``src``,
            indicating how important it is to map each ``src`` value accurately.
            weight can match src in one of three ways:
            weight.shape = (1,NCHANNELS) # a weight for each data channel
            weight.shape = (NITEMS, 1) # a weight for each data item
            weight.shape = (NITEMS, NCHANNELS) # a weighting for each part of 
                           each item
    
    Returns
    -----
    sorted: list
            New list, containing items from ``src`` sorted to match 
            ``template``.
            Each item from ``src`` occurs exactly once in ``sorted``.
    """
    def key2 (v):
        return v[1]
    tempval = [key (v) for v in template]
    src = weightedSort (list (src), key, weight)
    srcval = [key (v) for v in src]
    totalweight = float (sum (weight))
    # make sure that all comparable values in the template get placed first.
    todo = enumerate (tempval) # 
    todo = weightedSort (todo, key2, weight)
    sorted = [None] * len (template)
#    todo.reverse()
    # try to randomize suitability
#    import random
#    todo = random.shuffle (todo)
    for targindex, val in todo:
        closest = None
        diff = 0x7fffffff # 2.147 billion ((2 ^ 31) - 1)
        for i, val2 in enumerate (srcval):
            try:
                thisdiff = reduce ( lambda a, b: a+b, 
                                    [abs ((weighs * v) - (weighs * v2))
                                     for weighs, v, v2 in zip 
                                     (weight, val, val2)])
                thisdiff /= totalweight
            except:
                # only an int
                thisdiff = abs (val2 - val)
            if thisdiff < diff:
                closest = i
                diff = thisdiff
        # closest should always be non-None, now.
        sorted[targindex] = src.pop (closest)
        srcval.pop (closest)
    return sorted
    
