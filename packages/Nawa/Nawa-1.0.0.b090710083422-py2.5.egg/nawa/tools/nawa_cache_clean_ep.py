#!/usr/bin/python
#!-*- coding:utf-8 -*-

"""sample script. call nawa.cc.clean()

This script will work as alternate of cron.
If your server account not-support cron, you setup this 
script to your server account, and add the path of script 
to some web feedreader service. So, feedreader service 
will request that path at intervals.

nawa.cc.clean() is a little heavy.
you must carefully use this script.
"""

__author__ =  'rubyu'
__version__=  '1.0'


def rss():
    """Return result of nawa.cc.clean() as RSS Feed."""
    
    import os
    import nawa_config
    from nawa import cc
    cc.init(nawa_config)
    
    total, deleted = cc.clean()
    host = os.environ['HTTP_HOST']
    path = os.environ['SCRIPT_NAME']
    path = path[:path.rindex('/')]
    url = 'http://%s%s/' % (host, path)
    
    import datetime
    now = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0900')
    xml = []
    xml.append( '<?xml version="1.0" encoding="UTF-8" ?>' )
    xml.append( '<rss version="2.0">' )
    xml.append( '<channel>' )
    xml.append( '<title>nawa_cache_clean</title>' )
    xml.append( '<link>%s</link>' % url )
    xml.append( '<description>status of nawa.cc.clean()</description>' )
    xml.append( '<pubDate>%s</pubDate>'             % now )
    xml.append( '<lastBuildDate>%s</lastBuildDate>' % now )
    xml.append( '<language>us-en</language>' )
    
    xml.append( '<item>' )
    xml.append( '<title>%s -> %s</title>' % (total, total - deleted) )
    xml.append( '<link>%s</link>' % url )
    xml.append( '<pubDate>%s</pubDate>' % now )
    xml.append( '</item>' )

    xml.append( '</channel>' )
    xml.append( '</rss>' )
    xml = ''.join(xml)
    
    print 'Status: 200 OK'
    print 'Content-Type: application/xml; charset=utf-8'
    print ''
    print xml.encode('utf-8')

if __name__ == "__main__":
    rss()