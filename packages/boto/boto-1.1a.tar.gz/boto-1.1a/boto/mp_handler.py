from mod_python import apache
from boto.sdb.persist import set_domain
from grokdocs.tag import Tag
from boto.utils import find_class
import boto

_initialized = False

_html_start = """
<!DOCTYPE html PUBLIC "~//W3C//DTD XHTML 1.1//EN"
   "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <title>%s</title>
  <meta name="viewport" content="width=320; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;"/>
  <style type="text/css" media="screen">@import "http://iphone.grokdocs.com/iui/iui/iui.css";</style>
  <script type="application/x-javascript" src="http://iphone.grokdocs.com/iui/iui.js"></script></head>
<body>
"""
_html_toolbar = """
  <div class="toolbar">
        <h1 id="pageTitle"></h1>
        <a id="backButton" class="button" selected="true" href="%s">%s</a>
        <a class="button" href="#searchForm">Search</a>
  </div>
"""
_html_end = """
</body>
</html>
"""

def connect():
    global _initialized
    if not _initialized:
        set_domain('grokdocs')
        _initialized = True

def directory(req):
    req.write(_html_start % 'Grokdocs Directory')
    req.write(_html_toolbar % ('/', ''))
    req.write('<ul id="directory" title="Directory" selected="true">\n')
    for key in boto.config.options('Handler'):
        if boto.config.get('Handler', key).find(':') > 0:
            req.write('<li><a href="/%s">%s</a></li>\n' % (key, key))
    req.write('</ul>\n')
    req.write(_html_end)
    return apache.OK

def list_resource(req, resource_name):
    mod_name, cls_name = boto.config.get('Handler', resource_name).split(':')
    cls = find_class(mod_name, cls_name)
    req.write(_html_start % 'Instances of %s' % resource_name)
    req.write(_html_toolbar % ('/', 'GrokDocs'))
    req.write('<ul id="%s" title="%s" selected="true">\n' % (resource_name,
                                                             resource_name))
    for o in cls.list(10):
        req.write(o.summary(format='xhtml', resource_name=resource_name))
    req.write('</ul>\n')
    req.write(_html_end)
    return apache.OK

def view_resource(req, resource_name, resource_id):
    mod_name, cls_name = boto.config.get('Handler', resource_name).split(':')
    cls = find_class(mod_name, cls_name)
    req.write(_html_start % 'View %s:%s' % (resource_name, resource_id))
    req.write(_html_toolbar % ('/'+resource_name, resource_name))
    req.write('<div id="settings" title="Settings" class="panel" selected="true">\n')
    o = cls(resource_id)
    req.write(o.view(format='xhtml', resource_name=resource_name))
    req.write('</div>\n')
    req.write(_html_end)
    return apache.OK

def handle_resource(req):
    t = req.uri.split('/')
    if not boto.config.has_option('Handler', t[1]):
        return not_found(req)
    if len(t) == 2:
        return list_resource(req, t[1])
    elif len(t) == 3:
        return view_resource(req, t[1], t[2])

def not_found(req):
    req.write('<h2>%s Not Found</h2>' % uri)
    return apache.OK
    
def handler(req):
    connect()
    req.content_type = 'text/html'
    if req.uri == '/':
        return directory(req)
    else:
        return handle_resource(req)

