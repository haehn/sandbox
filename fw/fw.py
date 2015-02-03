#!/usr/bin/env python
import ctypes
import multiprocessing as mp
import os
import socket
import sys
import tornado
import tornado.websocket

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

class Worker(object):

  def __init__(self, id):
    '''
    '''
    self.__id = id

  def get(self, zoomlevel, x, y, z):
    '''
    '''
    return None

def work(manager, id, zoomlevel, x, y, z, memory):

  for j in range(100):
    for i in range(512*512):
      memory[i] = i;

  # print 'working', x, y, z
  manager.done(id, memory)


class Manager(object):

  def __init__(self):
    '''
    '''
    self.__workers = []
    self.__memory = []

    for i in range(5):
      memory = mp.RawArray(ctypes.c_ubyte, 512*512)
      print memory
      work_args = (self, i, 6,0,0,i,memory)
      worker = mp.Process(target=work,args=work_args)
      self.__memory.append(memory)
      self.__workers.append(worker)
      worker.start()


  def done(self, id, data):
    '''
    '''
    print id, data, data[1], data[256]

  def get(self, zoomlevel, x, y, z):
    '''
    '''
    content = str(zoomlevel)+'-'+str(x)+'-'+str(y)

    return content




#
# default handler
#
class Handler(tornado.web.RequestHandler):

  def initialize(self, logic):
    self.__logic = logic

  @tornado.web.asynchronous
  @gen.coroutine
  def get(self, uri):
    '''
    '''
    # response = yield self.__logic.handle(self)
    self.__logic.handle(self)


  def post(self, uri):
    '''
    '''
    self.__logic.handle(self)


class ServerLogic:

  def __init__( self, manager ):
    '''
    '''
    self.__manager = manager

  def run( self ):
    '''
    '''

    ip = socket.gethostbyname(socket.gethostname())
    port = 2001

    webapp = tornado.web.Application([

      (r'/viewer/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__),'web'))),
      (r'/data/(.*)', Handler, dict(logic=self))
  
    ])

    

    webapp.listen(port,max_buffer_size=1024*1024*150000)

    print '*'*80
    print '*', '\033[93m'+'ZSTACK RUNNING', '\033[0m'
    print '*'
    print '*', 'open', '\033[92m'+'http://' + ip + ':' + str(port) + '/' + '\033[0m'
    print '*'*80

    tornado.ioloop.IOLoop.instance().start()

  @gen.coroutine
  def handle( self, handler ):
    '''
    '''
    content = None

    #
    #
    #
    

    requested_tile = handler.request.uri.split('/')[-1].split('-')
    zoomlevel = int(requested_tile[0])
    x = int(requested_tile[1])
    y = int(requested_tile[2])

    content = self.__manager.get(zoomlevel, x, y, 0)

    
    content_type = 'text/html'


    # invalid request
    if not content:
      content = 'Error 404'
      content_type = 'text/html'

    # print 'IP',r.request.remote_ip

    handler.set_header('Access-Control-Allow-Origin', '*')
    handler.set_header('Content-Type', content_type)
    handler.write(content)





def print_help( script_name ):
  '''
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line
  '''
  description = ''
  print description
  print
  print 'Usage: ' + script_name + ' INPUT_DIRECTORY OUTPUT_DIRECTORY'
  print


#
# entry point
#
if __name__ == "__main__":

  # always show the help if no arguments were specified
  if len(sys.argv) != 0 and len( sys.argv ) < 3:
    print_help( sys.argv[0] )
    sys.exit( 1 )

  input_dir = sys.argv[1]
  output_dir = sys.argv[2]

  manager = Manager()

  server_logic = ServerLogic(manager)
  server_logic.run()
