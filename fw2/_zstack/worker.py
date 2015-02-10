import ctypes
import numpy as np

class Worker(object):

  def __init__(self):
    '''
    '''
    pass



  @staticmethod
  def shmem_as_ndarray(raw_array):
    import numpy as np
    _ctypes_to_numpy = {
                        ctypes.c_char : np.int8,
                        ctypes.c_wchar : np.int16,
                        ctypes.c_byte : np.int8,
                        ctypes.c_ubyte : np.uint8,
                        ctypes.c_short : np.int16,
                        ctypes.c_ushort : np.uint16,
                        ctypes.c_int : np.int32,
                        ctypes.c_uint : np.int32,
                        ctypes.c_long : np.int32,
                        ctypes.c_ulong : np.int32,
                        ctypes.c_float : np.float32,
                        ctypes.c_double : np.float64
                        }
    address = raw_array._wrapper.get_address()
    size = raw_array._wrapper.get_size()
    dtype = _ctypes_to_numpy[raw_array._type_]
    class Dummy(object): pass
    d = Dummy()
    d.__array_interface__ = {
                             'data' : (address, False),
                             'typestr' : np.dtype(np.uint8).str,
                             'descr' : np.dtype(np.uint8).descr,
                             'shape' : (size,),
                             'strides' : None,
                             'version' : 3
                             }                            
    return np.asarray(d).view(dtype=dtype)