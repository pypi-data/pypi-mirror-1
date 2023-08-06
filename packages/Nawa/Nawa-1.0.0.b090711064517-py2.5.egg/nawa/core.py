#!-*- coding:utf-8 -*-

"""Module of Nawa core functions."""

__author__ =  'rubyu'
__version__=  '1.0'

import os        
import cStringIO
import gzip
import re
import cgi

config_dir = None
config     = None

time      = None
startTime = None


re_int_pat = re.compile(r'^(-)?[0-9]+$')


def get_module_parent(module):
    """Returns parent of module's path."""
    return os.path.split(os.path.abspath(module.__file__))[0]

def init(nawa_config):
    """Given the config, initializes this module."""
    global config
    config = nawa_config.config
    global config_dir
    config_dir = get_module_parent(nawa_config)
    
    if config['global']['debug']:
        global time
        time = __import__('time')
        global startTime
        startTime = time.time() * 1000

def gz(text):
    """Given a string, returns data that gzip encoded, as a string."""
    try:
        gzbuf = cStringIO.StringIO()
        gz = gzip.GzipFile(mode = 'wb',  fileobj = gzbuf, compresslevel = 9)
        gz.write(text)
        gz.close()
        data = gzbuf.getvalue()
    except:
        raise Exception
    return data

def put(content, header={}, cache=True, cache_path=None):
    """Builds response data, write it as cache-file, 
    and output it as http-response.
    
    Caution:
        Response's header will be lost when written 
        it as cache file. Cache file has only "content".
    """
    
    g = config['global']
    
    mimetype = g['mimetype']
    charset  = g['charset']
    
    content = content.encode(charset)
    if g['gzip']:
        content = gz(content)
        header['Content-Encoding'] = 'gzip'
    
    header['Status']         = '200 OK'
    header['Content-Type']   = '%s; charset=%s' % (mimetype, charset)
    header['Content-Length'] = str(len(content))
    
    if g['debug']:
        header['x-nawa_cgi-response'] = 'true'
        header['x-nawa_erapsed(ms)']  = (time.time() * 1000) - startTime
    
    for h in header:
        print '%s: %s' % (h, header[h])
    print ''
    print content
    
    if g['cache'] and cache:
        try:
            #encode path to server locale
            path = cache_path.encode('utf-8')
            f = file(path, 'wb')
            f.write(content)
            f.close()
        except:
            pass

def get_cache_path(apiname, raws):
    """Returns absolute path of cache file.
    
    Usage:
    >>> core.get_cache_path('fooapi', ['001'])
    '/ ... /cache/0/0/1/fooapi&001'
    """
    parent = config_dir
    
    key1 = raws[0]
    d1 = key1[-3]
    d2 = key1[-2]
    d3 = key1[-1]
    filename = apiname
    for key in raws:
        filename += '&%s' % key
        
    path = os.path.join(parent, 'cache', d1, d2, d3, filename)
    return path

def clear(path):
    """Deletes cache file."""
    try:
        os.remove(path)
    except:
        pass

class key_class:
    """Simple class to manage the values that relate
    to key of API."""
    def __init__(self, raws, values):
        self.raws   = raws
        self.values = values

def get_url(*dirs):
    """Given some strings, and returns relative url 
    from root of server.
    
    Usage:
    >>> core.get_url('fooapi', 1)
    '/fooapp/fooapi/1/'
    """
    temp = []
    temp.append(config['global']['project_path'])
    temp += dirs
    
    url = []
    for dir in temp:
        if dir:
            dir = str(dir)
            if '/' == dir:
                continue
            if dir.startswith('/'):
                dir = dir[1:]
            if dir.endswith('/'):
                dir = dir[:-1]
            url.append(dir)
    url = '/'.join(url)
    url = '/%s/' % url            
    return url

class api_base:
    """class of API"""
    def __init__(self):
        self._parse_key()
        
        env = os.environ
        method = env['REQUEST_METHOD']
        
        if 'GET' == method:
            self.GET()
        elif 'POST' == method:
            self.POST()
        else:
            put('', cache=False)
    def GET(self):
        put('', cache=False)
    def POST(self):
        put('', cache=False)
    def response(self, content, header={}, cache=True):
        put(content, header=header, cache=cache, cache_path=self.get_cache_path())
    def _parse_key(self):
        """Parses the query-string and validate it."""
        q_parsed = cgi.parse_qs(os.environ['QUERY_STRING'])
        api_name = self.name
        
        api = config['APIs'][api_name]
        api_type = api['type']
        
        if 'nokey' == api_type:
            if 0 == (len(q_parsed) - 1):
                #valid
                self.key = key_class((), ())
                return
            else:
                #too many keys
                raise Exception
        
        keys = api['keys']
        
        if len(keys) != (len(q_parsed) - 1):
            #too many keys
            raise Exception
        
        raws   = []
        values = []
        for i in xrange(len(keys)):
            key  = api['keys'][i]
            name = key['name']
            try:
                v = q_parsed['key%s' % (i + 1)][0]
            except:
                #not enough
                raise Exception
            
            v = v.decode('utf-8')
            raws.append(v)
            
            type = key['type']
            
            if 'string' == type['name']:
                #check str length
                if type.has_key('min'):
                    if len(v) < int(type['min']):
                        #range error
                        raise Exception
                if type.has_key('max'):
                    if int(type['max']) < len(v):
                        #range error
                        raise Exception
                values.append(v)
                
            elif 'regexp' == type['name']:
                m = re.search(type['pattern'], v)
                if None != m:
                    groups = m.groups()
                    if 0 == len(groups):
                        values.append(v)
                    else:
                        values.append(groups)
                else:
                    #not match = invalid request
                    raise Exception
                
            elif 'int' == type['name']:
                try:
                    vint = int(v)
                except:
                    #value error
                    raise Exception
                
                #kill prolixity
                if not re_int_pat.match(v):
                    #not match ^(-)?[0-9]+$ = prolix
                    raise Exception
                if (0 == i) and ('cacheable' == api_type):
                    #kill value like 0010
                    if v.startswith('00')  and ( 4 <= len(v) ):
                        raise Exception
                else:
                    #kill value like 01
                    if 0 <= v:
                        if v.startswith('0')  and ( 2 <= len(v) ):
                            raise Exception
                    else:
                        if v.startswith('-0') and ( 3 <= len(v) ):
                            raise Exception
                
                if type.has_key('min'):
                    if vint < int(type['min']):
                        #range error
                        raise Exception
                if type.has_key('max'):
                    if int(type['max']) < vint:
                        #range error
                        raise Exception
                values.append(vint)
            else:
                #unknown type
                raise Exception
        if len(keys) != len(values):
            #too many keys
            raise Exception
        
        self.key = key_class(tuple(raws), tuple(values))
        
class api_cacheable(api_base):
    """Class of API that have some keys and can put cache."""
    def get_cache_path(self):
        return get_cache_path(self.name, self.key.raws)

class api_nokey(api_base):
    """Class of API that have no keys and can put cache."""
    def get_cache_path(self):
        key1 = config['APIs'][self.name]['nokey_index']
        return get_cache_path(self.name, [key1])
        
class api_uncacheable(api_base):
    """Class of API that have some keys and can't put cache."""
    def response(self, content, header={}):
        put(content, header=header, cache=False)
    def get_cache_path(self):
        #not support
        raise Exception

    