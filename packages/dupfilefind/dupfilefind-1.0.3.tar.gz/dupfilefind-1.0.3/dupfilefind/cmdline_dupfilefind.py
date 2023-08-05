#!/usr/bin/env python

import sys

import argparse

import dupfilefind

DEFAULT_VERBOSITY=0
DEFAULT_IGNOREDIRS="_darcs,.svn"
DEFAULT_HARDLINKEM=False
DEFAULT_MINSIZE=2**10

READSIZE=8192

def main():
    if '-V' in sys.argv or '--version' in sys.argv:
        print "dupfilefind version: ", dupfilefind.__version__
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Find files with identical contents.")
    parser.add_argument("-v", "--verbose", help="Emit more information.", action='append_const', const=None, default=[])
    parser.add_argument("-I", "--ignore-dirs", help="comma-separated list of directories to skip (if you need to name a directory which has a comma in its name then escape that command twice) (default %s" % DEFAULT_IGNOREDIRS, action='store', default=DEFAULT_IGNOREDIRS)
    parser.add_argument("-H", "--hard-link-them", help="Whenever a file is found with identical contents to a previously discovered file, replace the new one with a hard link to the old one.  This option is very dangerous because hard links are confusing and dangerous things to have around.", action='store_true')
    parser.add_argument("-D", "--delete-them", help="Whenever a file is found with identical contents to a previously discovered file, delete the new one.  This option is dangerous.", action='store_true')
    parser.add_argument("-m", "--min-size", help="Ignore files smaller than this (default %d)." % DEFAULT_MINSIZE, default=DEFAULT_MINSIZE, type=int, metavar='M')
    args = parser.parse_args()

    if args.delete_them and args.hard_link_them:
        print "Please choose only one of .--hard-link_them. and '--delete-them'."
        sys.exit(-1)

    return dupfilefind.dffem(len(args.verbose), args.ignore_dirs, args.hard_link_them, args.delete_them, args.min_size)

