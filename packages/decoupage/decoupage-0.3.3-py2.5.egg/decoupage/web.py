"""
decoupage: a view with webob
"""

import os

from formatters import formatters

from genshi.builder import Markup
from genshi.template import TemplateLoader
from martini.config import ConfigMunger
from paste.fileapp import FileApp
from pkg_resources import resource_filename
from pkg_resources import iter_entry_points
from webob import Request, Response, exc

class Decoupage(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'configuration': None,
                 'directory': None, # directory to serve
                 'cascade': 'True', # whether to cascade configuration
                 'template': 'index.html', # XXX see below
                 'template_directories': '' # list of directories to look for templates
                 }

    def __init__(self, **app_conf):

        # set defaults from app configuration
        kw = self.app_conf('decoupage', app_conf)
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # configure defaults
        self.auto_reload = self.auto_reload.lower() == 'true'
        self.cascade = self.cascade.lower() == 'true'
        self.directory = self.directory.rstrip(os.path.sep)
        assert os.path.isdir(self.directory)
        self.template_directories = self.template_directories.split() # no spaces in directory names, for now
        assert sum([os.path.isdir(directory) for directory in self.template_directories]) == len(self.template_directories)

        # static file server
        self.fileserver = FileApp
        
        # pluggable index data formatters
        self.formatters = {}
        for formatter in iter_entry_points('decoupage.formatters'):
            try:
                _formatter = formatter.load()
                template_dir = resource_filename(formatter.module_name, 'templates')
                if template_dir not in self.template_directories and os.path.isdir(template_dir):
                    self.template_directories.append(template_dir)
            except:
                continue # XXX should probably raise
            self.formatters[formatter.name] = _formatter
        
        # template loader
        self.loader = TemplateLoader(self.template_directories, 
                                     auto_reload=self.auto_reload)

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)
        filename = request.path_info.strip('/')
        path = os.path.join(self.directory, filename)
        if os.path.exists(path):
            if os.path.isdir(path):

                if not request.path_info.endswith('/'):
                    raise exc.HTTPMovedPermanently(add_slash=True)

                res = self.get(request)
                return res(environ, start_response)
            else:
                fileserver = self.fileserver(path)
                return fileserver(environ, start_response)
        else:
            raise exc.HTTPNotFound()

    def get_response(self, text, content_type='text/html'):
        """construct a response to a GET request"""
        res = Response(content_type=content_type, body=text)
        return res

    def get(self, request):
        """
        return response to a GET requst
        """
        # ensure a sane path        
        path = request.path_info.strip('/')
        directory = os.path.join(self.directory, path)
        path = '/%s' % path
        
        # get the configuraton
        conf = self.conf(path)

        # add data for the files
        files = []
        for i in os.listdir(directory):
            files.append({'path' : '%s/%s' % (path.rstrip('/'), i),
                          'name': i,
                          'description': conf.get(i.lower(), None)})
        # build data dictionary
        data = {'path': path, 'files': files, 'request': request}

        # apply formatters
        # XXX this should be cached if not self.auto_reload
        if '/formatters' in conf:
            # ordered list of formatters to be applied first
            formatters = [ i for i in conf['/formatters'].split()
                           if i in self.formatters ]
        else:
            formatters = []
        for key in conf:
            if key.startswith('/'):
                key = key[1:]
                if key in self.formatters and key not in formatters:
                    formatters.append(key)
        for name in formatters:
            formatter = self.formatters[name](conf.get('/%s' % name, ''))
            formatter(request, data)


        # render the template
        template = conf.get('/template')
        if template is None:
            if 'index.html' in [ f['name'] for f in files ]:
                template = os.path.join(directory, 'index.html')
            else:
                template = self.template
        if not os.path.isabs(template):
            template = os.path.join(directory, template)
        if not os.path.exists(template):
            template = self.template
        template = self.loader.load(template)
        res = template.generate(**data).render('html', doctype='html')
        return self.get_response(res)

    ### internal methods

    def conf(self, path, cascade=None):
        """returns configuration dictionary appropriate to a path"""
        if cascade is None:
            cascase = self.cascade

        directory = os.path.join(self.directory, path.strip('/'))
        if path.strip('/'):
            path_tuple = tuple(path.strip('/').split('/'))
        else:
            path_tuple = ()

        # return cached configuration
        if hasattr(self, '_conf') and path_tuple in self._conf:
            return self._conf[path_tuple]

        conf = {}

        # local configuration
        ini_path = os.path.join(directory, 'index.ini')
        if os.path.exists(ini_path):
            _conf = ConfigMunger(ini_path).dict()
            if len(_conf) == 1:
                conf = _conf[_conf.keys()[0]].copy()

        # global configuration
        if not conf and self.configuration and os.path.exists(self.configuration):
            conf = ConfigMunger(self.configuration).dict().get('/%s' % path.rstrip('/'), {})

        # inherit and cascade configuration
        inherit_directory = None
        if '/inherit' in conf:
            inherit_directory = conf['/inherit']
        elif self.cascade and path_tuple:
            inherit_directory = '/%s' % '/'.join(path_tuple[:-1])
        if inherit_directory:
            parent_configuration = self.conf(inherit_directory)
            for key, value in parent_configuration.items():
                if key.startswith('/') and key not in conf:
                    conf[key] = value

        # cache configuration
        if not self.auto_reload:
            if not hasattr(self, '_conf'):
                self._conf = {}
            self._conf[path_tuple] = conf

        return conf

    def fmtrs(self, path):
        formatters = []
        for key, value in self.conf(path).items():
            if key.startswith('/'):
                key = key[1:]
                if key in self.formatters:
                    formatter = self.formatters[key](value)        


    def app_conf(self, keystr, app_conf):
        keystr += '.'
        return dict([(key.split(keystr, 1)[-1], value)
                     for key, value in app_conf.items()
                     if key.startswith(keystr) ])        
