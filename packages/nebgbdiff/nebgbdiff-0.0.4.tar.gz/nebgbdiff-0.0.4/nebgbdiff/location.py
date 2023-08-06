
def typeordercmp(a, b):
    return ordercmp(a, b, same_type=True)

def ordercmp(a, b, same_type=False):
    if same_type and a["type"] != b["type"]:
        return cmp(a["type"].lower(), b["type"].lower())
    a = a["location"]
    b = b["location"]
    # Reverse strand comes second
    if a["type"] != b["type"] and a["type"] == "complement":
        return 1
    apos, bpos = getpos(a, min), getpos(b, min)
    if apos == bpos:
        return getpos(a, max) - getpos(b, max)
    return apos - bpos

def coordoverlap(x1, y1, x2, y2):
    # TODO: Rewrite this with actual math and not
    # a crappy integer intersection.
    assert x1 <= y1 and x2 <= y2, "Invalid coordinates."
    s1 = set(range(x1, y1+1))
    s2 = set(range(x2, y2+1))
    i = s1.intersection(s2)
    return float(len(i)) / (float(len(s1) + len(s2)) - len(i))

def overlapcmp(a, b, jifactor=0.6, same_type=False):
    if same_type and a["type"] != b["type"]:
        return cmp(a["type"].lower(), b["type"].lower())
    a = a["location"]
    b = b["location"]
    amin, amax = getpos(a, min), getpos(a, max)
    bmin, bmax = getpos(b, min), getpos(b, max)
    res = coordoverlap(amin, amax, bmin, bmax)
    if res < jifactor:
        return amin - bmin
    else:
        return 0

def getpos(loc, op):
    if loc["type"] == "index":
        return loc["position"]
    elif loc["type"] in ["bond", "one-of"]:
        return op(loc["positions"])
    elif loc["type"] == "span":
        return op(loc["from"], loc["to"])
    elif loc["type"] in ["site", "choice"]:
        return op(loc["between"])
    elif loc["type"] == "gap":
        return None
    elif loc["type"] in ["complement", "reference"]:
        return getpos(loc["segment"], op)
    elif loc["type"] in ["join", "order"]:
        pos = map(lambda p: getpos(p, op), loc["segments"])
        pos = filter(lambda p: p is not None, pos)
        return op(pos)
    else:
        raise KeyError("Location %r has no 'type'." % loc)

def update_coords(loc, table):
    if loc["type"] == "index":
        loc["position"] = new_coord(loc["position"], table)
    elif loc["type"] in ["bond", "one-of"]:
        loc["positions"] = map(lambda p: new_coord(p, table), loc["positions"])
    elif loc["type"] == "span":
        loc["from"] = new_coord(loc["from"], table)
        loc["to"] = new_coord(loc["to"], table)
    elif loc["type"] in ["site", "choice"]:
        loc["between"] = map(lambda p: new_coord(p, table), loc["between"])
    elif loc["type"] == "gap":
        pass # Gaps aren't coordinates
    elif loc["type"] in ["complement", "reference"]:
        update_coords(loc["segment"], table)
    elif loc["type"] in ["join", "order"]:
        for seg in loc["segments"]:
            update_coords(seg, table)
    else:
        raise KeyError("Location %r has no 'type'." % loc)

def new_coord(pos, table):
    result = None
    for pair in table:
        if pos < pair[0] or pos > pair[1]:
            continue
        if result != None:
            raise ValueError("Coordinate maps to multiple positions.")
        result = pos - pair[0] + table[pair][0]
    if result == None:
        raise ValueError("Unable to map coordinate: %d" % pos)
    return result
