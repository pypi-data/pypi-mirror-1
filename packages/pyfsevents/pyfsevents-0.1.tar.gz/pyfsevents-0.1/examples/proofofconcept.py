"""
proofofconcept.py - simple script printing the event paths on stdout

Copyright 2009 Nicolas Dumazet <nicdumz@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the MIT License.
"""
import pyfsevents
import os


print """Proof of concept:
    This script watches for the current directory, and prints the paths
    where events occured. (Try creating a file in this directory!)

    Kill it with a ctrl-C"""

def eventprinter(path, subdir):
    print 'event occured in %s*' % path

pyfsevents.registerpath(os.path.abspath('.'), eventprinter)
pyfsevents.listen()
