import pyopencl as cl

class Powertrain(object):

  def __init__(self, gpu=False):

    # create the CL context
    platform = cl.get_platforms()
    if gpu:
      device = [platform[0].get_devices(device_type=cl.device_type.GPU)][0]
    else:
      device = [platform[0].get_devices(device_type=cl.device_type.CPU)][0]
    # print 'Using openCL device', device

    self._context = cl.Context(devices=device)
    self._queue = cl.CommandQueue(self._context)
    self._program = None

  @property
  def context(self):

    return self._context

  @property
  def queue(self):
      return self._queue

  @property
  def program(self):

    return self._program

  @program.setter
  def program(self, program):

    # compile program
    self._program = cl.Program(self._context, program).build()

