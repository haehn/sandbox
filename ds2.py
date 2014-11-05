
import pycuda.driver as cuda
import pycuda.gpuarray as gpuarray #For GPU array computations
import pycuda.compiler as nvcc #Compiles our CUDA kernels
import pycuda.autoinit #Start Those GPUs!
import numpy as np
import cv2
import sys


img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
img = img.astype(np.int16)
width, height = (img.shape[0], img.shape[1])
print width, height, img.dtype
print img

downsample=nvcc.SourceModule("""
texture<int16_t, 2, cudaReadModeElementType> tex;

__global__ void downsample(int16_t * data, int width, int height) {

  unsigned int x = blockIdx.x * blockDim.x + threadIdx.x;
  unsigned int y = blockIdx.y * blockDim.y + threadIdx.y;

  if ((x >= width) || (y >= height)) {
    return;
  }

  data[x * width + y] = tex2D(tex, x, y);

}
""")

downsample_func = downsample.get_function("downsample")
texref = downsample.get_texref("tex")

cuda.matrix_to_texref(img, texref, order="C")
# texref.set_flags(cuda.TRSF_NORMALIZED_COORDINATES)
# texref.set_filter_mode(cuda.filter_mode.LINEAR)

gpu_output = np.zeros_like(img, dtype=np.int16)

blocksize = (16,16,1)
gridsize = (width / blocksize[0], height / blocksize[1])

print 'blocksize', blocksize
print 'gridsize', gridsize

downsample_func(cuda.Out(gpu_output), np.int32(width), np.int32(height), block=blocksize, grid = gridsize, texrefs=[texref])


gpu_output = gpu_output.transpose()

print gpu_output

cv2.imwrite(sys.argv[2], gpu_output)