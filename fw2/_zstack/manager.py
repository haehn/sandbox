import ctypes
import json
import math
import multiprocessing as mp
import numpy as np
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

    self._sections = None
    self._views = {}

    self._zoomlevels = None

    self._client_tile_size = 512

  def start(self):
    '''
    '''
    print 'Starting manager with', self._no_workers, 'workers.'

    #
    # index all JSONs
    #
    self._sections = self._indexer.index(self._input_dir)

    print 'Indexed', len(self._sections), 'sections.'

    #
    # find zoomlevels by taking the first tile
    # 
    self._zoomlevels = range(int(math.log(self._sections[0]._tiles[0]._width/512,2)) + 1)

    #
    # add the first sections to the viewing queue
    #
    for z in range(2):
      self._views[z] = [None]*len(self._zoomlevels)
      for l in self._zoomlevels[:1:-1]: # but don't queue the two largest zoomlevels yet
        view = View(self._sections[z]._tiles, l)
        self._views[z][l] = view
        self._viewing_queue.append(view)



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


  def getContent(self):
    '''
    Returns a JSON content descriptor.
    '''
    sections = []
    for i,s in enumerate(self._sections):
      s_descriptor = {}
      s_descriptor['width'] = s._bbox[1]
      s_descriptor['height'] = s._bbox[3]
      s_descriptor['layer'] = i
      s_descriptor['minLevel'] = self._zoomlevels[0]
      s_descriptor['maxLevel'] = self._zoomlevels[-1]
      s_descriptor['tileSize'] = self._client_tile_size
      sections.append(s_descriptor)

    return json.dumps(sections)


  def get(self,x,y,z,zoomlevel):
    '''
    Grab data using the client tile format.
    '''
    # check if we have data for this tile
    if not z in self._views:
      self._views[z] = [None]*len(self._zoomlevels)

    view = self._views[z][zoomlevel]

    if not view:
      print 'Did not find view for layer', z, 'and zoomlevel', zoomlevel
      # we still need to load this zoomlevel
      view = View(self._sections[z]._tiles, zoomlevel)
      self._views[z][zoomlevel] = view
      self._viewing_queue.append(view) # add it to the viewing queue
      return np.empty(0) # and jump out

    # here we definitely have a view for this section with the right zoomlevel
    # but we have to check if it was fully loaded yet

    # TODO we need to check if the tiles cover our ROI  

    if view._status.isLoaded():
      # yes, it is - we can immediately get the data
      data = view._imagedata
      bbox = view._bbox
      data = data.reshape(bbox[3], bbox[1])
      return data

    return np.empty(0) # and jump out


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

      for view in self._viewing_queue:

        # check if we have the tiles required for this view
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
          self._viewing_queue.remove(view)
          view._status.loading()
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


