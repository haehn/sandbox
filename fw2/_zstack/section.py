import sys

from tile import Tile

class Section:

  def __init__(self):

    '''
    '''
    self._id = None
    self._tiles = None
    self._data_prefix = None

  def __str__(self):
    '''
    '''
    return 'Section ' + str(self._id)


  @staticmethod
  def calculateBB(section, tiles=None, zoomlevel=0):
    '''
    If tiles are None, use all tiles of the section.
    '''

    if not tiles:
      tiles = section._tiles

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

      minX = min(minX, offset_x)
      minY = min(minY, offset_y)

      width = max(width, tile_width+offset_x)
      height = max(height, tile_height+offset_y)

    width = int(width-minX) + 1
    height = int(height-minY) + 1

    return [0, width, 0, height]


  @staticmethod
  def fromJSON(json):
    '''
    '''

    new_section = Section()
    loaded_tiles = []

    for t in json:
      new_tile = Tile.fromJSON(t)
      new_tile._section = new_section

      loaded_tiles.append(new_tile)

    new_section._tiles = loaded_tiles

    # calculate boundingbox for section
    new_section._bbox = Section.calculateBB(new_section)

    return new_section

