import ctypes
import multiprocessing as mp
import os

from indexer import Indexer
from loader import Loader

class Manager(object):

  def __init__(self, input_dir):
    '''
    '''
    self._input_dir = input_dir
    self._indexer = Indexer()

    self._no_workers = 6#mp.cpu_count()

    self._active_workers = mp.Queue(self._no_workers)

    self._loading_queue = []#mp.Queue()
    self._viewing_queue = []
    self._memories = []

  def start(self):
    '''
    '''
    print 'Starting manager with', self._no_workers, 'workers.'

    #
    # index all JSONs
    #
    sections = self._indexer.index(self._input_dir)

    print 'Indexed', len(sections), 'sections.'


    #
    # add the first sections to the loading queue
    #
    # for i in range(self._no_workers):
    # self._loading_queue.append(sections[0]._tiles[i])
    self._viewing_queue.append(sections[0]._tiles)

    #
    # start loading one
    #
    while 1:
      self.process()

  def onLoad(self, loader_id, tile):
    '''
    '''
    print tile
    # print 'Loaded', tile._mipmapLevels["0"]['imageUrl'], Loader.shmem_as_ndarray(tile._memory)[0:1000]
    self._active_workers.get() # reduce worker counter


  def process(self):
    '''
    Starts loading the next section.
    '''
    # do nothing while workers are not available
    if self._active_workers.full():
      # print 'busy'
      return

    # viewing
    if len(self._viewing_queue) != 0:
      # check if we have the tiles
      view = self._viewing_queue[0]
      allLoaded = True
      for tile in view:
        if tile._status.isVirgin():
          # we need to load this tile
          tile._status.loading()
          self._loading_queue.append(tile)
          allLoaded = False
          print 'We need tile', tile
        elif tile._status.isLoading():
          # print 'Still waiting for', tile
          allLoaded = False
          # print 'loading', tile._status._code
          # elif tile._status.isLoaded():
          # we already have this tile
        # elif tile._status.isLoaded():
          

      if allLoaded:
        print 'We are ready to stitch', view

      # if self._active_workers.empty():
        # print 'yap'
      # else:
        # print 'no'

      # return


    # loading
    if len(self._loading_queue) != 0:
      tile = self._loading_queue.pop(0)

      

      # allocate shared mem for tile
      memory = mp.RawArray(ctypes.c_ubyte, tile._bbox[1]*tile._bbox[3])
      tile._memory = memory # we need to keep a reference
      tile._imagedata = Loader.shmem_as_ndarray(memory)

      # print 'Allocated', memory

      
      print 'starting worker', tile
      # start worker
      args = (self, 0, tile)
      worker = mp.Process(target=Loader.run, args=args)
      self._active_workers.put(1) # increase worker counter
      worker.start()



