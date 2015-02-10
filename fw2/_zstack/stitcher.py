import numpy as np
import pyopencl as cl

from powertrain import Powertrain
from worker import Worker

class Stitcher(Worker):

  def __init__(self, manager, view):
    '''
    '''

    # setup stitch kernel
    stitcher = Powertrain(True)
    stitcher.program = """
        __kernel void stitch(__global uchar *out_g,
                                const int out_width,
                                const int out_height,
                                const int tile_offset_x,
                                const int tile_offset_y,
                                const int tile_width,
                                const int tile_height,
                                __global const uchar *tile_g) {

          // id inside output
          int gid = get_global_id(0);

          if (gid >= out_width*out_height)
            return;

          // col + row inside output
          int col = gid % out_width;
          int row = gid / out_width;

          // do nothing until we reach the hotspot
          if (col < tile_offset_x) {
            return;
          }

          if (row < tile_offset_y) {
            return;
          }

          // we are in the hotspot
          int tile_col = col - tile_offset_x;
          int tile_row = row - tile_offset_y;

          if (tile_col > tile_width) {
            return;
          }

          if (tile_row > tile_height) {
            return;
          }


          int k = tile_row*tile_width + tile_col;

          if (tile_g[k] == 0) {
            return;
          }

          out_g[gid] = tile_g[k];


        }
    """

    divisor = 2**view._zoomlevel

    out_width = view._bbox[1]
    out_height = view._bbox[3]

    for t in view._tiles:

      tile_width = t._real_width / divisor
      tile_height = t._real_height / divisor

      offset_x = 0
      offset_y = 0

      for transform in t._transforms:

        offset_x += transform.x
        offset_y += transform.y

      offset_x /= divisor
      offset_y /= divisor

      offset_x = int(offset_x-view._bbox[0]) + 1
      offset_y = int(offset_y-view._bbox[2]) + 1

      print 'placing tile', t, 'at', offset_x, offset_y

      mf = cl.mem_flags
      out_img = cl.Buffer(stitcher.context, mf.READ_WRITE | mf.USE_HOST_PTR, hostbuf=view._memory)
      in_img = cl.Buffer(stitcher.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=t._memory)

      stitcher.program.stitch(stitcher.queue,
                              (out_width*out_height,),
                              None,
                              out_img,
                              np.int32(out_width),
                              np.int32(out_height),
                              np.int32(offset_x),
                              np.int32(offset_y),
                              np.int32(tile_width),
                              np.int32(tile_height),
                              in_img

                              )

    cl.enqueue_copy(stitcher.queue, view._memory, out_img).wait()

    manager.onStitch(view)


  @staticmethod
  def run(manager, view):
    '''
    '''
    Stitcher(manager, view)

