#!/usr/bin/env python

import md5, os, stat

READSIZE=8192

def dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE):
    assert not (HARDLINKEM and DELETEEM) # at most one of these
    # d1 = { k: size, v: { k: (dev, ino,), v: [ fname ] } }
    d1 = {}

    visiteddirs = set() # to avoid symlink recursion

    def md5it(f):
        h = md5.new()
        d = f.read(READSIZE)
        while d:
            h.update(d)
            d = f.read(READSIZE)
        return h.hexdigest()

    # First pass: build map from size, dev, inode number to filenames.
    def visit(dirpath, dirnames, fnames):
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
                    l = d2.setdefault((thestat.st_dev, thestat.st_ino,), [])
                    l.append(fullfname)
            except:
                if VERBOSITY:
                    print "note: couldn't stat file named %s" % (fullfname,)
        for dirname in dirnames:
            if VERBOSITY > 2:
                print "about to check islink(%s): %s" % (dirname, os.path.islink(dirname),)
            if os.path.islink(dirname):
                for (idirpath, idirnames, ifnames,) in os.walk(dirname):
                    visit(idirpath, idirnames, ifnames)

    for (dirpath, dirnames, fnames,) in os.walk("."):
        visit(dirpath, dirnames, fnames)

    # Second pass: for any files which have identical size and different (dev, ino,), md5 that file.  Build map from md5 to { (dev, ino,): [ fname ] }.
    # ... and print out any collisions (that is: same md5, different (dev, ino,)).

    # d3 = { k: md5hash, v: { k: (dev, ino,), v: [ fname ] } }
    d3 = {}

    for (size, d2,) in d1.iteritems():
        if len(d2) > 1:
            if VERBOSITY:
                print "files with same sizes.  size: %s, fnames: %s" % (size, d2,)
            for ((dev, ino,), fnames,) in d2.iteritems():
                md5h = None
                for fname in fnames:
                    try:
                        md5h = md5it(open(fname, "r")) # Here's the expensive part.
                        break
                    except:
                        print "note: couldn't read file named %s" % (fname,)
                        raise

                if md5h is None and len(fnames) > 1:
                    print "note: couldn't read any of these (same-inode) files: %s" % (fnames,)
                    break

                d4 = d3.setdefault(md5h, {})
                assert not d4.has_key((dev, ino,))
                d4[(dev, ino,)] = fnames
                if len(d4) == 2:
                    # The first collision.  Print out the first two.
                    if HARDLINKEM or DELETEEM:
                        onename = d4.items()[0][1][0]
                    for ((iterdev, iterino,), iterfnames,) in d4.iteritems():
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
