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


        __kernel void stitch(__global uchar *out_g,
                                const int out_width,
                                const int out_height,  
                                __global const uchar *tile_g) {
          int gid = get_global_id(0);

          if (gid >= out_width*out_height)
            return;

          // col + row inside output
          //int col = gid % out_width;
          //int row = gid / out_width;

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
    """

    divisor = 2**view._zoomlevel

    minX = view._bbox[0] 
    minY = view._bbox[2]
    out_width = view._bbox[1]
    out_height = view._bbox[3]

    reshaped_imagedata = view._imagedata.reshape(out_height, out_width)

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

      offset_x = int(offset_x-minX) + 1
      offset_y = int(offset_y-minY) + 1

      # print 'placing tile', t, 'at', offset_x, offset_y

      mf = cl.mem_flags

      # output_subarray_start = offset_y*out_width + offset_x
      # output_subarray_end = output_subarray_start + tile_width*tile_height
      # output_subarray = view._imagedata[output_subarray_start:output_subarray_end]
      output_subarray = reshaped_imagedata[offset_y:offset_y+tile_height,offset_x:offset_x+tile_width]
      output_subarray = output_subarray.ravel()

      # print output_subarray_start, output_subarray_end, output_subarray_end-output_subarray_start

      out_img = cl.Buffer(stitcher.context, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=output_subarray)
      in_img = cl.Buffer(stitcher.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=t._levels[view._zoomlevel]._memory)



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
      stitcher.program.stitch(stitcher.queue,
                              (tile_width*tile_height,),
                              None,
                              out_img,
                              np.int32(tile_width),
                              np.int32(tile_height),
                              in_img)

      cl.enqueue_copy(stitcher.queue, output_subarray, out_img).wait()

      reshaped_imagedata[offset_y:offset_y+tile_height,offset_x:offset_x+tile_width] = output_subarray.reshape(tile_height, tile_width)

      # view._imagedata[output_subarray_start:output_subarray_end] = output_subarray

    # print 'storing'
    # img = view._imagedata.reshape(out_height, out_width)
    # cv2.imwrite('/tmp/stitch.jpg', reshaped_imagedata)

    view._status.loaded()

    manager.onStitch(view)


  @staticmethod
  def run(manager, view):
    '''
    '''
    Stitcher(manager, view)

