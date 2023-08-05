import pocketwsgi
from wsgiref.simple_server import make_server

@pocketwsgi.expose('/')
def hello(errors=None):
    name = pocketwsgi.request.params.get('name', 'pocketwsgi')
    return pocketwsgi.renderer.render('hello.html', name=name)

httpd = make_server('', 8000, pocketwsgi.application)
print "Serving HTTP on port 8000..."
httpd.serve_forever()
