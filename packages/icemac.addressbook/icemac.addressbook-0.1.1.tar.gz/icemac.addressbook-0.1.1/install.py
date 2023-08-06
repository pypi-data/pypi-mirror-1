#! /bin/env python

import os.path
import subprocess
import sys

if __name__ == '__main__':
    python = sys.executable

    # create buildout.cfg
    print 'creating buildout.cfg ...'
    if os.path.exists('buildout.cfg'):
        print "ERROR: buildout.cfg already exists."
        print "       Please rename the existing one and restart install."
        sys.exit(-1)
    buildout_cfg = file('buildout.cfg', 'w')
    buildout_cfg.write('[buildout]\nextends = profiles/base.cfg')
    buildout_cfg.close()

    # call boostrap.py
    print 'calling %s bootstrap.py ...' % python
    res = subprocess.call([sys.executable, 'bootstrap.py'])
    if res:
        sys.exit(res)

    # run buildout
    res = subprocess.call(['bin/buildout'])
    if res:
        sys.exit(res)
