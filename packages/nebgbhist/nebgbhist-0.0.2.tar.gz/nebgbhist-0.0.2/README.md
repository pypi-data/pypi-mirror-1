nebgbhist
=========

Tools for building annotation histories from multiple Genbank files.

Example
=======

    $ mkdir gbhist
    $ neb-rev-fetch -d gbhist NC_008512
    $ neb-gbhist -d gbhist | neb-diff-apply NC_008512.git
    $ git --git-dir=NC_008512.git gc --aggressive
    $ neb-validate-history -p NC_008512.git -g gbhist/2009-04-29-04-04.gbk

Playing with files
==================

If you clone the pack repository after building you can poke around at the
contents on the file system. For larger genomes with lots of edits this may run
afoul of directory entry limits until I rewrite the object storage. For the
Carsonella (NC_008512) example I use there isn't an issue.

    $ git clone NC_008512.git
    $ cd NC_008512
    $ ls -1
    *files*

