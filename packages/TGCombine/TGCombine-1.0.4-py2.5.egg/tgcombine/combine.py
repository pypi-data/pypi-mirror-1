"""
    TGCombine 
    @version: 1.0.4
    combine.py packaged as  a Turbogears Widget
    @author: Vince Spicer
    @contact: vinces1979@gmail.com
    @change: 2008-05-19: mime type issue on OSX reported by "Matthew Sherborne" <msherborne@gmail.com>
    @change: 2008-05-20: added the ability to run javascript through "Dean Edwards" packer
"""

from cherrypy import response, HTTPError, request, HTTPRedirect
from jsmin import JavascriptMinify
from jspacker import JavaScriptPacker
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
CacheTimeOut = int(config.get('combine.timeout', 10)) #: DEfault 10 days  -  Cache timeout in days ex: 0.5 = 12hrs
MinifyMode = config.get('combine.minify', "all") #: Minify Mode
ProjectMode = config.get('server.environment', 'development') #: project mode
JSPack = config.get("combine.pack_javascript", False) # run JS through packer (Disable if javascript errors occur)  

FileType = re.compile(".*?(css|javascript).*") #: check the mimetype to see which file type we are dealing with

def doMinify():
    """ check if minify should be used """
    if MinifyMode == "all":
        return True
    return MinifyMode == ProjectMode

def cssMinify(css):
    """
    CSS file compressor
    @param css: the css string to compress 
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
        """ simple page handler """
        return self.index(pagename)
    
    @expose()
    def index(self, files=None, *kw):
        """ main request handler """
        if not kw and not files:
            raise HTTPError(400, 'No files specified')
        if not files:
            files = kw[0]
        
        fileMime = ""
        types = {'javascript': JSFolder, 'css': CSSFolder}
        
        
        Files = [f for f in files.split(',') if f]
        fname = files.replace(',', '-').replace("/", "_")
        try:
            mime = mimetypes.types_map[path.splitext(Files[0])[1]]
        except KeyError:
            raise HTTPError(400, 'mime type not supported')
        
        if FileType.search(mime):
            fileMime = FileType.search(mime).groups()[0]
        
        if fileMime not in types:
            raise HTTPError(400, 'mime type not supported')      
        
        response.headers['Content-Type'] = mime
        response.headers['Expires'] = (DateTime.now() + CacheTimeOut).strftime("%a, %d %b %y %X GMT") 
        response.headers['Last-Modified'] = DateTime.now().strftime("%a, %d %b %y %X GMT") 
        
        modified_check = request.headers.get('If-Modified-Since', None)
        
        cache = CacheFolder
        location = Scriptbasedir        
        static = path.join (location, types[fileMime])
        
        if cache and path.exists(cache):
            cacheFile = "%s/%s" % (cache, fname)
            if path.exists(cacheFile):
                lastMod = 0
                if ProjectMode != "production": #: dev mode lets check for file changes
                    for reqFile in Files:
                        floc = "%s/%s" % (static, reqFile)
                        if path.exists(floc) and path.getmtime(floc) > lastMod:
                            lastMod = path.getmtime(floc)
                if path.getmtime(cacheFile) >= lastMod:
                    if modified_check and DateTime.DateFrom(path.getmtime(cacheFile)) <= DateTime.DateFrom(modified_check):
                            raise HTTPRedirect("", 304)
                    return open(cacheFile).read()

        
        ret = StringIO.StringIO()
        for cfile in Files:
            if path.exists(path.join(static, cfile)):
                ret.write(open(path.join(static, cfile), 'r').read())
        ret.seek(0)
        
        if doMinify():
            if fileMime == 'javascript':
                out = StringIO.StringIO()
                jsm = JavascriptMinify()
                jsm.minify(ret, out)
                out.seek(0)
                ret = out.read()
                if JSPack:
                    packer = JavaScriptPacker()
                    ret = packer.pack(ret, compaction=False, encoding=62, fastDecode=True)
                    
            elif fileMime == 'css':
                ret = cssMinify(ret.read())
        else:
            ret = ret.read()
        
        if cache:
            cacheFile = open(path.join(cache, fname), 'w')
            cacheFile.write(ret)
            cacheFile.close()
        
        return ret
    