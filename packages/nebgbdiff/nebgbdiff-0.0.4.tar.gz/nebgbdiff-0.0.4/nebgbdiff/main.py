#! /usr/bin/env python

import datetime
import hashlib
import optparse as op
import os
import sys

import jsonical
import nebgb

import nebgbdiff.merge as merge
import nebgbdiff.meta as meta
import nebgbdiff.sequence as sequence

__usage__ = "%prog [-w DIR] GenBankFile1 [GenBankFile2]"

def insert(handle):
    rec = nebgb.parse(handle).next()
    hash_translations(rec)
    print mkjs({"type": "keyword", "keyword": "locus", "value": rec.locus})
    for kw in rec.keywords:
        if kw == "reference":
            for ref in rec.keywords[kw]:
                print mkjs({
                    "type": "reference",
                    "refid": mkjshash(ref),
                    "value": ref
                })
        else:
            print mkjs({
                "type": "keyword",
                "keyword": kw,
                "value": rec.keywords[kw]
            })
    seqsha = hashlib.sha1()
    for seq in rec.seqiter:
        seqsha.update(seq.upper())
    print mkjs({"type": "seqid", "seqid": seqsha.hexdigest().upper()})
    for f in rec.features:
        print mkjs({"type": "feature", "feature": f})

def diff(old, new, workdir=".gbdiff"):
    oldrec = nebgb.parse(old).next()
    newrec = nebgb.parse(new).next()
    hash_translations(oldrec, newrec)
    for m in meta.diff(oldrec, newrec):
        print mkjs(m)
    seq_updated = update_features(oldrec, newrec, workdir)
    (matched, todel, toins) = merge.merge(oldrec, newrec, seq_updated)
    for td in todel:
        print mkjs({"type": "feature", "feature": td, "delete": True})
    for m in matched:
        h1, h2 = map(mkjshash, m)
        if h1 != h2:
            print mkjs({
                "type": "feature",
                "feature": m[1],
                "previous": {
                    "type": m[0]["type"],
                    "location": m[0]["location"]
                }
            })
    for ti in toins:
        print mkjs({"type": "feature", "feature": ti})

def hash_translations(*args):
    for a in args:
        for f in a.features:
            props = f["properties"]
            if "translation" not in props:
                continue
            props["translation"] = mkhash(props["translation"]).upper()

def update_features(oldrec, newrec, workdir):
    (old, new, script) = sequence.diff(oldrec, newrec, workdir)
    if old == new:
        return False
    print mkjs({"type": "seqid", "seqid": old})
    script = dict(("%d-%d" % k, "%d-%d" % v) for k, v in script.iteritems())
    print mkjs({"type": "coords", "old": old, "new": new, "coords": script})

def mkjs(data):
    return jsonical.dumps(data)

def mkhash(arg):
    return hashlib.sha1(arg).hexdigest().upper()

def mkjshash(arg):
    return mkhash(mkjs(arg))

def options():
    return [
        op.make_option('-w', '--work', dest='work', default='.gbdiff',
            help='Temporary work directory to use. [default: %default]'),
    ]

def main():
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.error("You must specify at least one GenBank file.")
    
    if len(args) > 2:
        parser.error("Too many GenBank files specified.")

    for fname in args:
        if not os.path.exists(fname):
            parser.error("Unable to find file: %s" % args[0])
   
    if len(args) == 1:
        insert(open(args[0]))
    else:
        diff(open(args[0]), open(args[1]), workdir=opts.work)

if __name__ == '__main__':
    main()
