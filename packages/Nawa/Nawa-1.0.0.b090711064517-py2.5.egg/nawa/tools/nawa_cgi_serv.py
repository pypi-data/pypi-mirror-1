#!-*- coding:utf-8 -*-

"""It works as a simple http-server, gives you 
support to rapid Nawa-CGI application development.

caution:
  If you have edited config (nawa_config.yaml),
  you should be kill this script once.
  Because this script import and cache the 
  module nawa_config, so changes of config 
  have no effect to behave of this script.

todo:
  - setting with arguments
  - rational mod_rewrite emulation 
"""

__author__ =  'rubyu'
__version__=  '1.0'

import os
import sys
import CGIHTTPServer
import BaseHTTPServer
import SimpleHTTPServer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import cgi

from nawa_config import config

project_path = config['global']['project_path']
apis         = config['APIs']
end_point    = config['htaccess']['end_point']
index        = config['htaccess']['index']

print '-' * 10
print 'nawa_cgi_serv.py'
print '-' * 10
print '[project_path] %s' % project_path
print '[end_point] %s' % end_point
print '-' * 10

class custom_CGIHTTPRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):    
    end_point_path = '/%s' % end_point #separate with '/', not '\'
    def do_GET(self):
        self.do_POST()
    def do_POST(self):
        self.rewrite()
    def rewrite(self):
        self._path = self.path
        path       = self.path
        
        if project_path and '/' != project_path:
            if '/' != path:
                if path.startswith(project_path):
                    path = path[len(project_path):]
                else:
                    self.send_error(404, 'path(%s) not match project_path(%s)' % (path, project_path))
                    return
            else:
                f = StringIO()
                f.write('hosting <a href="%s">%s</a>\n' % (cgi.escape(project_path, True), cgi.escape(project_path, True)))
                f.write('<hr>')
                f.write('<h2>api info:</h2>\n')
                f.write('<table border="1">')
                for api in apis:
                    f.write('<tr>')
                    api_name = api
                    api = apis[api]
                    api_type = api['type']
                    f.write('<td>%s</td>' % cgi.escape(api_name, True))
                    f.write('<td>%s</td>' % cgi.escape(api_type, True))
                    if 'nokey' != api_type:
                        keys = api['keys']
                        for key in keys:
                            f.write('<td>%s</td>' % cgi.escape(str(key), True))
                    f.write('</tr>\n')
                f.write('</table>\n')
                f.write('<h2>config:</h2>\n')
                nawa_config_yaml = open('nawa_config.yaml', 'rb').read()
                f.write('<div><pre>')
                f.write(cgi.escape(nawa_config_yaml, True))
                f.write('</pre></div>')
                f.write('<hr>')
                length = f.tell()
                f.seek(0)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(length))
                self.end_headers()
                self.copyfile(f, self.wfile)
                return

        if path.startswith('/'):
            path = path[1:]
        
        print '[rewrite start] %s' % path
            
        if not path:
            if index:
                print '[rewrite DirectoryIndex] ',
                print path,
                path = index
                print ' -> %s' % path
            else:
                self.send_error(404, 'DirectoryIndex disabled')
                return
        
        if apis.has_key(path.split('/')[0]):
            print '[rewrite] %s' % path,
            
            if path.endswith('/'):
                path = path[:-1]
            list = path.split('/')
            api_name = list.pop(0)
            q = []
            q.append('apiname=%s' % api_name)
            for i in xrange(len(list)):
                if 0 == i:
                    list[i] = (3 - len(list[i]))*'0' + list[i]
                q.append('key%s=%s' % (i + 1, list[i]))
            query = '&'.join(q)
            #self.path = '%s?%s' ... Bug? CGIHTTPServer.py version 0.4 line 111-128
            self.path = './%s?%s' % (self.end_point_path, query)
            
            print ' - > %s?%s' % (end_point, query)
            
            self.cgi_info = '', end_point
            self.run_cgi()
        else:
            #static file
            self.path = '/%s' % path
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        
BaseHTTPServer.HTTPServer(( '127.0.0.1', 8086 ), custom_CGIHTTPRequestHandler).serve_forever()
