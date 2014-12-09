
import numpy as np
import pyopencl as cl
import pyopencl.array
import cv2
import sys
import time





def doit(ctx, queue, img_s, width, angle, Tx, Ty, out_width, out_s):

  mf = cl.mem_flags
  img_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s)
  out_g = cl.Buffer(ctx, mf.WRITE_ONLY, out_s.nbytes)

  # prg.ds(queue, img_s.shape, None, img_g, np.int32(width), out_g)
  prg.transform(queue, img_s.shape, None, img_g, np.int32(width), np.float32(angle), np.float32(Tx), np. float32(Ty), np.int32(out_width), out_g)


  cl.enqueue_copy(queue, out_s, out_g)

  print img_s[0:5], out_s[0:5]
  print img_s.shape, out_s.shape


  return out_s




img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
width, height = (img.shape[0], img.shape[1])

R, Tx, Ty = [0.34, 500, 500]
print "R {0}, Tx, Ty: {1}, {2}".format(R, Tx, Ty)
c = np.cos(R)
s = np.sin(R)
# Find the output's height and width

height, width = img.shape
points = [[0, 0], [0, height - 1], [width - 1, 0], [width - 1, height - 1]]
min_x, min_y, max_x, max_y = [ sys.maxint, sys.maxint, -sys.maxint, -sys.maxint ]
for point in points:
    # shift the point
    # point[0] += start_point[0]
    # point[1] += start_point[1]
    new_x = c * point[0] - s * point[1] + Tx
    new_y = s * point[0] + c * point[1] + Ty
    min_x = min(min_x, new_x)
    min_y = min(min_y, new_y)
    max_x = max(max_x, new_x)
    max_y = max(max_y, new_y)


# print min_x, min_y, max_x, max_y



M = np.float32([ [c, -s, Tx - min_x],[ s, c, Ty - min_y] ])


new_size = (int(max_x - min_x + 1), int(max_y - min_y + 1))

out_arr = cv2.warpAffine(img, M, new_size)

cur_width, cur_height = out_arr.shape
while cur_width > 512:

  cur_width, cur_height = out_arr.shape
  new_a = np.zeros((cur_width/2, cur_height/2), dtype=img.dtype)

  cv2.pyrDown(out_arr, new_a)
  # cv2.resize(out_arr, (0,0),new_a, .5, .5, cv2.INTER_AREA);

  out_arr = new_a

  print new_a.shape

