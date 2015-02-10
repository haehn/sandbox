from worker import Worker

class Stitcher(Worker):

  def __init__(self, manager, view):
    '''
    '''
    
    manager.onStitch(view)


  @staticmethod
  def run(manager, view):
    '''
    '''
    Stitcher(manager, view)

