import sys

from tile import Tile

class Section:

  def __init__(self):

    '''
    '''
    self._id = None
    self._tiles = None
    self._bbox = None
    self._data_prefix = None

  def __str__(self):
    '''
    '''
    return 'Section ' + str(self._id)


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

    return new_section

