<%
    debug = config['global']['debug']
%>\
#!/usr/bin/python
#!-*- coding:utf-8 -*-

%if debug:
import cgitb
cgitb.enable()
%endif
import nawaapi
%if debug:
nawaapi.dispatch()
%else:
try:
    nawaapi.dispatch()
except:
    nawaapi.error_response()
%endif
