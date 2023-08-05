#
import os
import re
import threading
import tempita
import webob
import selector
import formencode

environments = threading.local()
def get_environ():
    if hasattr(environments, 'environ'):
        return environments.environ
    else:
        return webob.Request.blank('').environ


def set_thread_environ(environ):
    environments.environ = environ


request = webob.Request(environ_getter=get_environ)

def forward(app):
    return request.get_response(app)

def wsgiapplication(useposargs=False):
    def decorator(appfunc):
        def wrap(environ, start_response):

            pos,named = environ.get('wsgiorg.routing_args', ((), {}))
            print pos, named
            if pos and named and useposargs:
                body = appfunc(*pos, **named)
            elif pos:
                body = appfunc(*pos)
            elif named:
                body = appfunc(**named)
            else:
                body = appfunc()

            if isinstance(body, webob.Response):
                return body(environ, start_response)
            else:
                start_response('200 OK',
                               [('content-type', 'text/html')])
                return body
        return wrap
    return decorator

class RegexDispatcher(object):
    def __init__(self):
        self.urls = []
                     
    def dispatchon(self, pattern, method=None):
        p = re.compile(pattern)
        def decorator(app):
            self.urls.append((p, app, method))
            return app
        return decorator

    def __call__(self, environ, start_response):
        scriptname = environ['SCRIPT_NAME']
        pathinfo = environ['PATH_INFO']
        requestmethod = environ['REQUEST_METHOD']
        for pattern, app, method in self.urls:
            m = pattern.match(pathinfo)
            if not m:
                continue
            extra_pathinfo = pathinfo[m.end():]
            if extra_pathinfo and not extra_pathinfo.startswith('/'):
                continue
            if method is not None and requestmethod != method:
                return self.method_not_allowed(environ, start_response)
            pos, named = environ.get('wsgiorg.routing_args', ((), {}))
            new_pos = list(pos) + list(m.groups())
            new_named = named.copy()
            new_named.update(m.groupdict())
            environ['wsgiorg.routing_args'] = (new_pos, new_named)
            environ['PATH_INFO'] = extra_pathinfo
            environ['SCRIPT_NAME'] = scriptname + pathinfo[:m.end()]
            environ['pocketwsgi.app_base'] = scriptname
            set_thread_environ(environ)
            response = request.get_response(app)
            return response(environ, start_response)

        return self.not_found(environ, start_response)

    def not_found(self, environ, start_response):
        response = webob.Response(status='404 resource not found')
        response.body = '404 resource not found'
        return response(environ, start_response)
        

    def method_not_allowed(self, environ, start_response):
        response = webob.Response(status='405 method not allowed')
        response.body = '405 method not allowed'
        return response(environ, start_response)
        

class Renderer(object):
    def __init__(self):
        self.templatedir = os.getcwd()
        self.templateValues = dict(request=request)

    def render(self, template, **kwargs):
        tmpl = tempita.HTMLTemplate.from_filename(os.path.join(self.templatedir, template))
        kwargs = kwargs.copy()
        kwargs.update(self.templateValues)
        return webob.Response(body=tmpl.substitute(**kwargs))

application = RegexDispatcher()
renderer = Renderer()

