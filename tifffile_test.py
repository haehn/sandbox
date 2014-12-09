import tifffile as tif
import time

start_t = time.clock()

i = tif.imread('test.tif')
print time.clock() - start_t
print i.shape
