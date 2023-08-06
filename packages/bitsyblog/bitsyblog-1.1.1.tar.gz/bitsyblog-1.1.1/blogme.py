#!/usr/bin/env python

import optparse
import os
import subprocess
import sys
import tempfile
import urllib2

# global variables

EDITOR='emacs -nw'
SERVER='http://bitsyblog.biz'
dotfile='.blogme'

parser = optparse.OptionParser()
parser.add_option('-s', '--server', default=SERVER)
parser.add_option('-u', '--user')
parser.add_option('-p', '--password')
parser.add_option('--private', action='store_true', default=False)
parser.add_option('--secret', action='store_true', default=False)

options, args = parser.parse_args()

if options.private and option.secret:
    print "post can't be secret and private!"
    sys.exit(1)

# parse dotfile

home = os.environ.get('HOME')
if home:
    dotfile = os.path.join(home, dotfile)
    if os.path.exists(dotfile):
        prefs = file(dotfile).read().split('\n')
        prefs = [ i for i in prefs if i.strip() ]
        prefs = [ [ j.strip() for j in i.split(':', 1) ] for i in prefs
                  if ':' in i] # probably not necessary
        prefs = dict(prefs)
    else:
        prefs = {}

# determine user name and password
fields = [ 'user', 'password' ]
for field in fields:
    globals()[field] = prefs.get(field)

    optval = getattr(options, field)
    if optval:
        password = None # needed to ensure prompting for pw from command line
        globals()[field] = optval

    if globals()[field] is None:
        globals()[field] = raw_input('%s: ' % field)
assert user is not None
assert password is not None

# write the dotfile if it doesn't exist
if not os.path.exists(dotfile):
    preffile = file(dotfile, 'w')
    print >> preffile, 'user: %s' % user
    print >> preffile, 'password: %s' % password
    preffile.close()
    os.chmod(dotfile, 0600)
        
def tmpbuffer(editor=EDITOR):
    """open an editor and retreive the resulting editted buffer"""
    tmpfile = tempfile.mktemp(suffix='.txt')
    cmdline = editor.split()
    cmdline.append(tmpfile)
    edit = subprocess.call(cmdline)
    buffer = file(tmpfile).read().strip()
    os.remove(tmpfile)
    return buffer

# get the blog

if args:
    msg = ' '.join(args)
else:
    msg = tmpbuffer()

# open the url

url = '/'.join((options.server, user))
url += '?auth=digest' # specify authentication method

if options.private:
    url += '&privacy=private'
if options.secret:
    url += '&privacy=secret'

authhandler = urllib2.HTTPDigestAuthHandler()
authhandler.add_password('bitsyblog', url, user, password)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)

try:
    url = urllib2.urlopen(url, data=msg)
    print url.url # print the blog post's url
except urllib2.HTTPError:
    pass
