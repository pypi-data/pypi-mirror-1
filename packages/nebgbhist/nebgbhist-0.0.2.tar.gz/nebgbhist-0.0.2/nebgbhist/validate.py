#! /usr/bin/env python

import hashlib
import optparse as op
import os

import jsonical
import nebgb
import nebpack

__usage__ = "%prog [-p PACK] [-g GENBANK]"

def jscmp(a, b):
    a = jsonical.dumps(a, indent=4)
    b = jsonical.dumps(b, indent=4)
    if a != b:
        print a
        print b
        return False
    return True

def mkhash(data):
    return hashlib.sha1(data).hexdigest().upper()

def validate(pack, rec):
    if not jscmp(pack.get_keyword("locus"), rec.locus):
        raise ValueError("Keyword 'locus' does not match.")
    for kwname, kwval in rec.keywords.iteritems():
        if kwname == "reference":
            for r in kwval:
                rid = pack.jshash(r)
                pack.get_reference(rid) # raises error on failure
        elif not jscmp(pack.get_keyword(kwname), kwval):
            raise ValueError("Keyword %r does not match.")
    active_ids = pack.active_ids.copy()
    count = 0
    for feat in rec.features:
        count += 1
        if count % 100 == 0:
            print "%d of %d" % (count, len(rec.features))
        props = feat["properties"]
        if "translation" in props:
            props["translation"] = mkhash(props["translation"]) 
        descid = pack.desc_id(feat)
        pf = pack.get_feature(descid)
        pf.pop("deleted", None)
        pf.pop("previous", None)
        if not jscmp(pf, feat):
            raise ValueError("Features don't match.")
        active_ids.pop(descid)
        active_ids.pop(pack.get_feature_id(descid))
    if len(active_ids):
        for aid, aidv in active_ids.iteritems():
            print "%s -> %s" % (aid, aidv)

def options():
    return [
        op.make_option('-p', '--pack', dest='pack', default='genome.pack',
            help="Genome pack to validate."),
        op.make_option('-g', '--gb', dest='gb', default='genome.gb',
            help="Genbank to validate the pack against.")
    ]

def main():
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()
    
    if len(args):
        parser.error("Unknown arguments: %s" % ' '.join(args))

    if not os.path.isdir(opts.pack):
        parser.error("Pack path is not a directory: %s" % opts.pack)
    
    if not os.path.isfile(opts.gb):
        parser.error("Genbank path is not a file: %s" % opts.gb)
    
    pack = nebpack.Pack(opts.pack)
    rec = nebgb.parse_file(opts.gb).next()
    validate(pack, rec)

if __name__ == '__main__':
    main()
