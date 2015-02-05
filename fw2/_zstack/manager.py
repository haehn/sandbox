import multiprocessing as mp

from indexer import Indexer
from worker import Worker

class Manager(object):

  def __init__(self, input_dir):
    '''
    '''
    self._input_dir = input_dir
    self._indexer = Indexer()

    self._no_workers = 6#mp.cpu_count()

    self._queue = mp.Queue()

  def start(self):
    '''
    '''
    print 'Starting manager with', self._no_workers, 'workers.'

    #
    # index all JSONs
    #
    sections = self._indexer.index(self._input_dir)

    print 'Indexed', len(sections), 'sections.'


    #
    # add the first sections to the loading queue
    #
    for i in range(self._no_workers):
      self._queue.put(sections[0]._tiles[i])

    #
    # start loading one
    #
    self.process()
    while not self._queue.empty():
      self.process()

  def done(self, tile):
    '''
    '''
    print 'Loaded', tile._mipmapLevels["0"]['imageUrl']

  def process(self):
    '''
    Starts loading the next section.
    '''
    if not self._queue.empty():
      tile = self._queue.get()

      args = (self, tile)

      # start worker
      worker = mp.Process(target=Worker.run, args=args)
      worker.start()
