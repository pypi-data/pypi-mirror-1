#!/usr/bin/env python

import md5, os, stat

from pyutil import mathutil

READSIZE=8192

def md5it(f):
    h = md5.new()
    d = f.read(READSIZE)
    while d:
        h.update(d)
        d = f.read(READSIZE)
    return h.hexdigest()

def dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, PROFILES, DIRS, next_multiple=mathutil.next_multiple):
    assert not (HARDLINKEM and DELETEEM) # at most one of these
    # d1 = { k: size, v: { k: (dev, ino,), v: [ fname ] } }
    d1 = {}

    visiteddirs = set() # to avoid symlink recursion

    # First pass: build map from size, dev, inode number to filenames, and if PROFILES then print out the first 4 chars of the md5sum and size of each file.
    def visit(dirpath, dirnames, fnames, next_multiple=next_multiple):
        if dirpath in visiteddirs:
            return
        visiteddirs.add(dirpath)
        for IGNOREDIR in IGNOREDIRS:
            if IGNOREDIR in dirnames:
                dirnames.remove(IGNOREDIR)
        for fname in fnames:
            if VERBOSITY > 1:
                print fname
            fullfname = os.path.join(dirpath, fname)
            try:
                thestat = os.stat(fullfname)
                if not stat.S_ISLNK(thestat.st_mode) and thestat.st_size >= MINSIZE:
                    d2 = d1.setdefault(thestat.st_size, {})
                    if d2.has_key((thestat.st_dev, thestat.st_ino,)):
                        l = d2[(thestat.st_dev, thestat.st_ino,)]
                    else:
                        l = []
                        d2[(thestat.st_dev, thestat.st_ino,)] = l
                    l.append(fullfname)
            except EnvironmentError, le:
                if VERBOSITY:
                    print "note: couldn't stat file named %s because %s" % (fullfname, le)
        for dirname in dirnames:
            if VERBOSITY > 2:
                print "about to check islink(%s): %s" % (dirname, os.path.islink(dirname),)
            if os.path.islink(dirname):
                for (idirpath, idirnames, ifnames,) in os.walk(dirname):
                    visit(idirpath, idirnames, ifnames)

    for DIR in DIRS:
        for (dirpath, dirnames, fnames,) in os.walk(DIR):
            visit(dirpath, dirnames, fnames)

    # Second pass: for any files which have identical size and different (dev, ino,), md5 that file.  Build map from md5 to { (dev, ino,): [ fname ] }.
    # ... and print out any collisions (that is: same md5, different (dev, ino,)).

    # d3 = { k: md5hash, v: { k: (dev, ino,), v: [ fname ] } }
    d3 = {}

    for (size, d2,) in d1.iteritems():
        if (len(d2) > 1) or (len(d2) == 1 and PROFILES):
            if VERBOSITY:
                print "files with same sizes.  size: %s, fnames: %s" % (size, d2,)
            for ((dev, ino,), fnames,) in d2.iteritems():
                md5h = None
                for fname in fnames:
                    try:
                        md5h = md5it(open(fname, "rb")) # Here's the expensive part.
                        break
                    except EnvironmentError, le:
                        print "note: couldn't read file named %s because %s" % (fname, le)

                if md5h is None and len(fnames) > 1:
                    print "note: couldn't read any of these (same-inode) files: %s" % (fnames,)
                    break

                if PROFILES:
                    print "%s:%s" % (md5h[:4], next_multiple(size, 4096))

                d4 = d3.setdefault(md5h, {})
                assert not d4.has_key((dev, ino,))
                d4[(dev, ino,)] = fnames
                if len(d4) == 2:
                    # The first collision.  Print out the first two.
                    if HARDLINKEM or DELETEEM or PROFILES:
                        onename = d4.items()[0][1][0]
                    for ((iterdev, iterino,), iterfnames,) in d4.iteritems():
                        if PROFILES:
                            print "identical; md5: %s, dev: %s, ino: %s, size: %s" % (md5h[:4], iterdev, iterino, next_multiple(size, 4096),)
                        else:
                            print "md5: %s, dev: %s, ino: %s, size: %s, fnames: %s" % (md5h, iterdev, iterino, size, iterfnames,)
                        if HARDLINKEM or DELETEEM:
                            for fname in iterfnames:
                                if fname != onename:
                                    os.unlink(fname)
                                    if HARDLINKEM:
                                        print "hardlinking %s -> %s" % (fname, onename)
                                        os.link(onename, fname)
                                    else:
                                        print "deleting %s (since there is already %s)" % (fname, onename)
                elif len(d4) > 2:
                    # More collisions.  Print out the new one.
                    if PROFILES:
                        print "identical; md5: %s, dev: %s, ino: %s, size: %s" % (md5h[:4], dev, ino, next_multiple(size, 4096),)
                    else:
                        print "md5: %s, dev: %s, ino: %s, size: %s, fnames: %s" % (md5h, dev, ino, size, fnames,)
                    if HARDLINKEM or DELETEEM:
                        for fname in fnames:
                            if fname != onename:
                                os.unlink(fname)
                                if HARDLINKEM:
                                    print "hardlinking %s -> %s" % (fname, onename)
                                    os.link(onename, fname)
                                else:
                                    print "deleting %s (since there is already %s)" % (fname, onename)
