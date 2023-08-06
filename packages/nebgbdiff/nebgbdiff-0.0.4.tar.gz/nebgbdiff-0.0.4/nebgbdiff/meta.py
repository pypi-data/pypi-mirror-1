
import hashlib
import json
import os

def diff(oldrec, newrec):
    ret = []
    if oldrec.locus != newrec.locus:
        yield {
            "type": "keyword",
            "keyword": "locus",
            "value": newrec.locus
        }
    for item in diff_kws(oldrec.keywords, newrec.keywords):
        yield item

def diff_kws(oldkw, newkw):
    ret = []
    for o in oldkw:
        if o == "reference":
            for item in diff_refs(oldkw[o], newkw.get(o, [])):
                yield item
        elif o not in newkw:
            yield {"type": "keyword", "keyword": o, "delete": True}
        elif oldkw[o] != newkw[o]:
            yield {"type": "keyword", "keyword": o, "value": newkw[o]}
    for n in newkw:
        if n in oldkw:
            continue
        yield {"type": "keyword", "keyword": n, "value": newkw[n]}

def diff_refs(oldrefs, newrefs):
    itemize = lambda p: (hashlib.sha1(json.dumps(p)).hexdigest().upper(), p)
    oldrefs = dict(map(itemize, oldrefs))
    newrefs = dict(map(itemize, newrefs))
    for o in oldrefs:
        if o not in newrefs:
            yield {"type": "reference", "refid": o, "delete": True}
    for n in newrefs:
        if n not in oldrefs:
            yield {"type": "reference", "refid": n, "value": newrefs[n]}
