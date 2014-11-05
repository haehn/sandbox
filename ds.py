#!/usr/bin/env python

import pycuda.driver as cuda #For Memory Allocation and such
import pycuda.gpuarray as gpuarray #For GPU array computations
import pycuda.compiler as nvcc #Compiles our CUDA kernels
import pycuda.autoinit #Start Those GPUs!
import numpy as np # For Matrix Processing on GPUs
import cv2 #Computer Vision LIVES!
import sys


DownSampleModule = nvcc.SourceModule("""
//Cap a value between 255 and 0
__device__ float cap(float value){
	return value < 0.0 ? 0.0 :  (value > 255.0 ? 255.0 : value);
}
//Get the value of the image at a given integral index
__device__ float getPixel(float * image, int width, int height, int xIdx, int yIdx){
	//Make sure we are actually within bounds
	int accX = xIdx < 0 ? 0 : (xIdx >= width ? width - 1 : xIdx);
	int accY = yIdx < 0 ? 0 : (yIdx >= height ? height - 1 : yIdx);
	return image[accY * width + accX];
}
//Given a corner of a square, returns the sample value for the neighborhood
__device__ float sampledPixel(float * image, int width, int height, int xIdx, int yIdx){
	return cap((getPixel(image, width, height, xIdx, yIdx) 
					+ getPixel(image, width, height, xIdx + 1, yIdx)
					+ getPixel(image, width, height, xIdx, yIdx + 1)
					+ getPixel(image, width, height, xIdx + 1, yIdx + 1)) / 4.0);
}
//Fills an output with the downsampled version of the input
//output has dim (width / 2, height / 2)
__global__ void downSample(float * image, int width, int height, float * output){
	int xIdx = blockDim.x * blockIdx.x + threadIdx.x;
	int yIdx = blockDim.y * blockIdx.y + threadIdx.y;
	int downWidth = width / 2;
	int downHeight = height / 2;
	if(xIdx < downWidth && yIdx < downHeight){
		int upX = xIdx * 2;
		int upY = yIdx * 2;

		output[yIdx * downWidth + xIdx] = 255.;
	}
}
""")

DownSample = DownSampleModule.get_function("downSample");

#Takes a black and white image and downsamples it
def downSampleImage(img):
	imgGPU = gpuarray.to_gpu(img)
	height, width = int(img.shape[0]), int(img.shape[1])
	dimH, dimW = np.int32(img.shape)
	outGPU = gpuarray.zeros((height / 2, width / 2), np.uint8)
	blockSize = (16,16,1)
	gridSize = (width / blockSize[0], height / blockSize[1], 1)
	DownSample(imgGPU, dimW, dimH, imgGPU, block = blockSize, grid = gridSize)
	return outGPU.get()


if __name__ == "__main__":
	img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
	img = img.astype(np.uint8)
	cv2.imwrite(sys.argv[2], downSampleImage(img))
