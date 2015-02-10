import ctypes
import multiprocessing as mp
import os

from indexer import Indexer
from loader import Loader
from stitcher import Stitcher
from view import View

class Manager(object):

  def __init__(self, input_dir):
    '''
    '''
    self._input_dir = input_dir
    self._indexer = Indexer()

    self._no_workers = mp.cpu_count() - 1
    self._active_workers = mp.Queue(self._no_workers)

    self._loading_queue = []#mp.Queue()
    self._viewing_queue = []

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
    # add the first sections to the viewing queue
    #
    first_section = View(sections[0]._tiles)
    self._viewing_queue.append(first_section)

    #
    # start loading one
    #
    while 1:
      self.process()

  def onLoad(self, tile):
    '''
    '''
    print 'loaded', tile
    # print 'Loaded', tile._mipmapLevels["0"]['imageUrl'], Loader.shmem_as_ndarray(tile._memory)[0:1000]
    self._active_workers.get() # reduce worker counter


  def onStitch(self, view):
    '''
    '''
    print 'stitched', view
    self._active_workers.get() # reduce worker counter

  def process(self):
    '''
    Starts loading the next section.
    '''
    # do nothing while workers are not available
    if self._active_workers.full():
      return

    #
    # here we have at least 1 worker available
    #

    #
    # viewing has higher priority, so check if we have anything
    # in the viewing queue
    #
    if len(self._viewing_queue) != 0:
      # check if we have the tiles required for this view
      view = self._viewing_queue[0]
      allLoaded = True
      for tile in view._tiles:
        if tile._status.isVirgin():
          # we need to load this tile
          tile._status.loading()
          self._loading_queue.append(tile)
          allLoaded = False
          print 'We need tile', tile
        elif tile._status.isLoading():
          # the tile is still loading
          allLoaded = False
          

      if allLoaded:
        #
        # we have all the tiles and
        # now we can stitch the view
        #
        view = self._viewing_queue.pop(0)
        print 'starting view', view

        # now it is time to calculate the bounding box for this view
        bbox = View.calculateBB(view._tiles, view._zoomlevel)
        view._bbox = bbox # re-attach the bounding box (since something could have changed)

        # allocate shared mem for view
        memory = mp.RawArray(ctypes.c_ubyte, bbox[1]*bbox[3])
        view._memory = memory # we need to keep a reference
        view._imagedata = Stitcher.shmem_as_ndarray(memory)

        # start worker
        args = (self, view)
        worker = mp.Process(target=Stitcher.run, args=args)
        self._active_workers.put(1) # increase worker counter
        worker.start()
        return # jump out

    #
    # loading has lower priority
    # check if we have anything in the loading queue
    #
    if len(self._loading_queue) != 0:
      tile = self._loading_queue.pop(0)

      # allocate shared mem for tile
      memory = mp.RawArray(ctypes.c_ubyte, tile._bbox[1]*tile._bbox[3])
      tile._memory = memory # we need to keep a reference
      tile._imagedata = Loader.shmem_as_ndarray(memory)

      # start worker
      args = (self, tile)
      worker = mp.Process(target=Loader.run, args=args)
      self._active_workers.put(1) # increase worker counter
      worker.start()
      return # jump out


