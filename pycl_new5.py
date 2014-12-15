
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
p.program = """
const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | 
  CLK_FILTER_LINEAR | CLK_ADDRESS_CLAMP_TO_EDGE;

__kernel void downsample(__read_only image2d_t sourceImage, __write_only image2d_t targetImage)
{

  int w = get_image_width(targetImage);
  int h = get_image_height(targetImage);

  int outX = get_global_id(0);
  int outY = get_global_id(1);
  int2 posOut = {outX, outY};

  float inX = outX / (float) w;
  float inY = outY / (float) h;
  float2 posIn = {inX, inY};

  float4 pixel = read_imagef(sourceImage, sampler, posIn);
  write_imagef(targetImage, posOut, pixel);

}
"""



#
# load input image
#
img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
img_width, img_height = img.shape

#
# create CL buffers for zoomlevels as well as output arrays
#
mf = cl.mem_flags
width = img_width
image_format = cl.ImageFormat(cl.channel_order.R, cl.channel_type.UNSIGNED_INT8)
in_img = cl.Image(p.context, mf.READ_ONLY | mf.USE_HOST_PTR, image_format, hostbuf=img)

k=1
while width > 512:

  width /= 2

  out_buffer = np.zeros(shape=(width, width), dtype=np.uint8)
  out_img = cl.Image(p.context, mf.READ_WRITE, image_format, (out_buffer.shape))

  p.program.downsample(p.queue, out_buffer.shape, None, in_img, out_img)

  cl.enqueue_read_image(p.queue, out_img, (0,0), out_buffer.shape, out_buffer).wait()

  print out_buffer.shape
  # cv2.imwrite('/tmp/pycl_tex2_z'+str(k)+'.jpg', out_buffer)
  in_img = out_img
  k+=1


sys.exit()
