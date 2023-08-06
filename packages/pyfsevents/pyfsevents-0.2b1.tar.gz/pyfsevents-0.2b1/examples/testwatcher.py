"""
testwatcher.py - stresstest for watcher.py

Spawns a watcher watching a temporary directory, and generates randomly events
in that directory (create/modifiy/delete files). Checks each time
the correctness of watcher's output.

Copyright 2009 Nicolas Dumazet <nicdumz@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the MIT License.
"""
import os
import random
import signal
import string
import subprocess
import tempfile
import time
import watcher

def genname():
    "generates a random 5-letters long name"
    name = ''
    for i in range(5):
        name += random.choice(string.letters)
    return name

def unlink(path):
    "rm -rf path"
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    try:
        os.rmdir(path)
    except OSError:
        pass

class Tester(object):
    def __init__(self, child):
        # simple structure to mirror the state of current directory:
        # keys: pathnames
        # values: if file, True; if directory: a dict representing the subdir
        self.curdir = {}

        # contains the list of parent directories, up to the test root
        self.parentdirs = []

        self.child = child

        # do not let a modify event happen twice in the
        # same epoch second since atime lstat is in second: we would miss an
        # event
        self.lastmodifyevent = None

    def compare(self, key, path):
        "Compare child output against expected output"
        print key, path
        line = self.child.stdout.readline().strip()
        try:
            assert line == key + ' ' + path
        except AssertionError:
            print "wrong line:"
            print line
            raise


    # events
    # all the following methods return True when event was performed
    # and False if it was not possible to do such an event in the context

    def create(self):
        "creae a file in current directory"
        name = genname()
        path = os.getcwd() + "/" + name
        if os.path.exists(path):
            return False
        open(path, 'w+')
        self.curdir[name] = True
        self.compare("created", path)
        return True

    def modify(self):
        "modify a file in current directory"
        if not self.curdir:
            return False
        name = random.choice(self.curdir.keys())
        if os.path.isdir(name):
            return False
        if self.lastmodifyevent and time.time() - self.lastmodifyevent < 1:
            time.sleep(1)
        self.lastmodifyevent = time.time()
        fd = open(name, 'w+')
        fd.write('x')
        fd.close()
        self.compare("modified", os.getcwd() + "/" + name)
        return True

    def delete(self):
        "delete a file in current directory"
        if not self.curdir:
            return False
        name = random.choice(self.curdir.keys())
        full = os.path.join(os.getcwd(), name)
        if os.path.isdir(name):
            if self.curdir[name]:
                os.chdir(name)
                self.parentdirs.append(self.curdir)
                self.curdir = self.curdir[name]
                self.delete()
                return True
            else:
                os.rmdir(full)
        else:
            os.remove(name)

        del self.curdir[name]
        self.compare("deleted", full)
        return True

    def down(self):
        "create a directory, and cd to it"
        if len(self.parentdirs) > 5:
            return self.up()
        name = genname()
        if name in self.curdir:
            return False
        self.parentdirs.append(self.curdir)
        self.curdir[name] = {}
        self.curdir = self.curdir[name]
        os.mkdir(name)
        self.compare("created", os.path.join(os.getcwd(), name))
        os.chdir(name)
        return True

    def up(self):
        "cd .."
        if not self.parentdirs:
            return self.down()

        os.chdir('..')
        self.curdir = self.parentdirs[-1]
        self.parentdirs = self.parentdirs[:-1]
        return True

    def run(self):
        events = [self.create, self.create, self.modify, self.modify,
                  self.delete, self.delete, self.down, self.up]

        # 1000 random events
        for i in range(1000):
            step = random.choice(events)
            while not step():
                step = random.choice(events)


try:
    try:
        tmpdir = tempfile.mkdtemp()
    
        cmd = "python -u watcher.py %s" % tmpdir
        child = subprocess.Popen(cmd,
                                    shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    
        time.sleep(2)
        os.chdir(tmpdir)
        t = Tester(child)
        t.run()
    finally:
        os.chdir(tmpdir + '/..')
        time.sleep(1)
        os.kill(child.pid, signal.SIGINT)
        unlink(tmpdir)
except:
    out, err =  child.communicate()
    print out
