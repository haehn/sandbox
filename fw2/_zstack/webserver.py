import cv2
import os
import socket
import time
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

      (r'/viewer/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__),'../web'))),
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

    request = handler.request.uri.split('/')[-1]

    if request == 'content':
      # must be the table of contents
      content = self._manager.getContent()
      content_type = 'text/json'

    else:
      # must be a tile
      requested_tile = request.split('-')
      zoomlevel = int(requested_tile[0])
      x = int(requested_tile[1])
      y = int(requested_tile[2])
      z = int(requested_tile[3])

      tile = self._manager.get(x, y, z, zoomlevel)

      # right now block until we have the result.. maybe can be solved better
      while tile.shape == (0,):
        # loop = IOLoop.instance()
        # yield gen.Task(loop.add_timeout, time.time() + 5)
        self._manager.process()
        tile = self._manager.get(x, y, z, zoomlevel)
      
      content = cv2.imencode('.jpg', tile[y*512:y*512+512,x*512:x*512+512])[1].tostring()
      content_type = 'image/jpeg'

    # invalid request
    if not content:
      content = 'Error 404'
      content_type = 'text/html'

    handler.set_header('Access-Control-Allow-Origin', '*')
    handler.set_header('Content-Type', content_type)
    handler.write(content)
