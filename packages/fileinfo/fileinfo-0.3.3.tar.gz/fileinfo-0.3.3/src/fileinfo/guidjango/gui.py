#!/bin/env/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import atexit
import pickle
from os.path import dirname, join

import psi
from django.http import HttpResponse
try:
    from Foundation import NSURL
    from AppKit import NSWorkspace
    HAVE_PYOBJC = True
except ImportError:
    HAVE_PYOBJC = False

from tmpfile import pickledDataPath


def startDjango(port):
    "Start Django server in the background."
    
    # sys.stdout.close()
    # sys.stderr.close()
    print "Starting Django"
    path = join(dirname(__file__), "manage.py")
    cmd = "/usr/local/bin/python2.5 %s runserver %s" % (path, port)
    atexit.register(stopDjango, cmd)        
    os.system(cmd + " &")


def stopDjango(cmd):
    "Stop Django server."

    print "Stopping Django"
    processTable = psi.process.ProcessTable()
    pids = processTable.pids
    processes = [processTable.processes[i] for (i, pid) in enumerate(pids)]

    # filter process(es) who started Django
    psd = []
    for p in processes:
        try:
            args = p.args # might cause a permision problem
        except:
            continue
        if " ".join(p.args) == cmd:
            psd.append(p)
    
    for p in psd:
        print "terminating %d (%s)" % (p.pid, " ".join(p.args))
        os.system("kill -9 %d" % p.pid)
        
    # delete tmp. file
    os.remove(pickledDataPath)
        

def openPageInBrowser(url):
    # give the browser time to come up
    time.sleep(1.5)
    
    # open registered browser with Django displaying the data    
    if HAVE_PYOBJC:
        nsurl = NSURL.alloc().initWithString_(url)
        workspace = NSWorkspace.sharedWorkspace()
        workspace.openURL_(nsurl)
    elif sys.platform == "darwin":
        cmd = """osascript -e 'tell application "Firefox" to open location "%s"'""" % url
        os.system(cmd)
    else:
        print "No idea how to open %s in a browser. Please DIY!" % url


def main(HEADER, TABLE, FOOTER):
    port = "8899"
    u = "http://127.0.0.1:%s/test/" % port

    startDjango(port)

    # create tmp. file
    data = (HEADER, TABLE, FOOTER[0])
    pickle.dump(data, open(pickledDataPath, "w"))    

    openPageInBrowser(u)

    # block ourself (eating CPU time!)
    # there must be a better way!
    try:
        while True:
            pass
    except:
        pass
        

def test():
    TABLE = """\
    size;file(fake)
    608;crons
    8;ex.csv
    0;fonts
    123;imm.dat
    593;imm.license
    8417;profile1.xml.odt
    4240;UserDefaults.txt
    9999;total"""
    
    TABLE = [line.split(";") for line in TABLE.split("\n")]
    
    HEADER = TABLE[0]
    FOOTER = TABLE[-1]
    TABLE = TABLE[1:-1]
    
    main(HEADER, TABLE, FOOTER)


if __name__ == '__main__':
    try:
        TABLE = open(sys.argv[1]).read().strip()
    except IndexError:
        TABLE = """\
    size;file(fake)
    608;crons
    8;ex.csv
    0;fonts
    123;imm.dat
    593;imm.license
    8417;profile1.xml.odt
    4240;UserDefaults.txt
    9999;total"""
    
    TABLE = [line.split(";") for line in TABLE.split("\n")]
    
    HEADER = TABLE[0]
    FOOTER = TABLE[-1]
    TABLE = TABLE[1:-1]

    main(HEADER, TABLE, FOOTER)
