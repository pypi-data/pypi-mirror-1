"""
decoupage: a view with webob
"""

import os

from genshi.builder import Markup
from genshi.template import TemplateLoader
from martini.config import ConfigMunger
from paste.urlparser import StaticURLParser
from pkg_resources import iter_entry_points
from webob import Request, Response, exc

class Decoupage(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'configuration': None,
                 'directory': None,
                 'cascade': True, # TODO
                 'template': 'index.html',
                 }

    def __init__(self, **kw):
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = self.auto_reload.lower() == 'true'
        from pkg_resources import resource_filename
        if not os.path.isabs(self.template):
            self.template = os.path.join(resource_filename(__name__, 'templates'), self.template)
        assert os.path.exists(self.template)
        assert os.path.isdir(self.directory)
        self.loader = TemplateLoader(auto_reload=self.auto_reload)
        self.fileserver = StaticURLParser(self.directory)
        self.formatters = {}
        for formatter in iter_entry_points('decoupage.formatters'):
            try:
                _formatter = formatter.load()
            except:
                continue
            self.formatters[formatter.name] = _formatter

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)
        filename = request.path_info.strip('/')
        path = os.path.join(self.directory, filename)
        if os.path.exists(path):
            if os.path.isdir(path):
                res = self.get(request)
                return res(environ, start_response)
            else:
                return self.fileserver(environ, start_response)
        else:
            raise exc.HTTPNotFound()

    def get_response(self, text, content_type='text/html'):
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
        ini_path = os.path.join(directory, 'index.ini')
        conf = {}
        if os.path.exists(ini_path):
            _conf = ConfigMunger(ini_path).dict()
            if len(_conf) == 1:
                conf = _conf[_conf.keys()[0]].copy()
        if not conf and os.path.exists(self.configuration):
            conf = ConfigMunger(self.configuration).dict().get('/%s' % path.rstrip('/'), {})

        # add data for the files
        files = []
        for i in os.listdir(directory):
            files.append({'path' : '%s/%s' % (path.rstrip('/'), i),
                          'name': i,
                          'description': conf.get(i, i)})

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
        template = conf.get('/template', self.template)
        if not os.path.isabs(template):
            template = os.path.join(directory, template)
        if not os.path.exists(template):
            template = self.template
        template = self.loader.load(template or self.template)
        res = template.generate(**data).render('html', doctype='html')
        return self.get_response(res)

