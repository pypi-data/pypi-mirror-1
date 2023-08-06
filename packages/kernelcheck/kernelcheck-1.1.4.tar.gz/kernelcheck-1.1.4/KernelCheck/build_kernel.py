#!/usr/bin/env python

import os, sys, tempfile

from subprocess import *

###---Build Kernel
def build(config, reconfigure, patchtype, data):
    print "-- Process initialized --"
    print
    print "Kernel patch: " + str(patchtype)
    print "Manually configure options: " + str(config)
    print "Reconfigure X Server: " + str(reconfigure)
    print
    
    # Get data from tuple
    stable = data[0]
    stable_url = data[1]
    patch = data[2]
    patch_url = data[3]
    envy = str(data[4])
    
    print "Data:"
    print "Kernel: " + stable
    print "Patch: " + patch
    print

    try:
        t_path = tempfile.mktemp()
        ttt = os.open(t_path, os.O_CREAT | os.O_RDWR)
    # O_RDWR allows read & write
    except IOError:
        print 'Error:  Couldn\'t create temp file.'
        sys.exit(0)

    os.write(ttt, stable + '\n')
    os.write(ttt, stable_url + '\n')
    os.write(ttt, patch + '\n')
    os.write(ttt, patch_url + '\n')
    os.write(ttt, envy + '\n')
    # always close and remove the temp file
    # before you exit from script
    os.close(ttt)

    return t_path
