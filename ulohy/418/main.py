def binary_search(a, x):
    """Binary search algorithm.
    Searches for 'x' in list 'a'.
    Returns index of 'x'."""

    lo = 0
    hi = len(a)

    while lo < hi:
        mid = (lo + hi) // 2
        midval = a[mid]
        if midval < x:
            lo = mid + 1
        elif midval > x:
            hi = mid
        else:
            return mid

    return None


print(binary_search([1, 67, 100], 100))  # 2
print(binary_search([1, 67, 100], 50))  # None
