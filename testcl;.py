import numpy as np


import pyopencl as cl
import cv2
import time
import sys


img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
width, height = (img.shape[0], img.shape[1])

img_s = img.ravel()

ctx = cl.create_some_context()

start_t = time.clock()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s)
# b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)

prg = cl.Program(ctx, """
__kernel void sum(__global const uchar *a_g, __global uchar *res_g) {
  int gid = get_global_id(0);
  res_g[gid] = a_g[gid];
}
""").build()

res_g = cl.Buffer(ctx, mf.WRITE_ONLY, img_s.nbytes)
prg.sum(queue, img_s.shape, None, a_g, res_g)

res_np = np.empty_like(img_s)
cl.enqueue_copy(queue, res_np, res_g)

# Check on CPU with Numpy:

print time.clock() - start_t