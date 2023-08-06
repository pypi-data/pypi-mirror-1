#!/usr/bin/python
#!-*- coding:utf-8 -*-

"""Command line tool for Nawa framework management.

Usage:
  nawa_admin.py command
"""

import os
import sys
import shutil
from datetime import datetime

from nawa import core, utils

project_templates = ('nawa_config.yaml',
                     )

tools = ('nawa_cache_clean_ep.py',
         'nawa_cgi_serv.py'
         )

def start_project(argv):
    """Copies files of project template to current directory."""
    
    backup_time = datetime.now().strftime("%y%m%d%H%M%S")
    
    nawa_path = core.get_module_parent(core)  
    current   = os.getcwdu()
    
    for f in project_templates:
        From = os.path.join(nawa_path, 'bin', 'project_templates', f)
        To   = os.path.join(current, f)
        #backup
        if os.path.exists(To):
            shutil.copy2(To, '%s.%s' % (To, backup_time))
        #copy
        shutil.copy(From, To)
        
    for f in tools:
        From = os.path.join(nawa_path, 'tools', f)
        To   = os.path.join(current, f)
        #copy
        shutil.copy2(From, To)
    
def generate(argv):
    """Generate framework environment."""
    
    current = os.getcwdu()
    utils.generate_framework('cgi', current)

def help(argv):
    if 0 != len(argv):
        command = argv[0]
        if command and command != 'help':
            print commands[command].__doc__
    else:
        print __doc__
        print 'commands:'
        for command in commands:
            print '  %s' % command
        print ''
    sys.exit()

commands = {'start_project': start_project,
            'generate': generate,
            'help': help
            }

def error(str):
    print 'Error: %s' % str
    sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv[1:]
    if 0 == len(argv):
        help([])
    command = argv.pop(0)
    if commands.has_key(command):
        commands[command](argv)
    else:
        error('unknown command')
    