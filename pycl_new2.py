
import numpy as np
import pyopencl as cl

import cv2
import sys
import time


class Powertrain(object):

  def __init__(self, gpu=False):

    # create the CL context
    platform = cl.get_platforms()
    if gpu:
      device = [platform[0].get_devices(device_type=cl.device_type.GPU)][0]
    else:
      device = [platform[0].get_devices(device_type=cl.device_type.CPU)][0]
    print 'Using openCL device', device

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

    print 'Program built!'


use_gpu = False
if len(sys.argv)==3:
  use_gpu = True

p = Powertrain(use_gpu)
program = """
__kernel void downsample(__global const uchar *img0,
                         const int width,
                         __global uchar *img1,
                         __global uchar *img2,
                         __global uchar *img3,
                         __global uchar *img4,
                         __global uchar *img5) {
  int gid = get_global_id(0);

  int col = gid % width;
  int row = gid / width;
"""

for current_zoomlevel in range(1,6):
  program += """
    if (row % """+str(current_zoomlevel*2)+""" == 0 && col % """+str(current_zoomlevel*2)+""" == 0) {

      int new_row = row/"""+str(current_zoomlevel*2)+""";
      int new_col = col/"""+str(current_zoomlevel*2)+""";
      int new_width = width/"""+str(current_zoomlevel*2)+""";
      int k = new_row*new_width + new_col;

      int old_width = new_width*2;

      uchar c = img"""+str(current_zoomlevel-1)+"""[k];
      uchar r = img"""+str(current_zoomlevel-1)+"""[k+1];
      uchar b = img"""+str(current_zoomlevel-1)+"""[k+old_width];
      uchar b_r = img"""+str(current_zoomlevel-1)+"""[k+old_width+1];

      uchar val = (c + r + b + b_r) / 4;

      img"""+str(current_zoomlevel)+"""[k] = val;
    }      
  """

program +="""
}
"""

p.program = program

#
# load input image
#
img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
img_width, img_height = img.shape
img_bytes = img.ravel()

#
# create CL buffers for zoomlevels as well as output arrays
#
cl_buffers = {}
out_images = {}
zoomlevel = 0
mf = cl.mem_flags
width = img_width
while width >= 512:

  if zoomlevel == 0:
    # original image
    cl_buffers[zoomlevel] = cl.Buffer(p.context, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=img_bytes)
  else:
    cl_buffers[zoomlevel] = cl.Buffer(p.context, mf.WRITE_ONLY, img_bytes.nbytes)

  out_images[zoomlevel] = np.zeros((width*width), dtype=img_bytes.dtype)

  width /= 2
  zoomlevel += 1

max_zoomlevel = zoomlevel-1

print 'CL Buffers created!'


p.program.downsample(p.queue, out_images[0].shape, None, cl_buffers[0], np.int32(img_width), cl_buffers[1], cl_buffers[2], cl_buffers[3], cl_buffers[4], cl_buffers[5])


#
# run downsampling
#
for zoomlevel, cl_buffer in cl_buffers.iteritems():
  if (zoomlevel == max_zoomlevel):
    break

  out_zoomlevel = zoomlevel + 1
  # p.program.downsample(p.queue, out_images[out_zoomlevel].shape, None, cl_buffer, np.int32(img_width), cl_buffers[out_zoomlevel])
  # store the output
  cl.enqueue_copy(p.queue, out_images[out_zoomlevel], cl_buffers[out_zoomlevel])

  print out_images[out_zoomlevel].shape

sys.exit()