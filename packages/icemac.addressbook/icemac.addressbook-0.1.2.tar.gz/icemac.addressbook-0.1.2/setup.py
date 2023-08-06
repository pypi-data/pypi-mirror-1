# -*- coding: utf-8 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

version = '0.1.2'

setuptools.setup(
    name='icemac.addressbook',
    version=version,
    description="Multi user address book application",
    long_description=(
        read('README.txt') +
        read('INSTALL.txt') +
        read('TODO.txt') +
        read('CHANGES.txt')
        ),
    keywords='python address addressbook zope3 zope application web phone '
             'number e-mail email home page homepage',
    author='Michael Howitz',
    author_email='icemac@gmx.net',
    url='http://pypi.python.org/pypi/icemac.addressbook',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope3',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Religion',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Telephony',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Religion',
        ],
    packages=setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['icemac'],
    include_package_data=True,
    exclude_package_data = {'': ['DE_TODO.txt']},
    zip_safe=False,
    install_requires=[
        'setuptools>=0.6c8',
        'zope.interface>=3.4.0',
        'ZODB3',
        'ZConfig',
        'zdaemon',
        'zope.publisher',
        'zope.traversing',
        'zope.app.wsgi>=3.4.0',
        'zope.app.appsetup',
        'zope.app.zcmlfiles',
        # The following packages aren't needed from the
        # beginning, but end up being used in most apps
#                       'zope.annotation',
#                       'zope.copypastemove',
#                       'zope.formlib',
#                       'zope.i18n',
        'zope.app.authentication',
#                       'zope.app.session',
        # Packages required by application
        'zc.sourcefactory',
        'zope.securitypolicy',
        'z3c.form==1.9.1dev-r91116', 
        'z3c.formui',
        'z3c.layer',
        'z3c.pagelet',
        'gocept.reference==0.5.2',
        'StableDict',
        'gocept.country==0.6.4',
        'gocept.pagelet',
        'z3c.menu.ready2go>0.5.0',
        'zc.catalog',
        'xlwt==0.7.0',
        'z3c.table',
        ],
    extras_require = dict(
        test=['zope.testing',
#               'zope.app.testing',
              'zope.app.securitypolicy',
              'zope.testbrowser',
              'xlrd==0.6.1',
              ]),
    entry_points = """
      [console_scripts]
      debug = icemac.addressbook.startup:interactive_debug_prompt
      addressbook = icemac.addressbook.startup:zdaemon_controller
      debug_ajax = icemac.addressbook.startup:zdaemon_controller_debug_ajax
      debug_pdb = icemac.addressbook.startup:zdaemon_controller_debug_pdb
      [paste.app_factory]
      main = icemac.addressbook.startup:application_factory
      """
    )
