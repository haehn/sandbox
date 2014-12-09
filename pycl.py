
import numpy as np
import pyopencl as cl
import pyopencl.array
import cv2
import sys
import time



ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

prg = cl.Program(ctx, """
__kernel void sum(__global const uchar *img_g, const int width, __global uchar *out_g) {
  int gid = get_global_id(0);

  int col = gid % width;
  int row = gid / width;

  int new_row = row/2;
  int new_col = col/2;
  int new_width = width/2;
  int k = new_row*new_width + new_col;

  if (row % 2 == 0 && col % 2 == 0) {

    uchar c = img_g[gid];
    uchar r = img_g[gid+1];
    uchar b = img_g[gid+width];
    uchar b_r = img_g[gid+width+1];

    uchar val = (c + r + b + b_r) / 4;

    //out_g[k] = img_g[gid];
    out_g[k] = val;
  }
}
""").build()




def doit(ctx, queue, img_s, width, out_s):

  mf = cl.mem_flags
  img_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s)
  out_g = cl.Buffer(ctx, mf.WRITE_ONLY, img_s.nbytes)

  prg.sum(queue, img_s.shape, None, img_g, np.int32(width), out_g)


  cl.enqueue_copy(queue, out_s, out_g)

  # print img_s[0:5], out_s[0:5]
  # print img_s.shape, out_s.shape

  return out_s




img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
width, height = (img.shape[0], img.shape[1])
# print width, height, img.dtype
output = np.zeros((width/2, height/2), dtype=img.dtype)

img_s = img.ravel()
out_s = output.ravel()






k=0
while (width > 256):

  k+=1
  start_t = time.clock()
  out_s = doit(ctx, queue, img_s, width, out_s)
  print time.clock() - start_t
  # img_r = out_s.reshape(width/2, height/2)
  # cv2.imwrite('/tmp/pycli_z'+str(k)+'.jpg', img_r)

  img_s = out_s
  width /= 2
  height /= 2
  output = np.zeros((width/2, height/2), dtype=img.dtype)
  out_s = output.ravel()

