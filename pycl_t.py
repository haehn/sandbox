
import numpy as np
import pyopencl as cl
import pyopencl.array
import cv2
import sys
import time



ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

prg = cl.Program(ctx, """
__kernel void ds(__global const uchar *img_g, const int width, __global uchar *out_g) {
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

""").build()



def transform(ctx, queue, img_s, width, height, angle, Tx, Ty, out_width, out_height, out_s):

  mf = cl.mem_flags
  img_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s)
  out_g = cl.Buffer(ctx, mf.WRITE_ONLY, out_s.nbytes)

  # prg.ds(queue, img_s.shape, None, img_g, np.int32(width), out_g)
  prg.transform(queue, img_s.shape, None, img_g, np.int32(width), np.int32(height), np.float32(angle), np.float32(Tx), np. float32(Ty), np.int32(out_width), np.int32(out_height), out_g)


  cl.enqueue_copy(queue, out_s, out_g)

  # print img_s[0:5], out_s[0:5]
  # print img_s.shape, out_s.shape


  return out_s


img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
width, height = (img.shape[0], img.shape[1])

R, Tx, Ty = [0.34, 500, 500]
# print "R {0}, Tx, Ty: {1}, {2}".format(R, Tx, Ty)
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



# M = np.float32([ [c, -s, Tx - min_x],[ s, c, Ty - min_y] ])
Tx2 = Tx #- min_x
Ty2 = Ty #- min_y
# print Tx2, Ty2
new_width = int(max_x - min_x)
new_height = int(max_y - min_y)
if (new_width % 2 != 0):
  new_width += 1

if (new_height % 2 != 0):
  new_height +=1 

new_size = (new_width, new_height)

print new_size

# out_arr = cv2.warpAffine(img, M, new_size)
# print new_size
output = np.zeros(new_size, dtype=img.dtype)

img_s = img.ravel()
out_s = output.ravel()



# How many levels do I have?
# nLevels = 0;
# width = new_size[0] / 2
# out_pyr_g = []
# mf = cl.mem_flags
# while (width > 512):
#   if( nLevels == 0 ):
#     # TODO If run on CPU, does COPY_HOST_PTR make a copy of the data in main memory?
#     out_pyr_g.append(cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s))
#   else:
#     out_pyr_g.append(cl.Buffer(ctx, mf.READ_WRITE | mf.ALLOC_HOST_PTR, width*width))
#   width /= 2
#   nLevels+=1;
  

# print out_pyr_g
# sys.exit()


# Upload first to gpu

# img_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img_s)
# out_g = cl.Buffer(ctx, mf.READ_WRITE, img_s.nbytes)

# Memory allocation for all pyramid levels
transformed_bytes = transform(ctx, queue, img_s, width, height, R, Tx2, Ty2, new_size[0], new_size[1], out_s)
print 'transformed!'

# img_r = transformed_bytes.reshape(new_size[0], new_size[1])
# cv2.imwrite('/tmp/test.jpg', img_r)
# sys.exit(1)



def ds(ctx, queue, img_s, width, height, new_width, new_height, out_s):

  mf = cl.mem_flags
  img_g = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=img_s)
  out_g = cl.Buffer(ctx, mf.WRITE_ONLY, (new_width*new_height))
  print 'call', width, new_width, new_height
  prg.ds(queue, img_s.shape, None, img_g, np.int32(width), out_g)
  # prg.transform(queue, img_s.shape, None, img_g, np.int32(width), np.float32(angle), np.float32(Tx), np. float32(Ty), np.int32(out_width), out_g)
  print 'done'

  cl.enqueue_copy(queue, out_s, out_g).wait()
  print 'got it'
  # print img_s[0:5], out_s[0:5]
  # print img_s.shape, out_s.shape


  return out_s


width = new_size[0]
height = new_size[1]
# if (new_size[0] % 2 != 0):
#   # width is odd
#   width += 1

# if (new_size[1] % 2 != 0):
#   # height is odd
#   height += 1

# print transformed_bytes.shape

# if (width*height != new_size[0]*new_size[1]):
#   print 'extending input array'
#   transformed_bytes = np.hstack((transformed_bytes, [0]*(width*height - new_size[0]*new_size[1])))

# print transformed_bytes.shape

k = 0
new_width = int(width / 2)
new_height = int(height / 2)


# if (new_width % 2 !=0):
#   new_width += 1

# if (new_height % 2 != 0):
#   new_height += 1

# while (width > 512):





print 'downsampling', width, height, width*height, 'n', new_width, new_height, new_width*new_height

k+=1
downsampled = np.zeros((new_width*new_height), dtype=transformed_bytes.dtype)
downsampled = ds(ctx, queue, transformed_bytes, width, height, new_width, new_height, downsampled)

# if k==5:
print 'storing'
outimg = downsampled.reshape(new_width, new_height)
cv2.imwrite('/tmp/trans.jpg', outimg)

width = new_width
new_width /= 2
new_height /= 2
transformed_bytes = downsampled









