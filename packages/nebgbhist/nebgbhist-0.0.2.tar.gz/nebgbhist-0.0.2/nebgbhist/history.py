#! /usr/bin/env python

import glob
import optparse as op
import os
import subprocess as sp
import sys

__usage__ = '%prog [-h] [-d DIR]'

def do_history(gb1, gb2=None):
    sys.stderr.write("DIFF: %s %s\n" % (gb1, gb2))
    command = ['neb-gbdiff', gb1]
    if gb2 is not None:
        command.append(gb2)
    sp.check_call(command)

def generate_history(dir):
    fnames = glob.glob(os.path.join(dir, "*.gbk"))
    fnames.sort()
    if len(fnames):
        do_history(fnames[0])
    for i in range(1, len(fnames)):
        do_history(fnames[i-1], fnames[i])

def options():
    return [
        op.make_option('-d', '--dir', dest='dir', default='./',
            help="Directory containing a history of Genbank files."),
    ]

def main():
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()

    if len(args):
        parser.error("Unknown arguments: %s" % ' '.join(args))

    generate_history(opts.dir)

if __name__ == '__main__':
    try:
        main()
    except IOError, inst:
        # ignore BrokenPipe errors
        if inst.errno not in [32]:
            raise
    except KeyboardInterrupt:
        pass

