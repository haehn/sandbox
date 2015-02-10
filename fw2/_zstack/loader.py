import ctypes
import numpy as np
import os
import pyopencl as cl
import sys

from powertrain import Powertrain
from tile import Tile
from worker import Worker

class Loader(Worker):

  def __init__(self, manager, tile):
    '''
    '''

    # setup transform kernel
    transformer = Powertrain(True)
    transformer.program = """
      __kernel void transform(__global const uchar *img_g,
                              const int width,
                              const int height,
                              const float angle,
                              const float Tx,
                              const float Ty,
                              const int out_width,
                              const int out_height,
                              __global uchar *out_g) {
        int gid = get_global_id(0);

        int col = gid % width;
        int row = gid / width;

        if ((col >= width) || (row >= height)) {
          return;
        }

        if (col < 0) {
          return;
        }

        // 
        float c = cos(angle);
        float s = sin(angle);

        // new position
        int new_col = c * col - s * row + Tx;
        int new_row = s * col + c * row + Ty;

        if ((new_col >= out_width) || (new_row >= out_height)) {
          return;
        }

        if (new_col < 0) {
          return;
        }  

        int k = new_row*out_width + new_col;

        out_g[k] = img_g[gid];

      }    
    """


    imagedata = Tile.load(tile)
    width = imagedata.shape[0]
    height = imagedata.shape[1]
    # for i in range(len(imagedata)):
      # memory[i] = imagedata[i]

    transform = tile._transforms[1]
    c = np.cos(transform.r)
    s = np.sin(transform.r)

    points = [[0, 0], [0, height - 1], [width - 1, 0], [width - 1, height - 1]]
    min_x, min_y, max_x, max_y = [ sys.maxint, sys.maxint, -sys.maxint, -sys.maxint ]
    for point in points:
        new_x = c * point[0] - s * point[1] + transform.x
        new_y = s * point[0] + c * point[1] + transform.y
        min_x = min(min_x, new_x)
        min_y = min(min_y, new_y)
        max_x = max(max_x, new_x)
        max_y = max(max_y, new_y)

    tx = transform.x - min_x
    ty = transform.y - min_y
    output_width, output_height = (int(max_x - min_x)+1, int(max_y - min_y)+1)

    mf = cl.mem_flags
    in_img = cl.Buffer(transformer.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=imagedata)
    out_img = cl.Buffer(transformer.context, mf.WRITE_ONLY, tile._imagedata.nbytes)

    transformer.program.transform(transformer. queue,
                                 (width*height,),
                                 None,
                                 in_img,
                                 np.int32(width),
                                 np.int32(height),
                                 np.float32(transform.r),
                                 np.float32(tx),
                                 np.float32(ty),
                                 np.int32(output_width),
                                 np.int32(output_height),
                                 out_img)

    
    cl.enqueue_copy(transformer.queue, tile._memory, out_img).wait()

    # print 'Worker', tile._mipmapLevels["0"]['imageUrl'], memory.address

    # import cv2
    # img = memory.reshape(tile._real_width, tile._real_height)
    # cv2.imwrite('/tmp/'+os.path.basename(tile._mipmapLevels["0"]['imageUrl']), img)
    tile._status.loaded()
    # print Loader.shmem_as_ndarray(tile._memory)[20000:25000]
    manager.onLoad(tile)


  @staticmethod
  def run(manager, tile):
    '''
    '''
    Loader(manager, tile)



