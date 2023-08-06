"""
decoupage: a view with webob
"""

import os

from genshi.builder import Markup
from genshi.template import TemplateLoader
from martini.config import ConfigMunger
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from pkg_resources import iter_entry_points
from webob import Request, Response, exc

class Decoupage(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'configuration': None,
                 'directory': None,
                 'cascade': 'True', 
                 'template': 'index.html',
                 }

    def __init__(self, **app_conf):

        # set defaults from app configuration
        kw = self.app_conf('decoupage', app_conf)
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # configure defaults
        self.auto_reload = self.auto_reload.lower() == 'true'
        self.cascade = self.cascade.lower() == 'true'
        if not os.path.isabs(self.template):
            self.template = os.path.join(resource_filename(__name__, 'templates'), self.template)
        assert os.path.exists(self.template)
        self.directory = self.directory.rstrip(os.path.sep)
        assert os.path.isdir(self.directory)
        self.loader = TemplateLoader(auto_reload=self.auto_reload)

        # static file server
        self.fileserver = StaticURLParser(self.directory)

        # pluggable index data formatters
        self.formatters = {}
        self.formatter_args = {}
        for formatter in iter_entry_points('decoupage.formatters'):
            try:
                _formatter = formatter.load()
            except:
                continue
            self.formatters[formatter.name] = _formatter
            self.formatter_args = self.app_conf(formatter.name, app_conf)

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
                return self.fileserver(environ, start_response)
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
        for key, value in conf.items():
            if key.startswith('/'):
                key = key[1:]
                if key in self.formatters:
                    formatter = self.formatters[key](value)
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
        template = self.loader.load(template or self.template)
        res = template.generate(**data).render('html', doctype='html')
        return self.get_response(res)

    ### internal methods

    def conf(self, path):
        """returns configuration dictionary appropriate to a path"""

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

        # cascade configuration
        if self.cascade and path_tuple:
            parent_configuration = self.conf('/%s' % '/'.join(path_tuple[:-1]))
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
