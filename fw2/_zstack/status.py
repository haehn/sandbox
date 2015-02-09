import multiprocessing as mp

class Status:
  '''
  '''

  def __init__(self):
    '''
    '''
    self._code = mp.RawValue('i', 0)

  def virgin(self):
    '''
    '''
    self._code.value = 0

  def isVirgin(self):
    '''
    '''
    return (self._code.value == 0)

  def loading(self):
    '''
    '''
    self._code.value = 2

  def isLoading(self):
    '''
    '''
    return (self._code.value == 2)

  def loaded(self):
    '''
    '''
    self._code.value = 5

  def isLoaded(self):
    '''
    '''
    return (self._code.value == 5)

