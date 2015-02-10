import cv2
import os
import sys

from status import Status
from transform import Transform

class Tile:
  '''
  '''

  def __init__(self):
    '''
    '''
    self._status = Status()
    self._bbox = None
    self._height = -1
    self._width = -1
    self._real_height = -1
    self._real_width = -1
    self._layer = -1
    self._maxIntensity = -1
    self._minIntensity = -1
    self._mipmapLevels = None
    self._levels = []
    self._transforms = None
    self._section = None
    # self._memory = None
    # self._imagedata = None


  def __str__(self):

    return 'Tile, Layer: ' + str(self._layer) + ' Width: ' + str(self._real_width) + ' Height: ' + str(self._real_height)


  @staticmethod
  def load(tile):
    '''
    Loads image data from disk.
    '''
    # for l in self._mipmapLevels:

    prefix = tile._section._data_prefix

    return cv2.imread(os.path.join(prefix, tile._mipmapLevels["0"]['imageUrl']), cv2.CV_LOAD_IMAGE_GRAYSCALE)


  @staticmethod
  def calculateBB(tile):
    '''
    '''
    width = tile._width
    height = tile._height

    output_width = -sys.maxint
    output_height = -sys.maxint

    for t in tile._transforms:
      bb = t.calculateBB(width, height)
      output_width = max(output_width, bb[0])
      output_height = max(output_height, bb[1])

    return output_width, output_height


  @staticmethod
  def fromJSON(json):

    new_tile = Tile()
    new_tile._bbox = json['bbox']
    new_tile._height = int(json['height'])
    new_tile._width = int(json['width'])
    new_tile._layer = int(json['layer'])
    new_tile._minIntensity = json['minIntensity']
    new_tile._maxIntensity = json['maxIntensity']
    new_tile._mipmapLevels = json['mipmapLevels']
    jsonTransforms = json['transforms']

    new_tile._transforms = Transform.fromJSON(jsonTransforms)

    # re-calculate bounding box for transformed data
    bb = Tile.calculateBB(new_tile)
    new_tile._real_width = bb[0]
    new_tile._real_height = bb[1]
    new_tile._bbox = [0, bb[0], 0, bb[1]]

    return new_tile
