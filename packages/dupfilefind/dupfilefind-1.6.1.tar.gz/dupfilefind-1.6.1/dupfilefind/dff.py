#!/usr/bin/env python

import anydbm, errno, md5, os, stat, struct, sys

from cPickle import dumps, loads

from pyutil import fileutil, mathutil

READSIZE=8192

def md5it(f, MAXSIZE, VERBOSITY=0, PROFILES=False):
    bytesread = 0
    if VERBOSITY > 2:
        print "about to md5 %s" % (f,)

    h = md5.new()
    d = f.read(READSIZE)
    while d:
        h.update(d)
        d = f.read(READSIZE)
        bytesread += len(d)
        if bytesread > MAXSIZE:
            if VERBOSITY:
                hashval = h.hexdigest()
                print "Stopping processing of %s because we've already hashed max-size (%d) bytes of it.  (The result will be %s.)" % (f, MAXSIZE, hashval)
            break

    if VERBOSITY > 2:
        print "finished md5 %s" % (f,)

    return h.hexdigest()

TMPDB1FNAME="dupfilefind1_tmp.db"
TMPDB2FNAME="dupfilefind2_tmp.db"
def dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, MAXSIZE, PROFILES, INCLUDE_NAMES_IN_PROFILES, NOFOLLOWSYMLINKS, DIRS, WINDOWS):
    # on Windows and Cygwin:
    # d1 = { size: [fname]} }
    # d2 = { fname: "1" or "0" } # also for dirs, with "0" for value
    # on other platforms:
    # d1 = { size: [(dev, ino)]} }
    # d2 = { (dev, ino): [fname] or [] } # also for dirs, with empty [fname]

    tempd = fileutil.NamedTemporaryDirectory()
    db1fname = os.path.join(tempd.name, TMPDB1FNAME)
    d1 = anydbm.open(db1fname, "n")
    tempd.register_file(d1)
    fileutil.remove_if_possible(db1fname)
    db2fname = os.path.join(tempd.name, TMPDB2FNAME)
    d2 = anydbm.open(db2fname, "n")
    fileutil.remove_if_possible(db2fname)
    tempd.register_file(d2)
    try:
        return _dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, MAXSIZE, PROFILES, INCLUDE_NAMES_IN_PROFILES, NOFOLLOWSYMLINKS, DIRS, WINDOWS, d1, d2)
    finally:
        tempd.shutdown()

DUMPSEMPTYLIST = dumps([])
def _dffem(VERBOSITY, IGNOREDIRS, HARDLINKEM, DELETEEM, MINSIZE, MAXSIZE, PROFILES, INCLUDE_NAMES_IN_PROFILES, NOFOLLOWSYMLINKS, DIRS, WINDOWS, d1, d2, next_power_of_k=mathutil.next_power_of_k):
    assert not (HARDLINKEM and DELETEEM) # at most one of these

    # First pass: build map from size, dev, inode number to filenames.
    def visit(dirpath, dirnames, fnames, next_power_of_k=next_power_of_k):
        assert os.path.isabs(dirpath), dirpath

        # Make sure we're not recursing and visiting this directory a second time.
        if WINDOWS:
            dirkey = os.path.realpath(dirpath)
            if d2.has_key(dirkey):
                return
            d2[dirkey] = "0"
        else:
            dirstat = os.stat(os.path.realpath(dirpath))
            dirkey = struct.pack("@QQ", dirstat.st_dev, dirstat.st_ino)
            if d2.has_key(dirkey):
                return
            d2[dirkey] = DUMPSEMPTYLIST
            
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
            try:
                fullfname = os.path.realpath(os.path.abspath(os.path.join(dirpath, fname)))
            except EnvironmentError:
                # I got an exception on Mac OS X when calling realpath on /Network/Your-Fablahblah.
                fullfname = os.path.abspath(os.path.join(dirpath, fname))
            if VERBOSITY > 2:
                print "considering file: %s" % fullfname
            try:
                thestat = os.stat(fullfname)
                if stat.S_ISREG(thestat.st_mode) and thestat.st_size >= MINSIZE:
                    d1k = struct.pack("@Q", thestat.st_size)
                    if d1.has_key(d1k):
                        thed1set = loads(d1[d1k])
                    else:
                        thed1set = set()

                    if WINDOWS:
                        thed1set.add(fullfname)
                        d2[fullfname] = "1"
                    else:
                        devino = struct.pack("@QQ", thestat.st_dev, thestat.st_ino)
                        thed1set.add(devino)
                        if d2.has_key(devino):
                            thed2set = loads(d2[devino])
                        else:
                            thed2set = set()
                        thed2set.add(fullfname)
                        d2[devino] = dumps(thed2set)

                    d1[d1k] = dumps(thed1set)
            except EnvironmentError, le:
                if (VERBOSITY > 2) or (VERBOSITY and le.errno != errno.ENOENT):
                    print "note: couldn't stat file named %s because %s" % (fullfname, le)
        for dirname in dirnames:
            fulldirname = os.path.realpath(os.path.abspath(os.path.join(dirpath, dirname)))
            if VERBOSITY > 2:
                print "about to check islink(%s): %s" % (fulldirname, os.path.islink(fulldirname))
            if not NOFOLLOWSYMLINKS and os.path.islink(fulldirname):
                for (idirpath, idirnames, ifnames,) in os.walk(fulldirname):
                    visit(idirpath, idirnames, ifnames)

    if VERBOSITY > 2:
        print "about to visit DIRS %s" % (DIRS,)
    for DIR in DIRS:
        for (dirpath, dirnames, fnames,) in os.walk(DIR):
            visit(os.path.realpath(os.path.abspath(dirpath)), dirnames, fnames)

    # Second pass: for any files which have identical size and different (dev, ino,), md5 that file.  Build map from md5 to { (dev, ino,): [ fname ] }.
    # ... and print out any duplicates (that is: same md5, different (dev, ino,)).

    for (sizestr, thed1setstr,) in d1.iteritems():
        size = struct.unpack("@Q", sizestr)[0]
        thed1set = loads(thed1setstr)
        if VERBOSITY > 2:
            print "considering size class %d" % (size,)
        if (len(thed1set) > 1) or (len(thed1set) == 1 and PROFILES):
            if (VERBOSITY > 2) or (VERBOSITY > 1 and len(thed1set) > 1):
                print "about to compare %d elements of size class %d" % (len(thed1set), size)
            # on Windows and Cygwin -- idx is unique and the length of [ fname ] is always 1:
            # d3 = { k: md5hash, v: { k: idx, v: set( fname ) } }
            # on other platforms:
            # d3 = { k: md5hash, v: { k: devino, v: set( fname ) } }
            d3 = {}
            if WINDOWS:
                idx = 0

            for fname_or_devino in thed1set:
                if VERBOSITY > 2:
                    print "considering %r len(fnames): %s" % (fname_or_devino, len(fnames))
                    md5h = None

                if WINDOWS:
                    fnames = set([fname_or_devino])
                else:
                    fnames = loads(d2[fname_or_devino])

                for fname in fnames:
                    try:
                        md5h = md5it(open(fname, "rb"), MAXSIZE=MAXSIZE, VERBOSITY=VERBOSITY, PROFILES=PROFILES) # Here's the expensive part.
                        break
                    except EnvironmentError, le:
                        print "note: couldn't read file named %s because %s" % (fname, le)

                if md5h is None:
                    print "note: couldn't read any of these (same-inode) files: %s" % (fnames,)
                    break

                if PROFILES:
                    if INCLUDE_NAMES_IN_PROFILES:
                        print "%s:%s:%s" % (fname, md5h, size)
                    else:
                        print "%s:%s" % (md5h, size)

                d4 = d3.setdefault(md5h, {})
                if WINDOWS:
                    devino = idx
                    idx += 1
                else:
                    devino = fname_or_devino
                assert not d4.has_key(devino), (`devino`, `d4`, `size`, `thed1set`,)
                d4[devino] = fnames
                if len(d4) == 2:
                    # The first collision.  Print out the first two.
                    if HARDLINKEM or DELETEEM or PROFILES:
                        d4k,d4v = d4.popitem()
                        onename = d4v.pop()
                        # now put them back
                        d4v.add(onename)
                        d4[d4k] = d4v
                    for (iterdevino, iterfnames) in d4.iteritems():
                        if PROFILES:
                            print "identical; md5: %s, size: %s" % (md5h, size)
                        else:
                            print "md5: %s, size: %s, fnames: %s" % (md5h, size, iterfnames,)
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
                        print "identical; md5: %s, size: %s" % (md5h, size)
                    else:
                        print "md5: %s, size: %s, fnames: %s" % (md5h, size, fnames,)
                    if HARDLINKEM or DELETEEM:
                        for fname in fnames:
                            if fname != onename:
                                os.unlink(fname)
                                if HARDLINKEM:
                                    print "hardlinking %s -> %s" % (fname, onename)
                                    os.link(onename, fname)
                                else:
                                    print "deleting %s (since there is already %s)" % (fname, onename)
