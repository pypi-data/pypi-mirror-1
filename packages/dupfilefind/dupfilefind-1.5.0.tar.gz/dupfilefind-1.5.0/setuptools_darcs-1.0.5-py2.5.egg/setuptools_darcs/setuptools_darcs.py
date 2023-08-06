import os

def find_files_for_darcs(dirname):
    for pristinedir in ["pristine", "current",]:
        startdir = os.path.join("_darcs", pristinedir)
        if os.path.exists(startdir):
            for (dirpath, dirnames, filenames,) in os.walk(os.path.join(startdir, dirname)):
                startdirplussep = startdir + os.path.sep
                assert dirpath.startswith(startdirplussep) # sanity check
                reldir = dirpath[len(startdirplussep):]
                for filename in filenames:
                    yield(os.path.join(reldir, filename))

            return # we win
