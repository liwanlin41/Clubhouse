# helper functions

# return index where elt should be inserted in sorted list L
# in practice L is a list of tuples and elt is an id
def binary_search(L, elt):
    # handle edge cases
    if len(L) == 0 or L[0][1] > elt:
        return 0
    if L[-1][1] < elt: # elt goes at end of list
        return len(L)
    low = 0
    high = len(L)-1
    mid = (low+high)//2
    while high - low > 1:
        if L[mid][1] == elt:
            return mid # this shouldn't actually happen in practice
        if L[mid][1] < elt:
            low = mid
            mid = (low + high)//2
        else:
            high = mid
            mid = (low+high)//2
    if L[mid][1] <= elt < L[mid+1][1]:
        return mid+1
