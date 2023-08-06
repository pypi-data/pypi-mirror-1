import berry
from wsgiref.simple_server import make_server

@berry.get('^$')
def index(req):
  return "Welcome to the home page."

@berry.get('^hello/(.+)/?$')
def hello(req, name):
  return "Hello, %s!" % name

# generate a WSGI app
wsgi_app = berry.app()

# start a WSGI server
make_server('localhost', 3000, wsgi_app).serve_forever()