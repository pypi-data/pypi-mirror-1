#!/usr/bin/env python

"""
A hook into setuptools for Git

"""

CMD = "git ls-files '%s' 2>/dev/null"

import os
from string import strip

def gitlsfiles(dirname=""):

    pipe = os.popen(CMD % dirname)
    files = pipe.readlines()
    
    if pipe.close():
        # Something went terribly wrong but the setuptools doc says we
        # must be strong in the face of danger.  We shall not run away
        # in panic.
        return []
    return map(strip, files)

if __name__ == "__main__":
    import sys
    from pprint import pprint
    if len(sys.argv) != 2:
        print "USAGE: %s DIRNAME" % sys.argv[0]
        sys.exit(1)
    pprint(gitlsfiles(sys.argv[1]))
    
