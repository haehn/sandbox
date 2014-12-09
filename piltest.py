from PIL.Image import open
import time
import numpy

start_t = time.clock()
i = open('test.tif')
pixels = numpy.array(i)
# pixels = list(i.getdata())
# width, height = i.size
# pixels = [pixels[j * width:(j + 1) * width] for j in xrange(height)]
print time.clock() - start_t
# print pixels
