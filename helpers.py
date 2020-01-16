# helper functions

# return index where elt should be inserted in sorted list L
# key to generalize search for arbitrary list types
# in practice L is a list of tuples
def binary_search(L, elt, key = lambda x: x):
    # handle edge cases
    if len(L) == 0 or key(L[0]) > key(elt):
        return 0
    if key(L[-1]) < key(elt): # elt goes at end of list
        return len(L)
    low = 0
    high = len(L)-1
    mid = (low+high)//2
    while high - low > 1:
        if key(L[mid]) == key(elt):
            return mid+1 
        if key(L[mid]) < key(elt):
            low = mid
            mid = (low + high)//2
        else:
            high = mid
            mid = (low+high)//2
    if key(L[mid]) <= key(elt):
        return mid+1
    #< L[mid+1][1]:
