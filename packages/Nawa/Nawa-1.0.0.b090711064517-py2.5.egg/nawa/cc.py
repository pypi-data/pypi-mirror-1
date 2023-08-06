#!-*- coding:utf-8 -*-

"""Module of Nawa cache file delete functions."""

__author__ =  'rubyu'
__version__=  '1.0'

import os

config_dir = None
config     = None


def get_module_parent(module):
    """Returns parent of module's path."""
    return os.path.split(os.path.abspath(module.__file__))[0]

def init(nawa_config):
    """Given the config, initializes this module."""
    global config
    config = nawa_config.config
    global config_dir
    config_dir = get_module_parent(nawa_config)

def clean():
    """Deletes cache files."""
    
    quota = config['CC']['quota']
    min   = config['CC']['min']
    
    cache_dir = os.path.join(config_dir, 'cache')
    
    total = 0
    counts = []
    
    for i in xrange(10):
        istr = str(i)
        try:
            count = len(os.listdir( os.path.join(cache_dir, '0', '0', istr) ))
        except:
            count = 0
        total += count
        counts.append( (count, istr) )
    
    counts.sort(reverse=True)
    
    total *= 100
    
    deleted = 0
    
    for i in xrange(10):
        count = counts.pop()
        istr = count[1]
        for j in xrange(10):
            jstr = str(j)
            for k in xrange(10):
                kstr = str(k)
                delete_dir = os.path.join(cache_dir, kstr, jstr, istr)
                try:
                    for f in os.listdir(delete_dir):
                        try:
                            os.remove(os.path.join(delete_dir, f))
                            deleted += 1
                        except:
                            pass
                except:
                    pass
            if (min <= deleted) and ( ( total - deleted ) <= quota ):
                break
    return (total, deleted)
    
def clean_full():
    """Deletes all cache files."""
    
    cache_dir = os.path.join(config_dir, 'cache')
    
    deleted = 0
    for i in xrange(10):
        istr = str(i)
        for j in xrange(10):
            jstr = str(j)
            for k in xrange(10):
                kstr = str(k)
                delete_dir = os.path.join(cache_dir, istr, jstr, kstr)
                try:
                    for f in os.listdir(delete_dir):
                        try:
                            os.remove(os.path.join(delete_dir, f))
                            deleted += 1
                        except:
                            pass
                except:
                    pass
    return deleted

