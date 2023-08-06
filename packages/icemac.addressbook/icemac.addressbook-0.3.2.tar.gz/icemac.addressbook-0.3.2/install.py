#! /bin/env python

import os.path
import subprocess
import sys

if __name__ == '__main__':
    python = sys.executable

    # prerequisites
    if os.path.exists('buildout.cfg'):
        print "ERROR: buildout.cfg already exists."
        print "       Please rename the existing one and restart install."
        sys.exit(-1)

    # create admin.zcml
    print ' Log-in name for the administrator: ',
    admin_login = sys.stdin.readline().strip()
    print 'Password for the administrator: ',
    admin_passwd = sys.stdin.readline().strip()
    admin_zcml = file('admin.zcml', 'w')
    admin_zcml.write('\n'.join(
            ('<configure xmlns="http://namespaces.zope.org/zope">',
             '  <principal',
             '    id="icemac.addressbook.global.Administrator"',
             '    title="global administrator"',
             '    login="%s"' % admin_login,
             '    password_manager="Plain Text"',
             '    password="%s" />' % admin_passwd,
             '  <grant',
             '    role="zope.Manager"',
             '    principal="icemac.addressbook.global.Administrator" />',
             '</configure>',
             )))
    admin_zcml.close()

    # create buildout.cfg
    print 'creating buildout.cfg ...'
    buildout_cfg = file('buildout.cfg', 'w')
    buildout_cfg.write('[buildout]\nextends = profiles/prod.cfg')
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
