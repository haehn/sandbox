from tile import Tile

class Worker(object):

  def __init__(self, manager, tile):
    '''
    '''
    imagedata = Tile.load(tile)
    manager.done(tile)


  @staticmethod
  def run(manager, tile):
    '''
    '''
    Worker(manager, tile)

