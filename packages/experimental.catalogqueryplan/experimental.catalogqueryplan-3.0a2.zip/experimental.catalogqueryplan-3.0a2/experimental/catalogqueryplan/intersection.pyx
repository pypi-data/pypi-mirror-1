DEF SMALLSETSIZE = 1000
DEF BIGSMALLRATIO = 20

from BTrees._IIBTree import intersection as iiintersection
from BTrees._IIBTree import IISet

cpdef object ciiintersection(object o1, object o2):
    if o1 is None:
        return o2
    if o2 is None:
        return o1

    if not o2 or not o1:
        return iiintersection(o1, o2)

    cdef int l1, l2, lb, ls, i
    cdef object small, big, new, ins, has

    if isinstance(o1, int):
        l1 = 1
    else:
        l1 = len(o1)
    if isinstance(o2, int):
        l2 = 1
    else:
        l2 = len(o2)

    if l1 < l2:
        ls = l1
        small = o1
        lb = l2
        big = o2
    else:
        ls = l2
        small = o2
        lb = l1
        big = o1

    if ls < SMALLSETSIZE and lb/ls > BIGSMALLRATIO:
        new = IISet()
        ins = new.insert
        has = big.has_key
        for i in small:
            if has(i):
                ins(i)
        return new
    return iiintersection(o1, o2)
