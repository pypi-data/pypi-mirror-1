
import hashlib
import json
import os
import subprocess as sp

import location

def diff(a, b, workdir):
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    (hasha, hashb, script) = editscript(a, b, workdir)
    if script != {}:
        for f in a.features:
            try:
                location.update_coords(f["location"], script)
            except ValueError, inst:
                f["_delete_"] = True
    return (hasha, hashb, script)

def editscript(a, b, workdir):
    afname = os.path.join(workdir, "a.fa")
    ah = write_fa(a, "a", afname)
    bfname = os.path.join(workdir, "b.fa")
    bh = write_fa(b, "b", bfname)
    if ah == bh:
        return (ah, bh, {})
    combined = hashlib.sha1("%s%s" % (ah, bh)).hexdigest().upper()
    tablefname = os.path.join(workdir, "%s.coords" % combined)
    if os.path.exists(tablefname):
        tabledata = json.load(open(tablefname))
        ret = dict(((a, b), (c, d)) for a, b, c, d in tabledata["coords"])
        return (ah, bh, ret)
    devnull = open("/dev/null", "w")
    command = ["dnadiff", "-p", os.path.join(workdir, "out"), afname, bfname]
    sp.check_call(command, stdout=devnull, stderr=sp.STDOUT)
    coordmap = {}
    onecoords = os.path.join(workdir, "out.1coords")
    with open(onecoords) as handle:
        for line in handle:
            bits = line.split()
            a1, a2 = int(bits[0]), int(bits[1])
            b1, b2 = int(bits[2]), int(bits[3])
            coordmap[(a1, a2)] = (b1, b2)
    snps = os.path.join(workdir, "out.snps")
    with open(snps) as handle:
        ops = []
        for line in handle:
            bits = line.split()
            r, rsub = int(bits[0]), bits[1]
            qsub, q = bits[2], int(bits[3])
            if rsub != "." and qsub != ".":
                # base changes don't affect coordinates
                continue
            ops.append((r, rsub, q, qsub))
        add_snps(coordmap, ops)
    for k, v in coordmap.iteritems():
        if k[1] - k[0] != v[1] - v[0]:
            sys.stderr.write("MISMATCHED COORD TABLE: %r -> %r off by %d" % (
                k, v, abs((v[1] - v[0]) - (k[1] - k[0]))
            ))
    with open(tablefname, "w") as handle:
        coords = [
            [k[0], k[1], v[0], v[1]]
            for k, v in coordmap.iteritems()
        ]
        coords.sort()
        table = {"old": ah, "new": bh, "coords": coords}
        json.dump(table, handle, indent=4)
        handle.write("\n")
    return (ah, bh, coordmap)

def add_snps(coords, ops):
    while len(ops):
        r1, rsub, q1, qsub = ops.pop(0)
        r2, q2 = r1, q1
        while len(ops) and (ops[0][0] == r2 or ops[0][2] == q2):
            curr = ops.pop(0)
            if curr[0] == r2:
                assert curr[1] == rsub, "SNP ref substitution change"
            if curr[2] == q2:
                assert curr[3] == qsub, "SNP query substitution change." 
            r2, q2 = curr[0], curr[2]
        if qsub == '.':
            q2 += 1
            r1, r2 = r1-1, r2+1
        else:
            r2 += 1
            q1, q2 = q1-1, q2+1
        found = False
        for pair in coords:
            if r1 < pair[0] or r1 > pair[1]:
                continue
            dest = coords.pop(pair)
            assert r2 >= pair[0] and r2 <= pair[1], "Invalid SNP ref"
            assert q1 >= dest[0] and q1 <= dest[1], "Invalid SNP query left"
            assert q2 >= dest[0] and q2 <= dest[1], "Invalid SNP query right"
            coords[(pair[0], r1)] = (dest[0], q1)
            coords[(r2, pair[1])] = (q2, dest[1])
            found = True
            break
        assert found, "Failed to find coord pair to split."

def splitspan(a, b, pos, sub):
    if sub == ".":
        if pos == a:
            return None, (a, b)
        if pos == b:
            return (a, b), None
        return (a, pos-1), (pos, b)
    else:
        if pos == a:
            return None, (a+1, b)
        if pos == b:
            return (a, b-1), None
        return (a, pos-1), (pos+1, b)

def write_fa(rec, name, fname):
    sha = hashlib.sha1()
    with open(fname, "wb") as handle:
        handle.write(">%s\n" % name)
        for seq in rec.seqiter:
            seq = seq.upper()
            sha.update(seq)
            handle.write("%s\n" % seq)
    return sha.hexdigest().upper()

