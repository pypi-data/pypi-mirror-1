#!/usr/bin/env python

import sys

import argparse

import dupfilefind

DEFAULT_VERBOSITY=0
DEFAULT_IGNOREDIRS="_darcs,.svn,.git,.bzr,/proc,/sys,/dev,/tmp,/var/tmp,/lib64/udev"
DEFAULT_HARDLINKEM=False
DEFAULT_MINSIZE=2**10
DEFAULT_MAXSIZE=2**33
DEFAULT_PROFILES=False
DEFAULT_INCLUDE_NAMES_IN_PROFILES=False

READSIZE=8192

if 'cygwin' in sys.platform.lower() or 'win32' in sys.platform.lower() or 'win64' in sys.platform.lower():
    WINDOWS=True
else:
    WINDOWS=False

def main():
    if '-V' in sys.argv or '--version' in sys.argv:
        print "dupfilefind version: ", dupfilefind.__version__
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Find files with identical contents.")
    parser.add_argument("-v", "--verbose", help="Emit more information.", action='append_const', const=None, default=[])
    parser.add_argument("-I", "--ignore-dirs", help="comma-separated list of directories to skip (if you need to name a directory which has a comma in its name then escape that name twice) (this does what you would expect with relative vs. absolute paths) (default %s" % DEFAULT_IGNOREDIRS, action='store', default=DEFAULT_IGNOREDIRS)
    parser.add_argument("-H", "--hard-link-them", help="Whenever a file is found with identical contents to a previously discovered file, replace the new one with a hard link to the old one.  This option is very dangerous because hard links are confusing and dangerous things to have around.", action='store_true')
    parser.add_argument("-D", "--delete-them", help="Whenever a file is found with identical contents to a previously discovered file, delete the new one.  This option is dangerous.", action='store_true')
    parser.add_argument("-m", "--min-size", help="Ignore files smaller than this (default %d)." % DEFAULT_MINSIZE, default=DEFAULT_MINSIZE, type=int, metavar='m')
    parser.add_argument("-M", "--max-size", help="Hash only the first this many bytes of the file (default %d)." % DEFAULT_MAXSIZE, default=DEFAULT_MAXSIZE, type=int, metavar='M')
    parser.add_argument("-p", "--profiles", help="Print out the md5sum and size in bytes of every file.  This could be useful for a p2p storage project to measure how valuable convergent encryption is.", default=DEFAULT_PROFILES, action='store_true')
    parser.add_argument("--include-names-in-profiles", help="Print out the file name in addition to the other information from --profiles, for each file.", default=DEFAULT_INCLUDE_NAMES_IN_PROFILES, action='store_true')
    parser.add_argument("-n", "--no-follow-symlinks", help="Do not follow symlinks.", default=DEFAULT_PROFILES, action='store_true')
    parser.add_argument("dir", nargs='*', help="directories to recursively examine (default '.')", default=".")
    args = parser.parse_args()

    if args.delete_them and args.hard_link_them:
        print "Please choose only one of .--hard-link_them. and '--delete-them'."
        sys.exit(-1)

    if WINDOWS and args.hard_link_them:
        print "Sorry, hard links don't work on Windows."
        sys.exit(-1)

    return dupfilefind.dffem(len(args.verbose), args.ignore_dirs.split(','), args.hard_link_them, args.delete_them, args.min_size, args.max_size, args.profiles, args.include_names_in_profiles, args.no_follow_symlinks, args.dir, WINDOWS)

