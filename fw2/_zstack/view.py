import ctypes
import sys

from status import Status

class View(object):

  def __init__(self, tiles, zoomlevel=0):
    '''
    '''
    self._status = Status()
    self._tiles = tiles
    self._bbox = None
    self._zoomlevel = zoomlevel
    self._memory = None
    self._imagedata = None


  def __str__(self):

    return 'View ' + str(self._zoomlevel)




  @staticmethod
  def calculateBB(tiles, zoomlevel=0):
    '''
    '''

    width = 0
    height = 0

    minX = sys.maxint
    minY = sys.maxint

    divisor = 2**zoomlevel

    for t in tiles:

      tile_width = t._real_width / divisor
      tile_height = t._real_height / divisor

      offset_x = 0
      offset_y = 0

      for transform in t._transforms:

        offset_x += transform.x
        offset_y += transform.y

      offset_x /= divisor
      offset_y /= divisor

      # print offset_x, offset_y, minX, minY

      minX = min(minX, offset_x)
      minY = min(minY, offset_y)

      width = max(width, tile_width+offset_x)
      height = max(height, tile_height+offset_y)

    width = int(width-minX) + 1
    height = int(height-minY) + 1

    # print 'mins', minX, minY

    return [minX, width, minY, height]
