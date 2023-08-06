#!-*- coding:utf-8 -*-

from datetime import datetime
created = datetime.now().strftime('%y%m%d%H%M%S')

import os
data_files = []
for path, dirs, files in os.walk('nawa'):
    path = path.replace('\\', '/')
    data_files.append([path, ['%s/%s' % (path, f) for f in files]])

from setuptools import setup, find_packages
setup(
    name = 'Nawa',
    version = '1.0.0.b%s' % created,
    packages = find_packages(),
    scripts = ['nawa/bin/nawa_admin.py'],
    data_files = data_files,
    
    install_requires = ['Mako>=0.2.4', 'PyYAML>=3.08'],
    
    url = 'http://code.google.com/p/nawa-framework/',
    author = 'ruby-U',
    author_email = 'ruby.u.g@gmail.com',
    description = 'Nawa is a simple Python web framework that designed for our ecological scripting life.',
)
