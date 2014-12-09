import cv2
import time

start_t = time.clock()
i = cv2.imread('test.pgn', cv2.CV_LOAD_IMAGE_GRAYSCALE)
print time.clock() - start_t
print i.shape

k = 0
cv2.imwrite('/tmp/pycl_z'+str(k)+'.jpg', i)