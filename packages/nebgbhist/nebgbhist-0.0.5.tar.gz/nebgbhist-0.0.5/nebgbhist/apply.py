#! /usr/bin/env python

import sys

import jsonical

import nebpack

def stdin():
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        if not line.strip():
            continue
        try:
            yield jsonical.loads(line)
        except:
            sys.stderr.write("LAST LINE: %r\n" % line)
            raise

def process(pack, data):
    if data.get("type") == "keyword":
        if data.get("delete", False):
            pack.rem_keyword(data["keyword"])
        else:
            pack.add_keyword(data["keyword"], data["value"])
    elif data.get("type") == "reference":
        if data.get("delete", False):
            pack.rem_reference(data["refid"])
        else:
            pack.add_reference(data["refid"], data["value"])
    elif data.get("type") == "seqid":
        pack.add_seqid(data["seqid"].encode('utf-8'))
    elif data.get("type") == "feature":
        if data.get("delete", False):
            pack.rem_feature(data["feature"])
        else:
            desc_id = pack.desc_id(data.get("previous"))
            pack.add_feature(data["feature"], prev=desc_id)
    else:
        raise ValueError("Invalid type: %r" % data.get("type"))

def main():
    if len(sys.argv) != 2:
        print "usage: %s GIT_DIR" % sys.argv[0]
        exit(1)

    pack = nebpack.Pack(sys.argv[1])
    for obj in stdin():
        process(pack, obj)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

