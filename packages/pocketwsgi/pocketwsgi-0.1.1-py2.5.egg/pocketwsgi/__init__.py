#
import os
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

application = selector.Selector()

def weboblize(func):
    def decorator(environ, start_response):
        set_thread_environ(environ)
        url_vars = environ.get('wsgiorg.routing_args', [[], {}])
        res = func(*url_vars[0], **url_vars[1])
        return res(environ, start_response)
    return decorator 

def expose(pattern, method='GET', auth=False):
    def wrap(func):
        newfunc = weboblize(func)
        application.add(pattern, **{method:newfunc})
        newfunc.basefunc = func
        return newfunc
    return wrap

def validate(validator, error_handler):
    def wrap(func):
        def decorator(*args, **kwargs):
            try:
                params = validator.to_python(request.params)
                request.environ['form_result'] = params
                return func(*args, **kwargs)
            except formencode.Invalid, e:
                return error_handler.basefunc(errors=e.error_dict)
        return decorator
    return wrap

class Renderer(object):
    def __init__(self):
        self.templatedir = os.getcwd()
        self.templateValues = dict(request=request)

    def render(self, template, **kwargs):
        res = webob.Response()
        tmpl = tempita.HTMLTemplate.from_filename(os.path.join(self.templatedir, template))
        kwargs = kwargs.copy()
        kwargs.update(self.templateValues)
        res.body = tmpl.substitute(**kwargs)
        return res

renderer = Renderer()

