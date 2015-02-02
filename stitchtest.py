#!/usr/bin/env python
import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array
import cv2
import sys
import time
import os

jsonfile = sys.argv[1]
import json
with open(jsonfile) as f:
  tiles = json.load(f)


width = 0
height = 0

zoomlevel = sys.argv[2]
divisor = 2**int(zoomlevel)

minX = 0
minY = 0

for t in tiles:

  tile_width = 16384 / divisor
  tile_height = 16384 / divisor

  tile = np.zeros((tile_width, tile_height), dtype=np.uint8)

  transforms = []
  for r in t['transforms']:
    if r["className"] == "mpicbg.trakem2.transform.TranslationModel2D":
      transforms.append(map(float, r["dataString"].split(' ')))
    elif r["className"] == "mpicbg.trakem2.transform.RigidModel2D":
      transforms.append(map(float, r["dataString"].split(' '))[1:])


  offset_x0, offset_y0 = (transforms[0][0], transforms[0][1])
  offset_x1, offset_y1 = (transforms[1][0], transforms[1][1])

  offset_x = (offset_x0 + offset_x1) / divisor
  offset_y = (offset_y0 + offset_y1) / divisor

  minX = min(minX, offset_x)
  minY = min(minY, offset_y)

  width = max(width, tile_width+offset_x)
  height = max(height, tile_height+offset_y)

print width, height

width2 = int(width) + 1
height2 = int(height) + 1

print width2, height2

print minX, minY

width = int(width-minX) + 1
height = int(height-minY) + 1

print width, height


output = np.zeros((height, width), dtype=np.uint8)

for t in tiles:

  tile_width = 16384 / divisor
  tile_height = 16384 / divisor

  tile = np.ones((tile_width, tile_height), dtype=np.uint8)

  transforms = []
  for r in t['transforms']:
    if r["className"] == "mpicbg.trakem2.transform.TranslationModel2D":
      transforms.append(map(float, r["dataString"].split(' ')))
    elif r["className"] == "mpicbg.trakem2.transform.RigidModel2D":
      transforms.append(map(float, r["dataString"].split(' '))[1:])


  offset_x0, offset_y0 = (transforms[0][0], transforms[0][1])
  offset_x1, offset_y1 = (transforms[1][0], transforms[1][1])

  offset_x = (offset_x0 + offset_x1) / divisor
  offset_y = (offset_y0 + offset_y1) / divisor

  # print 'offsets',offset_x, offset_y

  # minX2 = int(minX) + 1
  # minY2 = int(minY) + 1
  # print 'new mins', minX2, minY2

  offset_x = int(offset_x-minX) + 1
  offset_y = int(offset_y-minY) + 1

  # print 'offsets after',offset_x, offset_y

  # print 'aaa', offset_x,offset_x+tile_width
  # print offset_x, offset_y, tile_width, tile_height, output[offset_y:offset_y+tile_height,offset_x:offset_x+tile_width].shape

  print 'placing tile at', offset_x, offset_y

  output[offset_y:offset_y+tile_height,offset_x:offset_x+tile_width] = tile*255

cv2.imwrite('/tmp/test333.jpg', output)
sys.exit(1)


