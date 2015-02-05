class Worker(object):

  def __init__(self, manager, section):
    '''
    '''
    self._manager = manager
    self._section = section

    for t in self._section._tiles:
      t.load()

    print 'loaded', section


  @staticmethod
  def run(manager, section):
    '''
    '''
    Worker(manager, section)

