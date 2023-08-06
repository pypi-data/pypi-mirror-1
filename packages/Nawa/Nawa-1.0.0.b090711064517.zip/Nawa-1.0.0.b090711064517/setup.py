#!-*- coding:utf-8 -*-

from datetime import datetime
created = datetime.now().strftime('%y%m%d%H%M%S')

PACKAGE_NAME    = "Nawa"
PACKAGE_VERSION = "1.0.0.b%s" % created
SUMMARY     = "Nawa is a simple Python web framework that designed for our ecological scripting life."
DESCRIPTION = """\
Nawa is a simple Python web framework that designed \
for our ecological scripting life. Nawa runs the \
application fast, using a trick that apache returns \
cache file to client directly. So if cache exists, \
script not awakes, apache returns response faster \
than FCGI environment.
"""

import os
data_files = []
for path, dirs, files in os.walk('nawa'):
    path = path.replace('\\', '/')
    data_files.append([path, ['%s/%s' % (path, f) for f in files]])

from setuptools import setup, find_packages
setup(
    name    = PACKAGE_NAME,
    version = PACKAGE_VERSION,
    description      = SUMMARY,
    long_description = DESCRIPTION,
    
    packages = find_packages(),
    data_files = data_files,
    scripts = ['nawa/bin/nawa_admin.py'],
    
    install_requires = ['Mako>=0.2.4', 'PyYAML>=3.08'],
    
    url          = 'http://code.google.com/p/nawa-framework/',
    author       = 'ruby-U',
    author_email = 'ruby.u.g@gmail.com',
    
    license   = 'MIT',
    platforms = ['Any'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   ],
)
