
import pycuda.driver as cuda
import pycuda.gpuarray as gpuarray #For GPU array computations
import pycuda.compiler as nvcc #Compiles our CUDA kernels
import pycuda.autoinit #Start Those GPUs!
import numpy as np
import cv2
import sys


downsample=nvcc.SourceModule("""
texture<float, 2, cudaReadModeElementType> tex;

__global__ void downsample(float * data, int width, int new_width) {

  unsigned int x = blockIdx.x * blockDim.x + threadIdx.x;
  unsigned int y = blockIdx.y * blockDim.y + threadIdx.y;

  float value = tex2D(tex, y, x)*255.;

  data[(x/2 * new_width + y/2)] = value;

}
""")
downsample_func = downsample.get_function("downsample")
texref = downsample.get_texref("tex")

blocksize = (16,16,1)


def doit(img):
  width, height = (img.shape[0], img.shape[1])
  
  cuda.matrix_to_texref(img, texref, order="C")
  texref.set_filter_mode(cuda.filter_mode.LINEAR)
  
  gpu_output = np.zeros((width/2,height/2), dtype=np.float32)
  gridsize = (width / blocksize[0], height / blocksize[1])

  downsample_func(cuda.Out(gpu_output), np.int32(width), np.int32(width/2), block=blocksize, grid = gridsize, texrefs=[texref])

  # gpu_output = gpu_output.transpose()

  return gpu_output







img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)

k=0
while (img.shape[0] > 512):
  k+=1
  img = doit(img)
  img = img.astype(np.uint8)
  cv2.imwrite('/tmp/py_z'+str(k)+'.jpg', img)
