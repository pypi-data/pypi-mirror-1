#!/usr/bin/env python

import anydbm, md5, os, stat, struct

from cPickle import dumps, loads

from pyutil import fileutil, mathutil

READSIZE=8192

class WTF(Exception): pass

def md5it(f, VERBOSITY=0):
    bytesread = 0
    if VERBOSITY > 2:
        print "xxxxxx about to md5 %s" % (f,)

    h = md5.new()
    d = f.read(READSIZE)
    while d:
        h.update(d)
        d = f.read(READSIZE)
        bytesread += len(d)
        if bytesread > 10**12:
            raise WTF("this file is just going and going %s" % (f,))

    if VERBOSITY > 2:
        print "xxxxxx finished md5 %s" % (f,)

    return h.hexdigest()

def dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, PROFILES, NOFOLLOWSYMLINKS, DIRS):
    # d1 = { size: {(dev, ino): [fname]} }
    d1 = anydbm.open("dupfilefind_d2", "n")
    try:
        return _dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, PROFILES, NOFOLLOWSYMLINKS, DIRS, d1)
    finally:
        d1.close()
        fileutil.remove_if_possible("dupfilefind_d2")

def _dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, PROFILES, NOFOLLOWSYMLINKS, DIRS, d1, next_multiple=mathutil.next_multiple):
    assert not (HARDLINKEM and DELETEEM) # at most one of these

    visited = set() # to avoid symlink recursion

    # First pass: build map from size, dev, inode number to filenames.
    def visit(dirpath, dirnames, fnames, next_multiple=next_multiple, visited=visited):
        assert os.path.isabs(dirpath), dirpath

        for IGNOREDIR in IGNOREDIRS:
            if os.path.isabs(IGNOREDIR):
                if os.path.dirname(IGNOREDIR) == dirpath:
                    if VERBOSITY > 2:
                        print "ignoring %s because IGNOREDIR was %s and we are in %s" % (os.path.basename(IGNOREDIR), IGNOREDIR, dirpath)
                    IGNOREDIR = os.path.basename(IGNOREDIR)
                else:
                    continue
            if IGNOREDIR in dirnames:
                if VERBOSITY > 2:
                    print "removing ignored dir %s from %s" % (IGNOREDIR, dirnames)
                dirnames.remove(IGNOREDIR)
        for fname in fnames:
            if VERBOSITY > 2:
                print "considering file: %s" % (os.path.join(dirpath, fname),)
            fullfname = os.path.join(dirpath, fname)
            try:
                thestat = os.stat(fullfname)
                if not stat.S_ISLNK(thestat.st_mode) and thestat.st_size >= MINSIZE:
                    d1k = struct.pack("@Q", thestat.st_size)
                    if d1.has_key(d1k):
                        d2 = loads(d1[d1k])
                    else:
                        d2 = {}

                    fnames = d2.get((thestat.st_dev, thestat.st_ino), [])
                    fnames.append(fullfname)
                    d2[(thestat.st_dev, thestat.st_ino)] = fnames
                    d1[d1k] = dumps(d2)
            except EnvironmentError, le:
                if VERBOSITY:
                    print "note: couldn't stat file named %s because %s" % (fullfname, le)
        for dirname in dirnames:
            fulldirname = os.path.join(dirpath, dirname)
            if VERBOSITY > 2:
                print "about to check islink(%s): %s" % (fulldirname, os.path.islink(fulldirname))
            if not NOFOLLOWSYMLINKS and os.path.islink(fulldirname):
                dirdevino = os.stat(fulldirname)[1:2]
                if dirdevino not in visited:
                    visited.add(dirdevino)

                    for (idirpath, idirnames, ifnames,) in os.walk(fulldirname):
                        visit(idirpath, idirnames, ifnames)

    if VERBOSITY > 2:
        print "about to visit DIRS %s" % (DIRS,)
    for DIR in DIRS:
        for (dirpath, dirnames, fnames,) in os.walk(DIR):
            visit(os.path.abspath(dirpath), dirnames, fnames)

    # Second pass: for any files which have identical size and different (dev, ino,), md5 that file.  Build map from md5 to { (dev, ino,): [ fname ] }.
    # ... and print out any duplicates (that is: same md5, different (dev, ino,)).

    for (sizestr, d2str,) in d1.iteritems():
        size = struct.unpack("@Q", sizestr)[0]
        d2 = loads(d2str)
        if VERBOSITY > 2:
            print "considering size class %d" % (size,)
        if (len(d2) > 1) or (len(d2) == 1 and PROFILES):
            if (VERBOSITY > 2) or (VERBOSITY > 1 and len(d2) > 1):
                print "about to compare %d elements of size class %d" % (len(d2), size)
            # d3 = { k: md5hash, v: { k: (dev, ino,), v: [ fname ] } }
            d3 = {}

            for ((dev, ino,), fnames,) in d2.iteritems():
                md5h = None
                for fname in fnames:
                    try:
                        if not os.path.isfile(fname):
                            print "xxxxxx weird.  not os.path.isfile(%s)" % (fname,)
                        try:
                            md5h = md5it(open(fname, "rb"), VERBOSITY=VERBOSITY) # Here's the expensive part.
                        except WTF, le:
                            le.args = tuple(le.args + (os.stat(fname),))
                            raise
                        break
                    except EnvironmentError, le:
                        print "note: couldn't read file named %s because %s" % (fname, le)

                if md5h is None:
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
