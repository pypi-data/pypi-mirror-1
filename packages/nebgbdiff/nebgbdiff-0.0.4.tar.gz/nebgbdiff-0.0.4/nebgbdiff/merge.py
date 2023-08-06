
import location

def merge(oldrec, newrec, check_type_change=False):
    matched, todel, toins = _do_merge(oldrec.features, newrec.features)
    if check_type_change:
        m, todel, toins = _do_merge(todel, toins, same_type=False)
        matched.extend(m)
    return matched, todel, toins

def _do_merge(a, b, same_type=True):
    matched, todel, toins = [], [], []
    cmpfun = location.typeordercmp
    if not same_type:
        cmpfun = location.ordercmp
    a.sort(cmp=cmpfun)
    b.sort(cmp=cmpfun)
    ai, bi = 0, 0
    while ai < len(a) and bi < len(b):
        # This clause is for when we have a sequence change
        # and some part of the old sequence was unmappable.
        if a[ai].get("_delete_", False):
            todel.append(a[ai])
            ai += 1
            continue
        res = location.overlapcmp(a[ai], b[bi], same_type=same_type)
        if res < 0:
            todel.append(a[ai])
            ai += 1
        elif res > 0:
            toins.append(b[bi])
            bi += 1
        else:
            matched.append((a[ai], b[bi]))
            ai += 1
            bi += 1
    while ai < len(a):
        todel.append(a[ai])
        ai += 1
    while bi < len(b):
        toins.append(b[bi])
        bi += 1
    return matched, todel, toins