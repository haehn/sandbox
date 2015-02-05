class Transform(object):

  def __init__(self, dataString):
    '''
    '''
    self._data = map(float, dataString.split(' '))

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

