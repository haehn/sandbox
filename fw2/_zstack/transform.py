import numpy as np
import sys

class Transform(object):

  def __init__(self, dataString):
    '''
    '''
    self._data = map(float, dataString.split(' '))

  def calculateBB(self, width, height):
    return width, height

  @staticmethod
  def fromJSON(json):

    transforms = []
    
    for t in json:

      transformClass = t["className"].split('.')[-1]

      try:

        transform = eval(transformClass + "('"+t["dataString"]+"')")
        transforms.append(transform)

      except:

        raise Exception('Unsupported transform: ' + t["className"])


    return transforms


class TranslationModel2D(Transform):

  def __init__(self, dataString):
    '''
    '''
    super(TranslationModel2D,self).__init__(dataString)

  @property
  def x(self):
    return self._data[0]

  @property
  def y(self):
    return self._data[1]


class RigidModel2D(Transform):

  def __init__(self, dataString):
    '''
    '''
    super(RigidModel2D,self).__init__(dataString)

  @property
  def r(self):
    return self._data[0]

  @property
  def x(self):
    return self._data[1]

  @property
  def y(self):
    return self._data[2]

  def calculateBB(self, width, height):

    c = np.cos(self.r)
    s = np.sin(self.r)

    points = [[0, 0], [0, height - 1], [width - 1, 0], [width - 1, height - 1]]
    min_x, min_y, max_x, max_y = [ sys.maxint, sys.maxint, -sys.maxint, -sys.maxint ]
    for point in points:
        new_x = c * point[0] - s * point[1] + self.x
        new_y = s * point[0] + c * point[1] + self.y
        min_x = min(min_x, new_x)
        min_y = min(min_y, new_y)
        max_x = max(max_x, new_x)
        max_y = max(max_y, new_y)

    output_width, output_height = (int(max_x - min_x)+1, int(max_y - min_y)+1)

    return output_width, output_height
