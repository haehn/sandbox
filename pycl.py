
import numpy as np
import pyopencl as cl
import cv2
import sys

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)



mf = cl.mem_flags

img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
width, height = (img.shape[0], img.shape[1])
print width, height, img.dtype
print img

clImageFormat = cl.ImageFormat(cl.channel_order.LUMINANCE, 
                               cl.channel_type.UNSIGNED_INT8)

clImage = cl.Image(ctx, 
                  mf.READ_ONLY | mf.COPY_HOST_PTR,
                   clImageFormat,
                   img.shape,
                   None,
                   img
                   )









# prg = cl.Program(ctx, """
# __kernel void sum(__global const float *a_g, __global const float *b_g, __global float *res_g) {
#   int gid = get_global_id(0);
#   res_g[gid] = a_g[gid] + b_g[gid];
# }
# """).build()

# res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)
# prg.sum(queue, a_np.shape, None, a_g, b_g, res_g)

# res_np = np.empty_like(a_np)
# cl.enqueue_copy(queue, res_np, res_g)


# # Check on CPU with Numpy:
# print(res_np - (a_np + b_np))
# print(np.linalg.norm(res_np - (a_np + b_np)))