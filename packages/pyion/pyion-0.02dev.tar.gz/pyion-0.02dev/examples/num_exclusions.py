# ab -> ab a b
# abc -> abc ab ac bc a b c
# abcd -> abcd abc abd acd bcd  ab ac ad bc bd cd  a b c d  1 + 6 + 4 + 4 aka subsetfac (4, 6)
# abcde -> abcde abcd abce abde acde bcde 5 + 1 +
#          abc abd abe acd ace ade bcd bce bde cde 10 +
#          ab ac ad ae bc bd be cd ce de 10 +
#          a b c d e  5
#          AKA subsetfac (5, 20) 
# abcdef -> .....
#
# there are always 3 sets of sets of the same size: the class 'a...N' of which there is one,
# the class 'a..N omitting one' of which there are N, and the class 'one of a..N' of which there are N
#
#
# the problem may be considered as a binary number problem, where 00 is excluded
# 
# 2 -> 11 10 01
# 3 -> 111 

import networkx as nx
import random
ids = [chr(97 + v) for v in range(26)]
def lengths (graph, node):
    """Return the lengths of the paths originating at node.
    
    Graph must not be circular.
    """
    successors = graph.successors (node)
    count = 1
    if len (successors) == 0:
        return 1 # just ourself
    for succ in successors:
        count += lengths (graph, succ)
    return count

def check (nramps, nitems):
    graph = nx.DiGraph ()
    for rampn in range (nramps):
        for rampindex in range (nitems):
            for destramp in range (nramps):
                for dest in range (rampindex + 1, nitems):
                    graph.add_edge (ids[(rampn * nitems) +rampindex], ids[(destramp * nitems) + dest])
    count = 0
    for i in range (nramps * nitems):
        l = lengths (graph, ids[i])
        if l > 1: # don't count 1-length paths
            count += l
    print count
#    print graph.edges()

def check2 (size, threshold = 6):
    graph = nx.DiGraph ()
    sorted = [random.randint (0,size * 2) for v in range(size)]
    sorted.sort()
    for index, value in enumerate (sorted):
        nextindex = index
        while nextindex < size and sorted[nextindex] - value < threshold:
            nextindex += 1
        if nextindex == size:
            continue # brightest possible option
        for nindex in range (nextindex, size):
            graph.add_edge (index, nindex)
    count = 0
    for index in range (size):
        count += lengths (graph, index)
    print count
    print len (graph.edges())

def nsubsets (n):
    return (2**n) - 1

print nsubsets (5)
check (4, 4)
for i in range (8):
    check2 (32, 4)
