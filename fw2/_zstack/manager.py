import ctypes
import math
import multiprocessing as mp
import os
import sys

from indexer import Indexer
from level import Level
from loader import Loader
from stitcher import Stitcher
from view import View

class Manager(object):

  def __init__(self, input_dir):
    '''
    '''
    self._input_dir = input_dir
    self._indexer = Indexer()

    self._no_workers = mp.cpu_count() - 1 # leave one main process out
    self._active_workers = mp.Queue(self._no_workers)

    self._loading_queue = []#mp.Queue()
    self._viewing_queue = []

    self._views = []

    self._zoomlevels = None

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
    # find zoomlevels by taking the first tile
    # 
    self._zoomlevels = range(int(math.log(sections[0]._tiles[0]._width/512,2)) + 1)

    #
    # add the first sections to the viewing queue
    #
    for i in range(2):
      first_section = View(sections[i]._tiles, self._zoomlevels[-1])
      self._views.append(first_section)
      self._viewing_queue.append(first_section)

    #
    # start loading one
    #
    while 1:
      self.process()

  def onLoad(self, tile):
    '''
    '''
    print 'Loaded', tile
    # print 'Loaded', tile._mipmapLevels["0"]['imageUrl'], Loader.shmem_as_ndarray(tile._memory)[0:1000]
    self._active_workers.get() # reduce worker counter


  def onStitch(self, view):
    '''
    '''
    print 'Stitched', view
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
        tile._status.loading()
        print 'Stitching', view

        # now it is time to calculate the bounding box for this view
        bbox = View.calculateBB(view._tiles, view._zoomlevel)
        # print bbox
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

      #zoomlevels = [0, 1, 2, 3, 4, 5] # TODO dynamically

      # allocate shared mem for tile and for each zoom level
      for z in self._zoomlevels:
        divisor = 2**z
        tile_width = tile._bbox[1] / divisor
        tile_height = tile._bbox[3] / divisor # TODO maybe int?
        memory = mp.RawArray(ctypes.c_ubyte, tile_width*tile_height)
        imagedata = Loader.shmem_as_ndarray(memory)
        tile._levels.append(Level(memory, imagedata))

      # start worker
      args = (self, tile)
      worker = mp.Process(target=Loader.run, args=args)
      self._active_workers.put(1) # increase worker counter
      worker.start()
      return # jump out


