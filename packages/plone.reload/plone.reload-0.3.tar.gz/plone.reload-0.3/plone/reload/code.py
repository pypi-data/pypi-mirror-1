import os
import os.path
import sys

_marker = []

BLACKLIST = _marker

def blacklist():
    global BLACKLIST
    if BLACKLIST is _marker:
        tmp = os.environ.get('TMPDIR', None)
        swhome = os.environ.get('SOFTWARE_HOME', None)
        zopehome = os.environ.get('ZOPE_HOME', None)
        pyhome = os.path.dirname(os.__file__)

        BLACKLIST = [os.path.abspath(p) for p in
                     (tmp, swhome, zopehome, pyhome) if p]

    return BLACKLIST

def search_path():
    path = []
    for p in tuple(sys.path):
        p = os.path.abspath(p)
        if not [p.startswith(b) for b in blacklist()]:
            path.append(p)
    return path

def reload_code():
    

    pass