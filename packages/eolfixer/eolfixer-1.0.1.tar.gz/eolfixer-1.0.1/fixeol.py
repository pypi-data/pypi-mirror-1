"""
This script walks over the files and subdirs of the specified directories
('.' by default), and changes the svn properties to match the PyPy guidelines:

 svn:ignore      includes '*.pyc' and '*.pyo' for all directories
 svn:eol-style   is 'native' for *.py and *.txt files

Copyright pypy project, MIT license.

Small modifications by Reinout van Rees.

"""

import os
import sys

import py

EXTENSIONS = []
for ext in ('txt', 'py', 'asc', 'cfg', 'in', 'pt', 'zcml', 'ini'):
    EXTENSIONS.append('.%s' % ext)
    EXTENSIONS.append('.%s_tmpl' % ext)


BINARY_INDICATORS = range(0, 32)
BINARY_INDICATORS.remove(9)    # tab
BINARY_INDICATORS.remove(10)   # lf
BINARY_INDICATORS.remove(12)   # ff, ^L
BINARY_INDICATORS.remove(13)   # cr
BINARY_INDICATORS = [chr(i) for i in BINARY_INDICATORS]


def looksbinary(data):
    "Check if some data chunk appears to be binary."
    for c in BINARY_INDICATORS:
        if c in data:
            return True
    return False


def can_set_eol_style(path):
    "check to see if we could set eol-style on the path."
    data = path.read(mode='rb')
    if looksbinary(data):
        print "%s looks like a binary, ignoring" % path
        return False
    original = data
    data = data.replace('\r\n', '\n')
    data = data.replace('\r', '\n')
    data = data.replace('\n', os.linesep)
    if data != original:
        print "*" * 30
        print "--->  %s  <---" % path
        print ("WARNING: the file content was modified "
               "by fixing the EOL style.")
        print "*" * 30
        #return False
        path.write(data, mode='wb')
        return True
    return True


def checkeolfile(path):
    return path.ext in EXTENSIONS


def fixdirectory(path):
    print "+ checking directory", path,
    fns = path.listdir(checkeolfile)
    if fns:
        ignores = path.propget('svn:ignore')
        newignores = ignores
        l = ignores.split('\n')
        for x in ('*.pyc', '*.pyo'):
            if x not in l:
                l.append(x)
        newignores = "\n".join(l)
        print ", setting ignores", newignores
        path.propset('svn:ignore', newignores)
    else:
        print
    for fn in fns:
        fixfile(fn)
    for x in path.listdir():
        #lambda x: x.check(dir=1, versioned=True)):
        try:
            x.check(versioned=True)
        except:
            print "Non-versioned, ignoring", x
            continue
        if not x.check(dir=1):
            continue
        if x.check(link=1):
            continue
        fixdirectory(x)


def fixfile(path):
    x = path.localpath.relto(py.path.local())
    if not x:
        x = path.localpath
    print "checking", x,
    if path.check(versioned=0):
        return False
    oldprop = path.propget('svn:eol-style')
    if oldprop:
        print "eol-style already set (%r)" % (oldprop, )
    else:
        if can_set_eol_style(path):
            print "setting eol-style native"
            path.propset('svn:eol-style', 'native')
        else:
            print "cannot set eol-style"


def main():
    if len(sys.argv) > 1:
        for fname in sys.argv[1:]:
            paths = [py.path.svnwc(x) for x in sys.argv[1:]]
    else:
        paths = [py.path.svnwc()]

    for path in paths:
        if path.check(link=1):
            print 'ignoring link', path
        elif path.check(dir=1):
            fixdirectory(path)
        elif path.check(file=1):
            fixfile(path)
        else:
            print "ignoring", path
