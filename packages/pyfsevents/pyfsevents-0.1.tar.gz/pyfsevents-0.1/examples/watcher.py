"""
watcher.py - advanced filesystem watcher

Maintain directory state in memory to be able to detect which file is modified,
created or deleted. Outputs events on stdout.

Copyright 2009 Nicolas Dumazet <nicdumz@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the MIT License.
"""
import os
import pyfsevents

logging = False
logfile = "logs.log"

if logging:
    f = open(logfile, 'w')
    def log(s):
        f.write(s + "\n")
        f.flush()
else:
    def log(s): pass

class directory(object):
    """
    Representing a directory

    * path is the relative path from watched path to this directory
    * files is a dict listing the files in this directory
        - keys are file names
        - values are lstat records
    * dirs is a dict listing the subdirectories
        - key are subdirectories names
        - values are directory objects
    """
    base = ''
    def __init__(self, abspath):
        if not abspath.startswith(directory.base):
            raise ValueError

        relpath = abspath[len(directory.base)+1:]

        self.path = relpath
        self.files = {}
        self.dirs = {}
        self.lstat = os.lstat(abspath)

    def dir(self, relpath):
        """
        Returns the directory contained at the relative path relpath.
        Creates the intermediate directories if necessary.
        """
        if not relpath:
            return self
        l = relpath.split('/')
        ret = self
        while l:
            next = l.pop(0)
            try:
                ret = ret.dirs[next]
            except KeyError:
                d = directory(directory.base + '/' + ret.path + '/' + next)
                log("new directory: '%s/%s'" % (ret.path, next))
                ret.dirs[next] = d
                ret = d
        return ret

    def debug(self, level=0):
        for f, s in self.files.iteritems():
            log("    "*level + "%s (%s)" % (f, s.st_atime))
        for name, d in self.dirs.iteritems():
            log("%s/ (%s):" % (name, d.lstat.st_atime))
            d.debug(level+1)

def watch(basepath):

    def write(key, file):
        s = "%s %s" % (key, file)
        log(s)
        print key, file

    basepath = os.path.realpath(basepath)

    # init directory
    directory.base = basepath

    # create structure
    base = directory(basepath)

    # initial scan
    for root, dirs, files in os.walk(basepath):
        rel = root[len(basepath):] 
        if rel:
            cur = base.dir(rel)
        else:
            cur = base
        for file in files:
            cur.files[file] = os.lstat(root + '/' + file)

    log("after initial scan:")
    base.debug()

    def callback(path, isrec):
        # note: path is slash-terminated

        if isrec:
            raise NotImplementedError

        if not path.startswith(basepath):
            raise RuntimeError

        # remove base, and trailing slash
        relpath = path[len(basepath)+1:-1]

        d = base.dir(relpath)

        oldfiles = d.files.keys()
        olddirs = d.dirs.keys()

        # scan the dir for changes
        for file in os.listdir(path):
            name = path + file
            try:
                newstats = os.lstat(name)
            except OSError:
                #race condition, file is deleted during the scan
                continue

            if os.path.isdir(name):
                try:
                    if d.dirs[file].lstat != newstats:
                        # modified dirs? not meaningful here.
                        # write("modified", name)
                        d.dirs[file].lstat = newstats
                    olddirs.remove(file)
                except KeyError:
                    write("created", name)
                    log("creating dir %s (%s)" % (name, file))
                    try:
                        d.dirs[file] = directory(name)
                    except OSError:
                        log("abort: race, dir already deleted")
                        continue
            else:
                try:
                    if d.files[file] != newstats:
                        write("modified", name)
                    oldfiles.remove(file)
                except KeyError:
                    write("created", name)

                d.files[file] = newstats

        for file in oldfiles:
            write("deleted", path + file)
            del d.files[file]
        for dir in olddirs:
            write("deleted", path + dir)
            del d.dirs[dir]
        base.debug()

    pyfsevents.registerpath(basepath, callback)
    pyfsevents.listen()

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print "    Usage: python watcher.py path"
        sys.exit(-1)

    watch(sys.argv[1])
