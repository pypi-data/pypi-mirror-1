Tiny WSGI Framework
============================

PocketWSGI uses below components.

- WebOb
- Tempita
- selector
- FormEncode

Mimimal Example
----------------------------
install:
::

 $ easy_install -f http://aodagx.ddo.jp/aodag/projects/pocketwsgi/downloads/ pocketwsgi

hello.py:
::

 import pocketwsgi

 @pocketwsgi.expose('/')
 def hello(errors=None):

    name = pocketwsgi.request.params.get('name', 'pocketwsgi')
    return pocketwsgi.renderer.render('hello.html', name=name)


 from wsgiref.simple_server import make_server

 httpd = make_server('', 8000, pocketwsgi.application)
 print "Serving HTTP on port 8000..."
 httpd.serve_forever()

hello.html:
::

 <html>
  <body>
    <h1>Hello, {{name}}</h1>
    <form action="/">
      <input type="text" name="name" 
             value="{{request.params.get('name')}}">
      <input type="submit">
    </form>
  </body>
 </hml>

