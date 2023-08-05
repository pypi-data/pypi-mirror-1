from itertools import repeat
from heapq import *
__all__=[
    'LEVENSHTEIN_DEFAULT_MAXDIST',

    'levenshtein_distance', 'levenshtein_selectone', '_levenshtein_select']

LEVENSHTEIN_DEFAULT_MAXDIST = 3
# this constant is simply used to accelerate distance function startup.
# NOTE: tests with the profile module indicated the advandages of this were 
# marginal at best! Exhaustive tests with large data & input sets are TBD.
_levenshtein_maxwordrange = 0
_levenshtein_firstcol = []
_levenshtein_firstrow = []

def _levenshtein_accomodate_wordlen(wordlenplusone):
    global _levenshtein_maxwordrange, _levenshtein_firstcol, _levenshtein_firstrow
    if wordlenplusone <= _levenshtein_maxwordrange:
        return _levenshtein_firstcol, _levenshtein_firstrow
  
    _levenshtein_firstcol.extend([((i,0),i)
        for i in xrange(_levenshtein_maxwordrange, wordlenplusone)])
    _levenshtein_firstrow.extend([((0,j),j)
        for j in xrange(_levenshtein_maxwordrange, wordlenplusone)])    
    _levenshtein_maxwordrange = wordlenplusone
    return _levenshtein_firstcol, _levenshtein_firstrow


def _levenshtein_prepare_dtab(a,b, dtab=None):
    dtab = dtab or {}
    dtab.clear()
    n,m=len(a), len(b)
    firstcol, firstrow = _levenshtein_accomodate_wordlen(
        max(n, m) + 1)
    dtab.update(firstcol[:n+1])
    dtab.update(firstrow[:m+1])
    return dtab, n, m

def levenshtein_distance(a,b):
    """Levenshtein word distance algorithm.

    a is the target word, b is the candidate. return the minimum edit distance
    from b to a. that is, the minimum number of insertions, deletions and 
    substitutions required to produce a from b.
    
    Picked this implementation of the net. However it is described well in:
        Speech & Langauge Processing: ISBN-X013122798X, Ch 5. pp 154
    
    Abridged from the above reference:
    
    This algorithm measures the 'minimum edit distance' between two 
    strings a,b. med(a,b) is defined as the minimum number of editing 
    operations required to transform one string into another. 
    
    The operations are delete,substitute,insert

    Levenshtein solves this problem using 'dynamic programming', essentialy a
    table driven mechanism for solving a problem a bit at a time and
    accumulating the result. Dynamic programming solutions for sequences in
    general work by creating a distance matrix with one column for each item in
    the target sequence and one row for each item in the source - ie., target
    allong the bottom & source down the side. For computing the minimum edit
    distance, this matrix is then the edit-distance matrix. Each cell
    edit-distance[i,j] contains the distance between the first i characters of
    the target and the first j characters of the source. The value of each 
    cell represents the minimum of the three possible paths through the matrix
    that arrive there.
    """
    c, n, m = _levenshtein_prepare_dtab(a,b)
    #c, n, m = {}, len(a), len(b)
    #c.update([((i,0),i) for i in range(0,n+1)])
    #c.update([((0,j),j) for j in range(0,m+1)])
    for i in range(1,n+1):
        for j in range(1,m+1):
            x = c[i-1,j]+1
            y = c[i,j-1]+1
            if a[i-1] == b[j-1]:
                z = c[i-1,j-1]
            else:
                z = c[i-1,j-1]+1
            c[i,j] = min(x,y,z)
    return c[n,m]

def levenshtein_selectone(asequence, b, 
    dtab=None, maxwordlen = 0, maxdist = LEVENSHTEIN_DEFAULT_MAXDIST):
    maxdist=min(len(b),maxdist)
    if len(asequence) == 1:
        d = levenshtein_distance(asequence[0], b)
        return d < maxdist and (0,d) or (-1,d) 
    state = _levenshtein_select(asequence, b, dtab, maxwordlen, maxdist)
    h=state[1]
    return h[0][0] < maxdist and (h[0][-1], h[0][0]) or (-1, maxdist) # ic,d

# performance tests for this routine, versus calling levenshtein_distance, are
# still TBD. I beleive that theoretical worst case performance is no better than
# levenshtein_distance. small scale tests _did_ show a small advantage. But 
# probably not enough to warant the considerable additional complexity. n'mind
# it was fun to write!
def _levenshtein_select(asequence, 
        b,                  # ignored if state is not None, otherwise  
        dtab = None,        # ignored if state is not None
        maxwordlen = 0,     # ignored if state is not None
        maxdist = LEVENSHTEIN_DEFAULT_MAXDIST, # ignored if state is not None,
        state = None
        ):
    
    b, h, dtabs, maxwordlen, maxdist = state or (
        b, None,None, maxwordlen, maxdist)
    if maxwordlen == 0:
        #assert state is None, "re-entry state must include original maxwordlen"
        asequence.append(b)
        maxwordlen = maxwordlen or reduce(max, map(len, asequence))
        asequence.pop() # pop b
        _levenshtein_accomodate_wordlen(maxwordlen+1)
        
    dtabs = dtabs or [
        [0, 0, c, n] 
        for c, n, m in map(
            _levenshtein_prepare_dtab, asequence, repeat(
                b, len(asequence)), repeat(dtab, len(asequence)))]       
        
    # obviously, m is invariant for all permutaions of 'asequence' with b
    m = len(b)
    #m = not state and m or len(b)
    
    # the purpose of 'h' is to enable efficient selection of an alternate match
    # of b against an item in asequence when the current selection starts to
    # deteriorate.
    #
    # h is a priority queue of the current match score of each item in
    # 'asequence' against 'b'.  it's items are a 3 tuple: (d, m', ic).  d is
    # the 'on diagonal' levenshtein distance of 'asequence[ic]' for m'
    # characters of b.
    # 
    # heapq orders tuple keys lexicaly. h[0][1] = m' = characters of b consumed
    # for the best existing match. hence when h[0][1] = m' = m we know that
    # there are no further matches in the heap with un consumed characters.

    h = h or [(0, 0, i) for i in range(len(asequence))]
    htop = heappop(h)
    irange = range(1, maxwordlen+1)
    jrange = range(1, m+1)
    while htop[0] <= h[0][0] and htop[1] < m:
        ic = htop[-1]
        dstart, (istart, jstart, c, n) = htop[0], dtabs[ic]
        for i in irange[istart:n]:
            # range of j is len(b) and hence is invariant for all in asequence.
            for j in jrange[jstart:]:
                x,y = c[i-1,j]+1, c[i,j-1]+1
                if asequence[ic][i-1] == b[j-1]:
                    z = c[i-1,j-1]
                else:
                    z = c[i-1,j-1]+1
                d = c[i,j] = min(x,y,z)
                if i==n and j == m and d == 0:
                    # * BEST MATCH *, early exit it is not possible to find a
                    # better match.  note, however, if the elements of
                    # 'asequence' are not unique terminating here will ignore
                    # equivelent matches.
                    heappush(h, htop)
                    return (b, h, dtabs, maxwordlen, maxdist)
                if i==j and d > dstart:
                    # for any given word pair the 'on diagonal' distance will
                    # remain constant or deteriorate.
                    #if j < m:
                    #    dtabs[ic][0:2]=[i-1, j]
                    #else:
                    #    dtabs[ic][0:2]=[i, 0]
                    dtabs[ic][0:2] = j < m and [i-1, j] or [i, 0]
                    # because of i==j above 
                    #   i*m+h[q][1] >= i*m+j
                    #   for q[0:len(asequence)] and j[0:i]
                    
                    htop = heapreplace(h, (d, j, htop[-1]))
                    break
            jstart = 0
            if i==j and d > dstart:
                break
        # if we complete a full examination without a deteriation in distance
        # we need to ensure we cycle the heap. note that without this then
        # ['apple','apple','apple'], 'param' will not halt.
        if ic == htop[-1]:
            htop = heapreplace(h, (d, m, htop[-1]))
        if htop[0] > maxdist:
            return (b, h, dtabs, maxwordlen, maxdist)
    # if we get here there are no 0 distance matches and we have full considered
    # all permutations that share the best distance.
    
    # in the case where all matches have equivelent distance we take the first.
    # a side effect of the above is that in this case htop is going to be the
    # last item.
    #
    # this tends to be 'what you'd expect'. there is a cost in herent in 
    # providing this. if it turns out not to be appropriate it will be removed.
    # 
    heappush(h, htop)
    return (b, h, dtabs, maxwordlen, maxdist)

