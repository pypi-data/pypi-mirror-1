#! /usr/bin/env python

import os
import optparse as op
import re
import sys
import time
import urllib

from BeautifulSoup import BeautifulSoup
import runfunc as rf

__usage__ = "%prog [-d DIR] ACC1 [ACC2 ...]"

NCBI="http://www.ncbi.nlm.nih.gov"

DATE_FMT = "%b %d %Y %I:%M %p"
FNAME_FMT = "%Y-%m-%d-%H-%m"
HREFRE = re.compile(r"[0-9A-Za-z]+:[0-9A-Za-z]+:[0-9A-Za-z]+")

def fetch_ids(acc):
    url = "%s/entrez/sutils/girevhist.cgi?val=%s" % (NCBI, acc)
    soup = BeautifulSoup(urllib.urlopen(url).read())
    ret = []
    for ln in soup.findAll("a"):
        data = ln["href"].split("?")[-1]
        if not HREFRE.match(data):
            continue
        try:
            date = time.strptime(ln.renderContents(), DATE_FMT)
        except:
            continue
        ret.append((data, date))
    return ret

def fetch(uid, date, path, count=5):
    if count < 1:
        raise RuntimeError("Failed to fetch url: %s" % url)
    url = "%s/sviewer/viewer.fcgi?sendto=on&list_uids=%s"
    gbk = urllib.urlopen(url % (NCBI, uid)).read()
    if len(gbk) < 1024:
        return fetch(uid, date, path, count-1)
    if not os.path.isdir(path):
        os.mkdir(path)
    ext = "ft" if format == "table" else "gbk"
    fname = time.strftime(FNAME_FMT, date) + "." + ext
    fname = os.path.join(path, fname)
    with open(fname, 'wb') as handle:
        handle.write(gbk)


def options():
    return [
        op.make_option('-d', '--dir', dest='dir', default='./'),
    ]

def main():
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.error("No accession provided.")

    if not os.path.exists(opts.dir):
        os.mkdir(opts.dir)
    
    for acc in args:
        for (uid, date) in fetch_ids(acc):
            fetch(uid, date, opts.dir)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
