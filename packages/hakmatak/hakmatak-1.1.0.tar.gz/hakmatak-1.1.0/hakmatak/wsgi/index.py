#!/usr/bin/env python
#****************************************************************
# File:      ./hakmatak/wsgi/index.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************

import os

from datetime import datetime

import re

from hakmatak.constant import APP_NAME,APP_VERSION
from hakmatak.w10n import W10n

# for identifying those as webifiable
# this must be consistent with rewrite rules in httpd.conf
PATTERN = re.compile('^.*/[^/]+\.(txt)$')

#SYMBOL = "&#92;&#33;&#47;" # \!/
#SYMBOL = "&#92;&#124;&#47;" # \|/
SYMBOL = "<img border='0' src='/icons/folder.gif'/>"

class Handler:
    def __init__(self,patterns=None,w10n=None):
        self.patterns = [PATTERN]
        if patterns != None:
            self.patterns = patterns

        if w10n == None:
            self.w10n = W10n()
        else:
            self.w10n = w10n

    # overidden by sub class
    def add_pattern(self,compiledPattern=None):
        if compiledPattern == None:
            return
        self.patterns.append(compiledPattern)

    def _is_webifiable(self,path):
        for p in self.patterns:
            if p.match(path):
                return True

    def do(self, environ, start_response):

        uri = environ['REQUEST_URI']

        dpath = environ['DOCUMENT_ROOT'] + uri
        # it must be dir
        if not os.path.isdir(dpath):
            raise Exception("Not a dir: %s" % dpath)

        # collection entries in l
        l = []
        # sort to lexical order
        dirList = os.listdir(dpath)
        dirList.sort()
        count = 0
        for name in dirList:
            # fixme: cap it at 1000 entries. it should be paged.
            if count >= 1000:
                break
            # skip these with leading '.', which are supposed to be hidden
            if name[0] == '.':
                continue
            path = dpath + name
            # ignore errors like rotten symlink
            try:
                stat = os.stat(path)
            except:
                continue
            #mtime = datetime.fromtimestamp(stat.st_mtime).isoformat('T')
            #mtime = datetime.fromtimestamp(stat.st_mtime)
    	# this is what apache provides
            #mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%d-%b-%Y %H:%M")
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = stat.st_size
            isDir = False
            if os.path.isdir(path):
                isDir = True
            l.append([name,mtime,size,isDir])
            count += 1

        # convert the list to html
        html = "<html><head><title>Index of %s</title></head><body>" % uri
        html += "<h1>Index of %s</h1>" % uri
        html += "<table border='0'>"
        #html += '<tr><th><img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Webifiable</a></th></tr><tr><th colspan="5"><hr></th></tr>'
        html += '<tr><th><img src="/icons/blank.gif" alt="[ICO]"></th><th>Name</th><th>Last modified</th><th>Size</th><th>Description</th><th>Webifiable</th></tr><tr><th colspan="6"><hr></th></tr>'
        html += '<tr><td valign="top"><img src="/icons/back.gif" alt="[DIR]"></td><td><a href="..">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td><td>&nbsp;</td><td>&nbsp;</td></tr>'
        for x in l:
            name,mtime,size,isDir = x
            #iconUrl = "/icons/unknown.gif"
            iconUrl = "/icons/generic.gif"
            path = uri + name
            webifiable = "&nbsp;"
            microformat = ""
            if isDir:
                size = "-"
                iconUrl = "/icons/dir.gif"
                path += '/'
                name += '/'
            else:
                pass
            if self._is_webifiable(path):
                microformat = 'class="w10n"'
                #webifiable = "<a href='%s/'><img border='0' src='/icons/ball.red.gif'/></a>" % path
                #webifiable = "<a href='%s/'><img border='0' src='/icons/right.gif'/></a>" % path
                #webifiable = "<a href='%s/?output=html'><img border='0' src='/icons/folder.gif'/></a>" % path
                webifiable = '<a style="text-decoration: none;" href="%s/?output=html">%s</a>' % (path,SYMBOL)
            html += '<tr><td valign="top"><img src="%s" alt="[   ]"></td><td><a %s href="%s">%s</a></td><td align="right">%s</td><td align="right">%s</td><td>&nbsp;</td><td align="center">%s</td></tr>' % (iconUrl,microformat,path,name,mtime,size,webifiable)
        html += '<tr><th colspan="6"><hr></th></tr>'
        html += "</table>"
        html += "<em>application:%s, spec:%s</em>" % (self.w10n.application,self.w10n.spec)

        html += "</body></html>"

        output = html
        mimeType = 'text/html'

        status = '200 OK'
        response_headers = [('Content-type', mimeType),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

# wsgi entry point
def application(environ, start_response):
    handler = Handler()
    #handler.add_pattern(PATTERN)
    return handler.do(environ, start_response)

# cgi entry point
if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
