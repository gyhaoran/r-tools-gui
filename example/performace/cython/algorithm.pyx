def fast_sum(int[:] arr):
    cdef long long i, total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
    