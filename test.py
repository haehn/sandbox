#!/usr/bin/env python
import cv2
import sys

if __name__ == "__main__":
  img = cv2.imread(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)
  img = cv2.resize(img, img, 400)
  cv2.imwrite(sys.argv[2], img)
