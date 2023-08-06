"""
OHRRPGCE/FF6 style random item selection (percentage probability based)
"""

from ion.n.random import percent
def got_item (info):
    """ Illustrates OHRRPGCE's behaviour giving items after battle.
    XXX make this into an example.
    Pass a tuple (item, item %, rareitem, rareitem %) as the info parameter.
    
    
    Returns
    -------
    item : object
           One of (item, rareitem, -1) (where -1 indicates nothing dropped)
    
    Notes
    -----
    equivalent to::
      
      tmp = chain (((item %, item), (rareitem %, rareitem)))
      if tmp:
        return tmp[-1]
      return -1
    
    """

    if percent (info[1]):
        # rareitem's chance to drop:
        # (100% - item%) * rareitem%
        #
        # eg. item% == 50, rareitem% == 50
        # drop item 25% of the time,
        # rareitem  25% of the time,
        # nothing   50% of the time.
        #
        # with rareitem% == 25:
        #  item     37.5%
        #  rareitem 12.5%
        #  nothing  50%
        #
        if percent ((info[3] * (100 - info[1])) / 100 ):
            return info[2] # rareitem
        else:
            return info[0] # item
    else:
        return -1 # nothing :(
        
    # expressed in weighted sampling:
    #
    # remainder = float (100 - info[1])
    #
    # return weightedSample ((info[0],info[2], -1), (info[1],
    # (remainder / 2.0) * (info[3]/100.0), remainder / 2.0)

    # In more general, weighting is like:
    #     item @ item%
    #     item2 @ remainder
    #     item3 @ i2remainder
    #     item4 @ i3remainder
    #     None  @ allremainder
    #
    # With remainders weighted into the previous remainder space.
    #
    #
    # say, 50% 40% 30% 20%
    #
    # then..
    # 50% chance of 1
    # 20% (40% * 50%) chance of 2
    # 8% (30% * (100% - (50% + 20%))) chance of 3
    # 4.2% chance (20% * (100% - (50% + 20% + 8%)) ) of 4
    # 16.8% chance (20% * (100% - (50% + 20% + 8% + 4.2%)) ) of None
    #
    # to be precise (percentages expressed like 1.00 == 100%)
    #
    # weights = []
    # weights.append (factorlist[0])
    # factorlist.pop(0)
    #
    # for fac in factorlist:
    #     weights.append ((fac / 100.0) * (100.0 - sum(weights)))
    #
    # weights.append (100.0 - sum(weights))
    #
    # examples:
    #
    #
    


# a dictionary mapping number -> name
lut = {
    -1: "Nothing",
    1: "Item",
    2: "RareItem",
}

print '100, 100:'
#give item, never rareitem or nothing:
for i in range (16):
    print lut[ got_item ((1, 100, 2, 100))]


print '\n\n50, 50:'
# give item 50% of the time, rareitem 25% of the time,
# or nothing 25% of the time:
for i in range (32):
    print lut[ got_item ((1, 50, 2, 50))]


print '\n\n75, 33:'
# give item 75% of the time, rareitem 8% of the time,
# or nothing 17% of the time:

for i in range (32):
    print lut[ got_item ((1, 75, 2, 33))]


