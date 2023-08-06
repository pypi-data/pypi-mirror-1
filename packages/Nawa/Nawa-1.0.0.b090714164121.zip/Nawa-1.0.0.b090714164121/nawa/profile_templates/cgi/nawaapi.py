<%
    debug   = config['global']['debug']
    charset = config['global']['charset']
    apis    = config['APIs']
%>\
#!-*- coding:utf-8 -*-

import os
import cgi
import datetime

from nawa import core

%for api_name in apis:
<%
    api = apis[api_name]
    api_type = api['type']
%>\
%if 'nokey' == api_type:
class api_${ api_name }(core.api_nokey):
    """API ${ api_name },
    
      - is cacheable.
      - has no keys.
    """
    name = '${ api_name }'
    def GET(self):
%else:
<%
    keys = api['keys']
    args = []
    for key in keys:
        args.append(key['name'])
    args = ', '.join(args)
%>\
%if 'cacheable' == api_type:
class api_${ api_name }(core.api_cacheable):
%elif 'uncacheable' == api_type:
class api_${ api_name }(core.api_uncacheable):
%endif
    """API ${ api_name },

      - is ${ api_type }.
      - has ${ len(keys) } keys.
      
%for i in xrange(len(keys)):
<%
    key = keys[i]
    key_name = key['name']
    key_type = key['type']
%>\
          - ${ key_name }(${ key_type['name'] })
%for key_type_key in key_type:
%if not ('name' == key_type_key):
                ${ key_type_key }: ${ key_type[key_type_key] }
%endif
%endfor
%endfor
    """
    name = '${ api_name }'
    def GET(self):
%if 1 == len(keys):
        ${ args } = self.key.values[0]
%else:
        ${ args } = self.key.values
%endif
%endif
        
        content =  'api_path: %s<br>' % cgi.escape(core.get_url(self.name), True)
        content += 'api: %s<br>'      % cgi.escape(self.name, True)
        content += 'key(raw):       %s<br>' % cgi.escape(str(self.key.raws), True)
        content += 'key(validated): %s<br>' % cgi.escape(str(self.key.values), True)
        content += 'generated: %s<br>' % datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
        self.response(content)
        
%endfor

api = {
%for api_name in apis:
    '${ api_name }': api_${ api_name },
%endfor
}

def error_response():
    print 'Status: 200 OK'
    print 'Content-Type: text/plain'
    print ''
    print 'Error occured.'

def dispatch():
    q = cgi.parse_qs(os.environ['QUERY_STRING'])
    apiname = q['apiname'][0]
    if api.has_key(apiname):
        import nawa_config
        core.init(nawa_config)
        api[apiname]()
    else:
        #unknown API
        raise Exception
    