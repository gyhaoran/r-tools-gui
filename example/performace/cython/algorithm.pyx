def fast_sum(int[:] arr):
    cdef int i, total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
    