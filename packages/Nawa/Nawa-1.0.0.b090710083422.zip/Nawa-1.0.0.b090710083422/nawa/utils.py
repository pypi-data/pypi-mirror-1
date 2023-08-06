#!-*- coding:utf-8 -*-

"""Module of Nawa framework generation."""

__author__ =  'rubyu'
__version__=  '1.0'

import os
import shutil
import codecs
from datetime import datetime

import yaml
from mako.template import Template


config_name = 'nawa_config.yaml'
    
    
def read_config(path):
    """Given a path to config yaml, returns config 
    that is python object.
    
    This function needs PyYAML.
    """
    print '[read_config] ... ',
    
    str = open(path).read()
    str = str.decode('utf-8')
    config = yaml.load(str)
    
    print 'ok'
    return config

def write_config(path, config):
    """Writes config to given path as python module."""
    
    print '[write_config] ... ',
    
    config_py = '# !-*- coding:utf-8 -*-\n\nconfig = ' + str(config)
    f = codecs.open(path, 'wb', 'utf-8')
    f.write(config_py)
    f.close()
    
    print 'ok'

import re

def validate_config(config):
    """Validates and normalizes config,"""
    
    print '[validate_config] ... '

    print 'normalize keys ... ',
    apis = config['APIs']
    for apiname in apis:
        api = apis[apiname]
        if None == api:
            #api is nokey
            continue
        
        keys = api['keys']
        
        if 0 == len(keys):
            #delete array if it is empty
            del api['keys']
            continue
        
        for key in keys:
            if not key.has_key('type'):
                #apply default
                temp = {}
                temp['name'] = 'int'
                temp['min']  = 0
                key['type'] = temp
                continue
            
            type = key['type']
            
            #wash key type
            if 'string' == type['name']:
                temp = {}
                temp['name'] = 'string'
                if type.has_key('max'):
                    temp['max'] = type['max']
                if type.has_key('min'):
                    temp['min'] = type['min']
                key['type'] = temp
                
            elif 'int' == type['name']:
                temp = {}
                temp['name'] = 'int'
                if type.has_key('max'):
                    temp['max'] = type['max']
                if type.has_key('min'):
                    temp['min'] = type['min']
                key['type'] = temp
            
            elif 'regexp' == type['name']:
                temp = {}
                temp['name'] = 'regexp'
                if type.has_key('pattern'):
                    pattern = type['pattern']
                    re.compile(pattern)
                    temp['pattern'] = pattern
                key['type'] = temp
    print 'ok'
    
    
    """
    Checks api type, and save the result.
    ・api have no key                        -> nokey
    ・key1 is int and (0 <= min)             -> cacheable
    ・key1 is (not int) or (int and min < 0) -> uncacheable
    """
    print 'checking api type ...'
    nokey_index = 1
    for apiname in apis:
        api = apis[apiname]

        if None == api:
            api = {}
            
            nokey_id = str(nokey_index)
            api['nokey_index'] = (3 - len(nokey_id)) * '0' + nokey_id[-3:]
            nokey_index += 1
            
            api['type'] = 'nokey'
            apis[apiname] = api
            
            print '  %s is %s' % (apiname, 'nokey')
            continue
        
        type = api['keys'][0]['type']
        if ( ( 'int' != type['name'] ) or
             #(is not int) or
             ( not type.has_key('min') or ( type['min'] < 0 ) )
             #(is int and min is undefined) or (min < 0)
             ):
            api['type'] = 'uncacheable'
            print '  %s is %s' % (apiname, 'uncacheable')
            continue
        api['type'] = 'cacheable'
        print '  %s is %s' % (apiname, 'cacheable')
    print 'ok'
    
    
    
def generate_cache_dir(cachepath):
    """Given a path to cache directory, generates cache 
    directory structure.    
    """
    
    print '[generate_cache_dir] ... ',
    for i in xrange(10):
        for j in xrange(10):
            for k in xrange(10):
                try:
                    p = os.path.join(cachepath, `i`, `j`, `k`)
                    os.makedirs(p)
                except:
                    pass
    print 'ok'

def generate_files(output_dir, tmpl_dir, config):
    """Output files.
    
    This function needs Mako.
    """
    backup_time = datetime.now().strftime("%y%m%d%H%M%S")
    
    print '[generate_files] ... '
    
    for (root, dirs, files) in os.walk(tmpl_dir):
        for file in files:
            
            file = os.path.join(root, file)
                
            print '  %s ... ' % file,
            
            tmpl = Template(filename = file,
                            input_encoding = 'utf-8'
                            )
            output = tmpl.render(**{'config': config})
            
            output_path = os.path.join(output_dir, file[len(tmpl_dir) + 1:])
            #backup
            if os.path.exists(output_path):
                shutil.copy2(output_path, '%s.%s' % (output_path, backup_time))
                
            f = codecs.open(output_path, 'wb', 'utf-8')
            f.write(output)
            f.close()
            
            if file.endswith('.py'):
                os.chmod(output_path, 0775)
                
            print 'ok'
    print 'ok'

def generate_framework(profile_name, target_path):
    """Given target template name and a path to config yaml, generates framework under 
    the rule that config define."""
    
    parent = os.path.split(os.path.abspath(__file__))[0]
    tmpl_path = os.path.join(parent, 'profile_templates', profile_name)
    config_pyname = config_name[:config_name.index('.')] + '.py' 
    
    print 'target_path: %s' % target_path
    print 'profile: %s' % profile_name
    print 'template_path: %s' % tmpl_path
    
    if not os.path.exists(os.path.join(target_path, 'cache')):
        generate_cache_dir(os.path.join(target_path, 'cache'))

    config = read_config(os.path.join(target_path, config_name))
    validate_config(config)
    generate_files(target_path, tmpl_path, config)
    write_config(os.path.join(target_path, config_pyname), config)
    
    print 'finish.'
