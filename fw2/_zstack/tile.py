import cv2
import os

from transform import Transform

class Tile:
  '''
  '''

  def __init__(self):
    '''
    '''
    self._bbox = None
    self._height = -1
    self._width = -1
    self._layer = -1
    self._maxIntensity = -1
    self._minIntensity = -1
    self._mipmapLevels = None
    self._mipmap = None
    self._transforms = None
    self._section = None


  def __str__(self):

    return 'Tile, Layer: ' + str(self._layer) + ' Width: ' + str(self._width) + ' Height: ' + str(self._height)


  @staticmethod
  def load(tile):
    '''
    Loads image data from disk.
    '''
    # for l in self._mipmapLevels:

    prefix = tile._section._data_prefix

    return cv2.imread(os.path.join(prefix, tile._mipmapLevels["0"]['imageUrl']), cv2.CV_LOAD_IMAGE_GRAYSCALE)


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

    return new_tile
