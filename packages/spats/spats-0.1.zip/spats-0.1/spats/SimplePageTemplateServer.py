# spats  |  Copyright(C), 2004-2007, Enfold Systems, LLC
#
#
# Enfold Systems, LLC
# 4617 Montrose Blvd., Suite C215
# Houston, Texas 77006 USA
# p. +1 713.942.2377 | f. +1 832.201.8856
# www.enfoldsystems.com
# info@enfoldsystems.com
#
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from simpletal import simpleTAL, simpleTALES
from tempfile import mkstemp

import threading
import os
import sys
import traceback
import imp
import cgi
import time
import urlparse
import socket
import traceback
import errno
import logging

from exceptions import Exception
class Unauthorized(Exception): pass

from StringIO import StringIO

from formats import getFormats, getOrder

logger = logging.getLogger("spats")

_config = {}

def _getDefaultConfig(spats_dir):
    return {
    # root_dir is where all relative URLs will be resolved against.
    # eg config['html_dir'] = ['foo', 'bar'] - root/foo and root/bar will
    # be searched.
    # If not specified, it is the directory of the 'executable'.
    "root_dir": os.path.dirname(os.path.abspath(sys.argv[0])),
    # is anonymous access allowed
    "anon_access":True,
    # auth_methods
    # not actually implemented yet
#    "auth_methods":["pwd_file",],
    # the root html or page template directory, everything is served out of here
    "html_dir":["html",],
    # the base directory where common css and other files can be stored
    "base_dir":"%s/base" % spats_dir,
    # what to show when it goes wrong
    "error_pages":{
        "500":"%s/errors/500.pt" % spats_dir,
        "302":"%s/errors/302.pt" % spats_dir,
        "403":"%s/errors/403.pt" % spats_dir,
        "404":"%s/errors/404.pt" % spats_dir
        },
    # what scripts will get compiled in
    "scripts_dir":["scripts",],
    # first page to show
    "default_pages":["index.html", "index.htm", "index.pt"],
    # what templates contain macros and need compiling
    "macros_templates":["base/template.pt",],
    # a chance to throw more stuff into the context here
    "extra_context":None,
    # run in debug_mode, slower but refreshes scripts
    "debug_mode":True,
    # plugins directory
    "plugins_dir":[],
    }

def importModule(location):
    name = os.path.basename(location).split('.')[0]
    path = os.path.dirname(location)
    paths = [path,]

    triple = imp.find_module(name, paths)

    for path in paths:
        if path not in sys.path:
            sys.path.append(path)

    mod = imp.load_module(name, *triple)

    return mod

_scripts = None
_templates = None

def parse_qs(data):
    old = cgi.parse_qs(urlparse.urlsplit(data)[3])
    new = {}
    for k, v in old.items():
        if len(v) ==  1:
            v = v[0]
        # We would normally expect utf8 encoded strings, but they are
        # apparently encoded in 'ISO-8859-1', the default for simpleTAL.
        # decode here so values are always Unicode, and no confusion
        # about the encoding can exist inside the templates.
        # ack - multiple variables can be specified, in which case we get a
        # list.
        if not hasattr(v, "decode"):
            v = [val.decode('ISO-8859-1') for val in v]
        else:
            v = v.decode('ISO-8859-1')
        new[k] = v
    return new

def iterate_plugins(dirs, config):
    magic = "plugin.py"
    for directory in dirs:
        if not os.path.exists(directory):
            continue
        listing = os.listdir(directory)
        for subdir in listing:
            plugindir = os.path.join(directory, subdir)
            if os.path.isdir(plugindir):
                # found plugins/etc
                if magic in os.listdir(plugindir):
                    # bingo
                    plugin = os.path.join(plugindir, magic)
                    try:
                        mod = importModule(plugin)
                    except ImportError, msg:
                        raise
                    if hasattr(mod, "__call__"):
                        # call plugin.py passing in the config
                        
                        config = mod.__call__(config)

    return config

class SimplePageTemplateHandler(SimpleHTTPRequestHandler):
    temp_files = []
    custom_headers = {}

    def getScripts(self, context):
        """ Figure out all the scripts, we'll do this once on first request """
        global _scripts

        for dr in _config['scripts_dir']:
            scripts_dir = os.path.abspath(dr)
            if not os.path.isdir(scripts_dir):
                logger.warning("Script directory '%s' does not exist",
                               scripts_dir)
                continue

            # importModule() above adds all paths to sys.path - but only
            # as a module is imported.  This means things may fail to import
            # depending on the order sys.path is changed.  We avoid that by
            # adding *all* script dirs to sys.path before starting the
            # import of any of them.
            if scripts_dir not in sys.path:
                logger.debug("Adding %r to sys.path", scripts_dir)
                sys.path.append(scripts_dir)

            # This code doesn't play well with classes - so all such code may
            # exist in a "lib" subdir.
            scripts_lib_dir = os.path.join(scripts_dir, "lib")
            if os.path.isdir(scripts_lib_dir) and scripts_lib_dir not in sys.path:
                sys.path.append(scripts_lib_dir)

        # cache all the imported scripted, unless we are in debug mode
        if _scripts is None or _config['debug_mode']:
            scripts = {}
            for dr in _config['scripts_dir']:
                dr = os.path.abspath(dr)
                if not os.path.exists(dr):
                    # if the dir doesn't exist, skip over
                    continue
                for file in os.listdir(dr):
                    if file.endswith('.py'):
                        name = file.split('.py')[0]
                        mod = None
                        if name.startswith('.'):
                            continue
                        try:
                            mod = importModule(os.path.join(dr, name))
                        except ImportError, msg:
                            if _config['debug_mode']:
                                # if we are in debug-mode, just move on, don't cry about it
                                print "** Failed to import %s, %s" % (file, msg)
                                continue
                            else:
                                raise
                        if hasattr(mod, "__call__"):
                            scripts[name] = mod
            _scripts = scripts
        # add in a changing context, so each invocation gets a new context
        _n_scripts = {}
        for k, v in _scripts.items():
            # insert context
            # make key the __call__ method
            v.context = context
            v.self = self
            _n_scripts[k] = v.__call__
        return _n_scripts

    def getTemplates(self):
        """ Get the templates """
        global _templates
        if _templates is None or _config['debug_mode']:
            templates = {}
            for t in _config['macros_templates']:
                # join works correctly if 2nd arg already absolute!
                t = os.path.normpath(os.path.join(_config['root_dir'], t))
                if t.endswith('.pt'):
                    name = os.path.basename(t).split('.pt')[0]
                    templateFile = open(t, 'rb')
                    logger.debug('Compiling template %r', t)
                    macros = simpleTAL.compileHTMLTemplate (templateFile)
                    templateFile.close()
                    templates[name] = macros
            _templates = templates
        return _templates

    def getContext(self, **kw):
        """ Figure out the context """
        # Trying to cache this does not make sense
        # since headers and options will change for each request
        context = simpleTALES.Context(allowPythonPath=1)
        context.addGlobal(
                "request", {
                    "headers":self.headers,
                    "query":parse_qs(self.path),
                    "url":self.path.split('?')[0]
                    }
        )

        context.addGlobal("macros", self.getTemplates())
        context.addGlobal("scripts", self.getScripts(context))
        if _config["extra_context"]:
            for k, v in _config["extra_context"].items():
                context.addGlobal(k, v)

        # always add in last error
        t, v, tb = sys.exc_info()
        kw["err_type"] = str(t)
        kw["err_value"] = str(v)
        strtb = StringIO()
        traceback.print_tb(tb, limit=50, file=strtb)
        kw["err_tb"] = strtb.getvalue()
        context.addGlobal("options", kw)
        return context

    def processPT(self, path, **kw):
        """ Process the path into a page template """
        # open up pt
        self.check_security()
        templateFile = open (path, 'rb')
        template = simpleTAL.compileHTMLTemplate (templateFile)
        templateFile.close()

        # write out to temp
        fd, out = mkstemp()
        os.close(fd)
        outfile = open(out, "wb")
        context = self.getContext(**kw)
        template.expand(context, outfile)
        outfile.close()

        return out

    def reset(self):
        self.custom_headers = {}
        self.temp_files = []

    def check_security(self):
        if not self._check_security:
            return

        if _config['anon_access']:
            return

        # implement ip checking
        # implement other checks
        raise Unauthorized

    def do_HEAD(self, *args, **kw):
        """ Perfom security """
        self.reset()
        SimpleHTTPRequestHandler.do_HEAD(self, *args, **kw)

    def do_GET(self, *args, **kw):
        """ The base class throws around files, we need to use temp files
        for page templates, this cleans them up and perform security"""
        self.reset()
        self._check_security = True
        try:
            f = self.send_head()
        except Unauthorized:
            f = self.send_error(403)
        except SystemExit:
            f = self.send_error(500, "The application is now shutting down")
            self.server.stop()
        except:
            logger.exception("Unhandled error rendering '%s'", self.requestline)
            f = self.send_error(500)

        # and what does this mean?
        assert(f != None)

        if f:
            self.copyfile(f, self.wfile)
            f.close()
        while self.temp_files:
            t = self.temp_files.pop()
            try:
                os.remove(t)
            except OSError, why:
                # let the os clean it then
                logger.warning("Failed to remove temp file '%s': %s", t, why)

    # send base class logging to a real logger.
    def log_request(self, code='-', size='-'):
        logger.debug('"%s" %s %s', self.requestline, str(code), str(size))

    def log_message(self, format, *args):
        logger.info(format, *args)

    def log_error(self, format, *args):
        logger.error(format, *args)

    def send_error(self, error, message=None):
        """ Send an error down the pipe """
        errors = _config["error_pages"]
        if str(error) in errors.keys():
            self._check_security = False
            return self.send_head(
                path=errors[str(error)],
                status_code=error,
                )
        raise ValueError, "Unknown error code: %s"  % error

    def add_header(self, k, v):
        """ Add in a header """
        hs = self.custom_headers.get(k, [])
        hs.append(v)
        self.custom_headers[k] = hs

    def send_head(self, path=None, status_code=200):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do. """
        # allow path to be forced
        if path is None:
            path = self.path
            assert path.find('..') < 0, "You cannot pass .. in the URL"

            # look through all the html directories
            for dr in _config['html_dir']:
                p = path
                if not p.startswith('%s/' % dr):
                    p = dr + p
                p = p.split('?')[0]
                if os.path.exists(p):
                    path = p
                    break
            #finally look in base if not there
            if not os.path.exists(path) and _config['base_dir']:
                path = _config['base_dir'] + self.path
                path = path.split('?')[0]

        # if we have a path, we have to start looking
        # through the html_dirs to find a default
        f = None
        if os.path.isdir(path):
            # Why go off searching paths again - surely the default doc
            # must be in the dir specified???
            for dr in _config['html_dir']:
                # print "Looking for page in", dr
                found = 0
                if os.path.isdir(dr):
                    # this is faster if you only have one/
                    for index in _config['default_pages']:
                        index = os.path.join(dr, index)
                        if os.path.exists(index):
                            path = index
                            found = 1
                            break
                if found:
                    break

        if path.endswith('.pt') or path.endswith('.ptx'):
            # do we check security, before processing this
            fpath = self.processPT(path)
            # register temp file
            self.temp_files.append(fpath)
            ctype = 'text/html'
            if path.endswith('.ptx'):
                ctype = 'text/xml'
        else:
            fpath = path
            ctype = self.guess_type(path)

        # If mode != 'rb', then we can't use stat to get the content-length
        # (as size on disk may not == number of \n translated bytes).
        # For now let the client deal with \n issues.
        mode = 'rb'
        try:
            f = open(fpath, mode)
        except IOError:
            raise
            return self.send_error(404)

        # write out the headers
        self.send_response(status_code)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))

        # allow a script to add in custom headers
        if self.custom_headers:
            for k, v in self.custom_headers.items():
                if isinstance(v, list):
                    for r in v:
                        self.send_header(k, r)
                else:
                    self.send_header(k, v)
        self.end_headers()

        # what does this mean?
        assert f != None
        return f

    def list_directory(self, path):
        """ Override directory listings in higher class """
        self.send_error(403, "You are not allowed to list the contents of this directory.")

class SpatsHTTPServer(HTTPServer):
    def __init__(self, *args):
        # assume we will start, and prevent issues with
        # the main thread checking before it is set.
        self.running = True
        HTTPServer.__init__(self, *args)

    def serve(self):
        # Run until stop() is called.
        self.running = True
        try:
            try:
                # Re rely on a timeout to prevent this blocking.
                while self.running:
                    self.handle_request()
            except SystemExit:
                pass
            except:
                logger.exception("Unexpected exception in spats server")
        finally:
            self.running = False

    def stop(self):
        # later we may need to do something fancier.
        self.running = False

# find a free port
def freePort(server, port):
    # 1.5 seconds should be enough to get a response
    # from most local servers
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(1.5)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            s.connect((server, port))
        except socket.error, exc:
            # Be careful not to mask real errors (such as invalid server string!)
            # We expect either 'conection refused' (ie, no one on the port), or
            # 'timed out' (ports in 'stealth' mode - no active error, just failure
            # to do anything)
    #        if exc[0] not in (errno.ECONNREFUSED, errno.ETIMEDOUT):
    #            raise
            # still makes no sense to me, basically the above code
            # means that spats never actually runs
            # on my box exc[0] is "timed out". that is not in
            # errno.ECONNREFUSED (10061)
            # errno.ETIMEDOUT (10060)
            # let's check what we get here
            s.close()
            return 1
        return 0
    finally:
        socket.setdefaulttimeout(old_timeout)

def start(config=None, server_address=None, format=None,
          spats_dir=None, handler=None):
    # spats_dir is where data files that ship with 'spats' are shipped.
    # By default this is the directory of the Python spats package
    # (ie, this dir)
    if not spats_dir:
        spats_dir = os.path.dirname(os.path.abspath(__file__))
        # If not with source-code, use sys.prefix, which is where distutils puts them.
        if not os.path.isdir(os.path.join(spats_dir, "base")):
            spats_dir = os.path.join(sys.prefix, 'spats')
    assert os.path.isdir(spats_dir), spats_dir

    # Fixup global config.
    # Update the global dict with our values.
    _config.update(_getDefaultConfig(spats_dir))

    # set defaults
    if server_address is None:
        # erm - an empty string for the host name will cause Windows firewall
        # to warn about the application.  '127.0.0.1' avoids the firewall, but
        # appears to not be in the IE6 "trusted sites" on Windows 2003 server,
        # while "http://localhost' explicitly is.  So we use 'localhost' to
        # avoid both issues.
        server_address = ('localhost', 8180)

    if format is None:
        # default order set in formats...
        format = getOrder()

    # _config is a global
    if config:
        for k, v in config.items():
            _config[k] = v

    # init plugins
    if _config.get("plugins_dir", []):
        _config.update(
            iterate_plugins(_config["plugins_dir"], 
                _config)
            )

    # help directory
    if 'help_dir' not in _config:
        # ack - this is suspect and only works for EP.  ES specifies help_dir
        if hasattr(sys, "frozen"):
            _config['help_dir'] = os.path.abspath(_config['root_dir'])

        elif ('extra_context' in _config and 
              'install_dir' in _config['extra_context']):
            # For Enfold Server, the help file is located in the 'install_dir'.
            _config['help_dir'] = _config['extra_context']['install_dir']
        else:
            # source builds should find the .chm file directly where
            # it is built.
            _config['help_dir'] = os.path.abspath(
                os.path.join(_config['root_dir'], '..', 'docs', 'public'))
    # The name of the help file is in the link - but both EP and ES
    # use 'Help.chm' so we might as well check for that here.
    if not os.path.exists(os.path.join(_config['help_dir'], "Help.chm")):
        print "Warning: Help file does not exist in " + _config['help_dir']

    server, port = server_address
    # give this 50 attempts
    for x in range(0, 50):
        res = freePort(server, port)
        if res:
            break
        # note we cumulative add for the hell of it
        port += x

    server_address = server, port
    logger.debug("Local server address is %s", server_address)

    # allow the handler to be overridden easily
    if handler is None:
        handler = SimplePageTemplateHandler
    
    httpd = SpatsHTTPServer(server_address, handler)
    httpd._config = _config

    t = threading.Thread(target = httpd.serve)
    t.setDaemon(True)
    t.start()

    # call each of the formats in the requested order
    # if something dies, yell
    try:
        formats = getFormats()
        for fmt in format:
            if fmt in formats: # if format available...
                try:
                    # Hack in support for a custom title
                    try:
                        pn = _config['extra_context']['product_name']
                    except KeyError:
                        pass
                    else:
                        formats[fmt].title = 'encontrol - ' + pn
                    # And ask it to start.
                    formats[fmt].__call__(server_address, httpd)
                    break
                except:
                    print "** Calling %s failed" % fmt
                    if config["debug_mode"]:
                        raise
        else:
            print "** Failed to find a suitable host application **"
            print "The requested format is", format
    finally:
        httpd.stop()
        t.join(2) # ack - our server doesn't shut down correctly :(
        if t.isAlive():
            logger.warning("Server thread did not stop")

if __name__=='__main__':
    pass
