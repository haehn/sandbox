import cv2
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


        __kernel void stitch2(__global uchar *out_g,
                                const int out_width,
                                const int out_height,  
                                __global const uchar *tile_g) {
          int gid = get_global_id(0);

          if (gid >= out_width*out_height)
            return;

          // col + row inside output
          int col = gid % out_width;
          int row = gid / out_width;

          if (tile_g[gid] == 0) {

            // check for boundary pixels (thin black lines)
            //int k_top = (row+1)*out_width + col;
            //int k_left = row*out_width + col+1;

            //if (tile_g[k_top] != 0) {
            //  out_g[gid] = tile_g[k_top];
            //  return;
            //}

            //if (tile_g[k_left] != 0) {
            //  out_g[gid] = tile_g[k_left];
            //  return;
            //}

            return;
          }

          out_g[gid] = tile_g[gid];


        }

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

      output_subarray_start = offset_y*out_width + offset_x
      output_subarray_end = output_subarray_start + tile_width*tile_height
      output_subarray = view._imagedata[output_subarray_start:output_subarray_end]

      out_img = cl.Buffer(stitcher.context, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=output_subarray)
      in_img = cl.Buffer(stitcher.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=t._memory)

      # stitcher.program.stitch(stitcher.queue,
      #                         (out_width*out_height,),
      #                         None,
      #                         out_img,
      #                         np.int32(out_width),
      #                         np.int32(out_height),
      #                         np.int32(offset_x),
      #                         np.int32(offset_y),
      #                         np.int32(tile_width),
      #                         np.int32(tile_height),
      #                         in_img

      #                         )
      stitcher.program.stitch2(stitcher.queue,
                               (tile_width*tile_height,),
                               None,
                               out_img,
                               np.int32(tile_width),
                               np.int32(tile_height),
                               in_img)

      cl.enqueue_copy(stitcher.queue, output_subarray, out_img).wait()

      view._imagedata[output_subarray_start:output_subarray_end] = output_subarray


    img = view._imagedata.reshape(out_height, out_width)
    cv2.imwrite('/tmp/stitch.jpg', img)

    manager.onStitch(view)


  @staticmethod
  def run(manager, view):
    '''
    '''
    Stitcher(manager, view)

