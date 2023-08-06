#****************************************************************
# File:      ./hakmatak/output/html/dirlist.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.constant import ATTRS,LEAVES,NODES
from hakmatak.constant import NAME,VALUE
#from hakmatak.constant import DATA
from hakmatak.constant import W10N

from hakmatak.constant import SIZE,TYPE,MTIME

from hakmatak.w10n import W10n

from hakmatak.output.writer import Writer

#metaSymbol = "&#60;+&#62;" # <+>
metaSymbol = "&#62;&#62;" # >>

MIMETYPE = "text/html"

class DirList(Writer):

    def _node_as_html(self,d):

        w10n = W10n()
        w10n.from_list(d[W10N])

        attrs = d[ATTRS]
        leaves = d[LEAVES]
        nodes = d[NODES]

        uri = w10n.path + w10n.identifier

        html = "<html><head><title>Index of %s</title></head><body>" % uri
        html += "<h1>Index of %s</h1>" % uri
        html += "<table border='0'>"
        #html += '<tr><th><img src="/icons/blank.gif" alt="[ICO]"></th><th>Name</th><th>Last modified</th><th>Size</th><th>Description</th><th>Meta</th></tr><tr><th colspan="6"><hr></th></tr>'
        html += '<tr><th><img src="/icons/blank.gif" alt="[ICO]"></th><th>Name</th><th>Last modified</th><th>Size</th><th>Metadata</th></tr><tr><th colspan="5"><hr></th></tr>'
        #html += '<tr><td valign="top"><img src="/icons/back.gif" alt="[DIR]"></td><td><a href="..">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td><td>&nbsp;</td><td>&nbsp;</td></tr>'
        html += '<tr><td valign="top"><img src="/icons/back.gif" alt="[DIR]"></td><td><a href="../?output=html">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td><td>&nbsp;</td></tr>'

        # html for leaves
        count = 0
        for x in leaves:
            name = x[NAME]
            size = None
            mtime = None
            if x.has_key(ATTRS):
                for attr in x[ATTRS]:
                    if attr[NAME] == SIZE:
                        size = attr[VALUE]
                    if attr[NAME] == MTIME:
                        mtime = attr[VALUE]
            iconUrl = "/icons/generic.gif"
            #microformat = 'class="w10n"'
            microformat = ''
            path = name + "[]" # direct dump with mimetype figured out by magic
            if mtime == None:
                mtime = "&nbsp;" 
            if size == None:
                size = "&nbsp;"
            meta = '<a style="text-decoration: none;" href="%s/?output=json">%s</a>' % (name,metaSymbol)
            #html += '<tr><td valign="top"><img src="%s" alt="[   ]"></td><td><a %s href="%s">%s</a></td><td align="right">%s</td><td align="right">%s</td><td>&nbsp;</td><td align="center">%s</td></tr>' % (iconUrl,microformat,path,name,mtime,size,meta)
            html += '<tr><td valign="top"><img src="%s" alt="[   ]"></td><td><a %s href="%s">%s</a></td><td align="right">%s</td><td align="right">%s</td><td align="center">%s</td></tr>' % (iconUrl,microformat,path,name,mtime,size,meta)
            count += 1

        # html for sub nodes
        count = 0
        for x in nodes:
            name = x[NAME]
            size = None
            mtime = None
            if x.has_key(ATTRS):
                for attr in x[ATTRS]:
                    if attr[NAME] == SIZE:
                        size = attr[VALUE]
                        if size == 0:
                            size = None
                    if attr[NAME] == MTIME:
                        mtime = attr[VALUE]
            iconUrl = "/icons/folder.gif"
            #microformat = 'class="w10n"'
            microformat = ''
            path = name + "/?output=html"
            if mtime == None:
                mtime = "&nbsp;"
            if size == None:
                size = "&nbsp;"
            meta = '<a style="text-decoration: none;" href="%s/?output=json">%s</a>' % (name,metaSymbol)
            #html += '<tr><td valign="top"><img src="%s" alt="[   ]"></td><td><a %s href="%s">%s</a></td><td align="right">%s</td><td align="right">%s</td><td>&nbsp;</td><td align="center">%s</td></tr>' % (iconUrl,microformat,path,name,mtime,size,meta)
            html += '<tr><td valign="top"><img src="%s" alt="[   ]"></td><td><a %s href="%s">%s</a></td><td align="right">%s</td><td align="right">%s</td><td align="center">%s</td></tr>' % (iconUrl,microformat,path,name,mtime,size,meta)
            count += 1

        html += '<tr><th colspan="5"><hr></th></tr>'
        html += "</table>"
        html += "<em>application:%s, spec:%s, type:%s</em>" % (w10n.application,w10n.spec,w10n.type)
        html += "</body></html>"

        return html

    def write(self,d):
        return (self._node_as_html(d),MIMETYPE)

def main():
    from hakmatak.node import Node
    from hakmatak.leaf import Leaf

    # create a simple d
    node = Node("")
    for i in range(3):
        name = "%s" % i
        leaf = Leaf(name)
        node.leaves.append(leaf.get_meta())
    d = node.get_meta()

    # create a simple w10n
    w10n = W10n()
    w10n.identifier = "/"
    w10n.path = "/a_fake_path"
    w10n.type = "test"
    d[W10N] = w10n.to_list()

    # write d in html as a dir list
    dirListWriter = DirList()
    data,mimeType = dirListWriter.write(d)

    import sys
    print >>sys.stderr, mimeType
    print >>sys.stdout, data

if __name__ == "__main__":
    main()
