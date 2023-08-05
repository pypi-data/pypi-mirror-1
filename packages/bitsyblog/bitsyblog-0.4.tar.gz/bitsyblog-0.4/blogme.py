#!/usr/bin/env python

import optparse
import os
import subprocess
import tempfile
import urllib2

EDITOR='emacs -nw'
SERVER='http://bitsyblog.biz'
USER='k0s'

parser = optparse.OptionParser()
parser.add_option('-s', '--server', default=SERVER)
parser.add_option('-u', '--user', default=USER)

options, args = parser.parse_args()

def tmpbuffer(editor=EDITOR):
    """open an editor and retreive the resulting editted buffer"""
    tmpfile = tempfile.mktemp()
    cmdline = editor.split()
    cmdline.append(tmpfile)
    edit = subprocess.call(cmdline)
    buffer = file(tmpfile).read()
    os.remove(tmpfile)
    return buffer

if args:
    msg = ' '.join(args)
else:
    msg = tmpbuffer()
    
print urllib2.urlopen('/'.join((options.server, options.user)),
                      data=msg).read()
