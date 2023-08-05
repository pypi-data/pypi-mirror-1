"""
    TGCombine 
    @version: 1.0
    combine.py packaged as  a Turbogears Widget
    @author: Vince Spicer
    @contact: vinces1979@gmail.com
"""

from cherrypy import response, HTTPError, request, HTTPRedirect
from jsmin import JavascriptMinify
from os import path
from pkg_resources import resource_filename
from turbogears import expose, config, controllers
from turbogears.util import get_package_name
import mimetypes
import re
from mx import DateTime
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

Scriptbasedir = resource_filename(get_package_name(), 'static') #: base path of the scripts
CacheFolder = config.get('combine.cache', None) #: web cache folder
JSFolder = config.get('combine.javascript', "javascript") #: javascript folder - relative to Scriptbasedir
CSSFolder = config.get('combine.css', "css") #: css folder - relative to Scriptbasedir

CacheTimeOut = int(config.get('combine.timeout', 10)) #: Cache timeout in days ex: 0.5 = 12hrs

def cssMinify(css):
    """
    CSS file compressor
    """
    cssWhiteSpace = re.compile("[\n|\t|\r]")
    cssComment =  re.compile("/\*.*?\*/")
    cssClass = re.compile("([\s\w.#:,]*?){(.*?)}")
    style = re.compile("([\w\s-]*?):(.*?);")

    css = cssComment.sub('', cssWhiteSpace.sub("", css)) #remove comments, eol, and tabs
    return '\n'.join(["%s{%s}" % (x[0].strip(), ''.join(["%s:%s;" % (y[0].strip(), y[1].strip()) for y in style.findall(x[1])])) for x in cssClass.findall(css)])

class combine(controllers.Controller):
    """    Combine and compress CSS/JS files, with caching    """
    
    @expose()
    def default(self, pagename):
        return self.index(pagename)
    
    @expose()
    def index(self, files=None, *kw):
        """ main request handler """
        if not kw and not files:
            raise HTTPError(400, 'No files specified')
        if not files:
            files = kw[0]
        types = {'application/x-javascript': ['javascript', JSFolder], 'text/css': ['css', CSSFolder]}
        Files = files.split(',')
        fname = files.replace(',', '-').replace("/", "_")
        try:
            mime = mimetypes.types_map[path.splitext(Files[0])[1]]
        except KeyError:
            raise HTTPError(400, 'mime type not supported')
        if mime not in types:
            raise HTTPError(400, 'mime type not supported')
        
        response.headers['Content-Type'] = mime
        response.headers['Expires'] = (DateTime.now() + 10).strftime("%a, %d %b %y %X GMT") 
        response.headers['Last-Modified'] = DateTime.now().strftime("%a, %d %b %y %X GMT") 
        
        modified_check = request.headers.get('If-Modified-Since', None)
        cache = config.get('combine.cache', None)
        location = resource_filename(get_package_name(), 'static')
        static = path.join (location, types[mime][1])
        useCache = False
        if cache and path.exists(cache):
            useCache = True
        if useCache:
            if path.exists("%s/%s" % (cache, fname)) and modified_check:
                if DateTime.DateFrom(path.getmtime("%s/%s" % (cache, fname))) <= DateTime.DateFrom(modified_check):
                    raise HTTPRedirect("", 304)
                return open("%s/%s" % (cache, fname)).read()
        ret = StringIO.StringIO()
        for cfile in Files:
            if path.exists(path.join(static, cfile)):
                ret.write(open(path.join(static, cfile), 'r').read())
        ret.seek(0)
        
        if types[mime][0] == 'javascript':
            out = StringIO.StringIO()
            jsm = JavascriptMinify()
            jsm.minify(ret, out)
            out.seek(0)
            ret = out.read()
        elif types[mime][0] == 'css':
            ret = cssMinify(ret.read())
        if useCache:
            cacheFile = open(path.join(cache, fname), 'w')
            cacheFile.write(ret)
            cacheFile.close()
        return ret
