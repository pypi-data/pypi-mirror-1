"""
redirector: a view with webob
"""

import re

from genshi.template import TemplateLoader
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename
from urlparse import urlparse
from webob import Request, Response, exc

class Redirector(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'auth': 'False',
                 'date_format': '%c',
                 'path': '.redirect',
                 'redirector': None,
                 'seconds': 5, # seconds for a meta-refresh tag to redirect
                 }

    def __init__(self, app, **kw):
        self.app = app # WSGI app

        # set instance attributes
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.response_functions = { 'GET': self.get,
                                    'POST': self.post,
                                    }
        # bool options
        for var in 'auto_reload', 'auth':
            setattr(self, var, getattr(self, var).lower() == 'true')

        # pick a redirector back end
        assert self.redirector
        if isinstance(self.redirector, basestring):
            name = self.redirector
            self.redirector = iter_entry_points('redirector.redirectors', name=name).next()
            # take first entry point;
            # will raise StopIteration if there are none

            self.redirector = self.redirector.load()
        keystr = name + '.'
        kwargs = dict([(key.split(keystr, 1)[1], value)
                       for key, value in kw.items()
                       if key.startswith(keystr)])
        self.redirector = self.redirector(**kwargs)

        # genshi template loader
        templates_dir = resource_filename(__name__, 'templates')
        self.loader = TemplateLoader(templates_dir,
                                     auto_reload=self.auto_reload)

        # redirect exceptions
        self.status_map = dict([(key, value) 
                                for key, value in exc.status_map.items()
                                if key in set([301, 302, 307])])


    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)

        path = request.path_info.strip('/').split('/')
        if path and path[0] == self.path:
            ### TODO: check if authorized
            res = self.make_response(request)
            return res(environ, start_response)
        else:

            ### query redirection tables
            for redirect in self.redirector.redirects():
                
                _from = redirect['from']
                parsed_url = urlparse(_from)
                if parsed_url[0]:
                    url = request.url
                else:
                    url = request.path_info
                from_re = re.compile(_from)

                # redirect on match
                match = from_re.match(url)
                if match:
                    location = from_re.sub(redirect['to'], url)
                    _type = redirect['type']
                    if isinstance(_type, int):
                        raise self.status_map[_type](location=location)
                    else:
                        res = self.meta_refresh(request, redirect, location)
                        return res(environ, start_response)

            return self.app(environ, start_response)
                                
    def make_response(self, request):
        return self.response_functions.get(request.method, self.error)(request)

    def get_response(self, text, content_type='text/html'):
        res = Response(content_type=content_type, body=text)
        return res

    def get(self, request):
        """
        return response to a GET requst
        """

        data = { 'redirects': self.redirector.redirects(),
                 'status_map': self.status_map,
                 'date_format': self.date_format }

        template = self.loader.load('redirects.html')
        res = template.generate(**data).render('html', doctype='html')
        return self.get_response(res)

    def post(self, request):
        """
        return response to a POST request
        """
        return self.get(request)

    def error(self, request):
        """deal with non-supported methods"""
        return exc.HTTPMethodNotAllowed("Only %r operations are allowed" % self.response_functions.keys())
        

    def meta_refresh(self, request, redirect, location):
        data = { 'request': request,
                 'redirect': redirect,
                 'location': location,
                 'seconds': redirect.get('seconds', self.seconds),
                 'date_format': self.date_format }
        template = self.loader.load('metarefresh.html')
        res = template.generate(**data).render('html', doctype='html')
        return self.get_response(res)
