import socket
import tornado
import tornado.gen
import tornado.web

class WebServerHandler(tornado.web.RequestHandler):

  def initialize(self, webserver):
    self._webserver = webserver

  @tornado.web.asynchronous
  @tornado.gen.coroutine
  def get(self, uri):
    '''
    '''
    self._webserver.handle(self)


class WebServer:

  def __init__( self, manager ):
    '''
    '''
    self._manager = manager

  def start( self ):
    '''
    '''

    ip = socket.gethostbyname('')
    port = 2001

    webapp = tornado.web.Application([

      (r'/data/(.*)', WebServerHandler, dict(webserver=self))
  
    ])

    webapp.listen(port, max_buffer_size=1024*1024*150000)

    print 'Starting webserver at \033[93mhttp://' + ip + ':' + str(port) + '\033[0m'

    tornado.ioloop.PeriodicCallback(self._manager.process, 100).start()
    tornado.ioloop.IOLoop.instance().start()

  @tornado.gen.coroutine
  def handle( self, handler ):
    '''
    '''
    content = None

    # invalid request
    if not content:
      content = 'Error 404'
      content_type = 'text/html'

    handler.set_header('Access-Control-Allow-Origin', '*')
    handler.set_header('Content-Type', content_type)
    handler.write(content)