"""
Random selection.

Summary:
    * OHRRPGCE/FF6 style random item selection (percentage probability based)
    * Weighted sampling of a sequence (choose one element, likelihood
      determined by weights)
    * Box-filling weighted sampling (virtual guarantee that each of
      the entire set of options will be given exactly once before
      repeating)    
    * Dispensing items from a stock. (absolute guarantee that each of
      the entire set of options will be given exactly once before
      repeating)
    * Simple dice roll (as in '2d4' - 2 4sided dice.)
    * Simple throw from origin. V -/+ (random() * W)

"""

# hackery so 'import random' imports the systemwide random, not us.
from __future__ import absolute_import
import sys
selfpath = sys.path.pop(0)
from random import randint, sample, gauss
sys.path.insert (0, selfpath)


#  How to use numpy.random.multinomial to pick from a list according
#  to probability weightings:

import numpy

def choices (probs, size = 1):
    """ For a sequence of length N, along with a probability array of length N,
        return an array of shape SIZE containing random indices 0..N-1
        selected according to the given probabilities.

        If you want actual samples rather than their indices, see samples()
        """
    # take 1 trial 
    tmp = numpy.random.multinomial (1, probs, size)
    # multiply ([0,0,1,0,0] -> [0,0,3,0,0])
    tmp *= range (1, len(probs) + 1)
    # sum ([0,0,3,0,0] -> 3
    return tmp.sum (-1) - 1

def samples (items, probs, size = 1):
    """ Given a probability list totaling to 1.0, and a list of items, return
        1 or more of the items in list, per the probabilities."""
    c = choices (probs, size)
    a = items
    # only adapt it if not already adapted.
    try:
        assert a.dtype == numpy.object_
        a = numpy.array (items, dtype = numpy.object_)
    except:
        pass
    return a.take(c)




# useful for eg. choosing which algo to demonstrate in a demo,
# choosing which item reward to give in an RPG,

def boxfill (seq, status, weights = None):
    """Fill weighted boxes in a roughly even way.
    
    If status is None, it is initialized.
    
    Then...
    
    status is used to inversely weight weights. status is a sequence of matching length to seq.
    Weighting is ((1.0/statusval) * weight)
    Thus, the more times something has been chosen relative to its siblings, 
    the less likely it is to be chosen.
    
    If you pass a status array, it should be filled with integers.

    As a choice falls behind the others in amount-of-times-chosen, its likelihood to be chosen
    approaches infinity (but is never actually infinite. 
    for instance, if choice A has been picked 4million times and choice B has been picked 10 times, there
    is a 1 / 400001 chance of A being picked next.

    Another nice property is the auto-leveling. If the choices weren't made evenly (deliberately, say, 
    like when a type of enemy can only drop one particular item), then you can still even out the 
    spread using this when the option to drop one of several is available.

    Returns an element from seq; Updates status in-place.
    
    See also
    --------
    dispense
    """
    # could optimize this using digitization
    if weights:
        _w = [(1.0 / s) * w for s, w in zip(status, weights)]
    else:
        _w = [1.0 / s for s in status]
    total = sum(_w)

    #elect a partition
    n = randint  (1, total)
    for i in xrange (len (weights)):
        n -= _w[i]
        if n <= 0:
            status[index] += 1
            return seq[i]
    return None

# boxfillIter goes here
class boxfill_iter (object):
    def __init__ (self, seq, status, weights = None, loop = 1):
        # infinite looping is done with loop = inf
        self.seq = seq
        self.status = status
        self.weights = weights
        self.loopcounter = loop

    def __iter__ (self):
        return self
        
    def next (self):
        nextrval = boxfill (self.seq, self.status, self.weights)
        if nextrval == None:
            self.loopcounter -= 1
        if self.loopcounter == 0:
            raise StopIteration()
        return nextrval    


# XXX same as samples (seq, weights)!
def weightedSample (seq, weights):
    """Randomly choose an element from seq according to weights. example:
    seq = ("Red","Green","Blue")
    weights = ( 20, 10, 5)
    weightedsample(seq, weights)

    returns "Red" ~20/35 of the time, "Green" ~10/35 of the time, and "Blue" ~5/35 of the time.
    
    Sorting the choices so the most likely come first will speed things up.
    """
    
    #calculate total
    total = sum (weights)

    #elect a partition
    n = randint (1, total)
    for i in range (len (weights)):
        n -= weights[i]
        if n <= 0:
            return seq[i]

    return None


# 2007-05-17 further optimizations (just fill and empty status, using sample)
# DODO use generator instead
def dispense (contents, status, n = 1):
    """Dispense the contents of a box.
    
    Parameters
    ----------
    contents: sequence
              Collection of items to dispense
    status: list
              Which items have not been dispensed already. 
              If you pass ``status = []`` it will be automatically initialized to all of the contents.
              Status will be modified in-place during calls to ``dispense()``
    num: integer
              Number of items to dispense
    
    Returns
    -------
    items: sequence
           Collection of items dispensed. May include None, when there are
           not enough items remaining in the box to dispense ``num`` items.
    
    Notes
    -----
    Save the contents of ``status`` if you want to persist the state.
    ``contents`` is never modified.

    """
    if len(status) < 1:
        # init
        status.extend(sample (contents, len (contents)))
    realn = min (n, len (status))
    tmp = status[:realn] + ([None] * (n - realn))
    # off with it's head!
    status[:realn] = []
    if len(tmp) == 1:
        return tmp[0]
    return tmp                  

def affinity_sample (items, data, samples = 1):
    """Sampling weighted by affinity.

       Parameters
       ----------
       items: sequence
              Group of 1 or more items which are related, represented as IDs
       data: map
              Intimacy data.
              Keys are item IDs, values are sequences of related item IDs
              All item IDs referenced must have an entry in ``data``.
       samples: integer
              Number of related items to find
            
       Returns
       -------
       sampled: sequence
                sequence of item IDs of length ``samples``
       
       Notes 
       -----
       Good for selecting partially or entirely themed sets.
       
       Sparse matrix might work better here.

       The first sample is picked randomly, if items[] is empty.
       Subsequent samples are required to be related increasingly intimately with the other samples.

       data should hold intimacy data.
        {
          key : (relation, relation, relation),
          key : ...
          ...
        }

        Each relation item should match a key in data.
        They can and should be repeated: for example:

        {
          'gauntlets' : ('small shield', 'buckler','tower shield','leather gloves','leather gloves')
          'leather gloves' : ('small shield', 'buckler','tower shield','gauntlets','gauntlets')
          'buckler' : ('small shield','small shield', 'tower shield', 'tower shield','leather gloves','gauntlets'),
          'small shield' : ('buckler','buckler','tower shield', 'tower shield','leather gloves','gauntlets'),
          'tower shield' : ('buckler','buckler','small shield','small shield','leather gloves','gauntlets'),
        }

        here, you can see the way that shields are more apropos to each other than handwear, though they both are apropos to each other, being armor, and vice versa.

        Normally, intimacy data would be autogenerated from something like:

        {
           'armor': ('buckler','small shield','tower shield', 'leather gloves','gauntlets'),
           'shields': ('buckler','small shield','tower shield'),
           'handwear': ('leather gloves','gauntlets'),
        }
        
        Which suggests the straightforward algorithym of: 'intimacy == number of categories shared' - thus, all armor is apropos at least 1 point, and the contents of the specific categories are apropos 2 or more points.

        (the real data would probably be numeric object ids, for efficiency; this works too, though.)


       Less than samples samples may be returned.
    """

def cumulative_to_simple_weights (factors):
    """ Convert a list of weights in terms of:
        M% chance of A, ((100%-Achance) * N%) chance of B, 
        ((100% - (Achance + Bchance)) * O%)  chance of C, 
        (whatever percentage remains in 100%) chance of Nothing.

        To absolute weights.
        ie. [50.0, 50.0] becomes [50.0, 25.0, 25.0] 
        ( 50% chance of A, 25% chance of B, 25% chance of nothing/ default.)

        Thus, your default option should be the last choice - choices[-1]

        There is not always a chance of Nothing being chosen. If the last factor is 100%, it will
        serve as the default itself, with 0% chance of Nothing.

        Specifying 0% chance for anything is as good as commenting it out. It's perfectly harmless
        and may be useful during testing.
        """
    weights = []; factors = list (factors)
    weights.append (factors.pop (0))
    for fac in factors:
        weights.append ((fac / 100.0) * (100.0 - sum (weights)))
    weights.append (100.0 - sum (weights))
    if weights[-1] <= 0.00000000001:
        weights.pop() # 0% chance is silly.
    return weights


def percent(p):
    """Return True p% of the time,
    
    Parameters
    ----------
    p: integer
       Percentage chance
    
    Returns
    -------
    success: bool
             Whether the percentage roll succeeded
    """
    if randint (1, 100) <= p:
        return True
    else:
        return False
    
def angband_diceroll (d, s):
    """Angband style dice roll - D rolls of an S-sided dice.
    
       angband_diceroll (2,16) averages 17.4
       angband_diceroll (16, 2) averages 24.


       Examples
       --------

       .. plot::

          rolls = [angband_diceroll (3,6) for v in range(100)]
          import matplotlib.pyplot as plt
          plt.plot (range(100), rolls, 'o')
    """
    from numpy.random import randint
    return randint (1, s + 1, d).sum()

def newdiceroll(d, s):
    "Newstyle dice roll"
    return int (gauss ((d + d * s / 2), (d * s) / 5))

## Choice tree goes here:
#
# idea is:
#
#
#  a10.
#  +  |
#  |  +-- b1
#  |  +-- c2 +-- d5
#  |         +-- e2
#  +         +-- f1
#  k10.
#  +  +--- l1
#  |  +--- m1
#  |  +--- n2
#  +
#  t20.
#     +--- u5
#     +--- v1 +-- w1
#             +-- x1
#             +-- y1
#             +-- z1
#
#  numbers show weights.
#  Each iteration picks an option from the current level, then moves
#  to the next level. Iteration terminates when an item has no
#  subitems.
#
#
# The above tree might look like (lispish):
#
# (10, (1, 'b', 2, (5, 'd', 2, 'e', 1, 'f')), 10, (1, 'l', 1, 'm', 2,
# 'n'), 20, (5,'u', 1, (1, 'w', 1, 'x', 1, 'y', 1, 'z')))
#
# You can use this as the governing data for an AI, for instance (if
# you recognize that the opponent is mounting a strikingly effective
# offensive, adapt the weightings to emphasize defense..)
#

#2007-05-22 added ChainIter

# xx use a XDigraph for the above system
# (point, (action, cond, chaincond), point)

def chain (pairs):
    """Iterates over (chance, value) pairs until a trial fails.
    
    Parameters
    ------------
    chain : iterable
        (chance, value), (chance, value), (chance, value)...
        sequence or iterable.
        chances are specified as percentages.
    
       Not to be confused with itertools.chain(), which returns an
       iterator chaining sequences end-to-end
       (a1,a2,a3..alast,b1,b2,b3..blast,..) with no random factor
       involved.

    Examples
    --------

    50% chance of 'bb', 25% chance of 'bb' and 'cc', 25% chance of Nothing::
        for a in chain (((50, 'bb'),(50, 'cc'))):
            #use the value of a here
       
    See also
    --------
    percent
    """
    index = -1
    for chance, value in pairs:
        if percent (chance):
            yield value
        else:
            raise StopIteration()
    
def diceroll (dice, sides):
    """Roll dice infinitely
    
    Parameters
    ----------
    dice: integer
          Number of dice to roll
    sides: integer
          Number of sides on the dice
          
    Returns
    -------
    value,...: integer
          Values in the range [``dice``..``dice*sides``]
    
    Notes
    -----
    Normally used in combination with ``ion.limititer()``
    """
    minval = sides
    maxval = dice * sides
    while 1:
        yield randint (minval, maxval)


def throw (origin, distance):
    """ see also gauss(), normalvariate() which sometimes produce
    values beyond bounds."""
    return randrange (origin - distance, origin + distance)




def plasma_color_gradient (divisions, initcolors, bounds = None):
    """
        Fills in randomish colors between colors A and B in the
        following manner:
    
        A           B
        A     C     B
        A  D  C     B
        A  D  C  E  B
        AE D  C  E  B
        AE DF C  E  B
        AE DF CG E  B
        AE DF CG EH B
        AEIDF CG EH B
        AEIDFJCG EH B
        AEIDFJCGKEH B
        AEIDFJCGKEHLB
        
        Parameters
        ----------
        divisions : integer where size % 2 == 1
        initcolors : array [X][CHANNEL]
        bounds : tuple of tuples, optional
                 Specifies acceptable randomization ranges for each 
                 channel, on the range 0(start) to 1 (end) 
                 
        Examples
        --------
        Limit the randomization of L to central 50%,
        the other channels are completely free.
        >>> plasma_color_gradient (3, [[100,-4,-10], [20,3,98]],
        ...                        ((.25,.75), (0,1), (0, 1)))
                         
    """
    # loop
    # find the first unfilled midpoint
    # fill it
    # check for complete fill -- if so, return.
    pass

__all__ = ('angband_diceroll', 'cumulative_to_simple_weights',
 'affinity_sample', 'boxfill', 'chain', 'diceroll', 'dispense', 'newdiceroll', 
 'percent', 'throw', 'choices', 'samples', 'plasma_color_gradient')

