import OpenGL.GL as gl
import OpenGL.GLUT as glut
import sys
from PIL.Image import open
from PIL.Image import fromarray
import numpy
import time 


def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    if key == '\033':
        sys.exit( )

#
# load image
#

glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Hello world!')
# glut.glutReshapeWindow(512,512)
# glut.glutReshapeFunc(reshape)
# glut.glutDisplayFunc(display)
# glut.glutKeyboardFunc(keyboard)

im = open('test.tif')
im_x = im.size[0]
im_y = im.size[1]

# start_t = time.clock()
# im2 = im.tostring("raw", "L", 0, -1)
# print time.clock() - start_t


im = numpy.array(im)

# ID = gl.glGenTextures(1)
gl.glBindTexture(gl.GL_TEXTURE_2D, 1)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, im_x, im_y, 0, gl.GL_LUMINANCE, gl.GL_UNSIGNED_BYTE, im)
gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

# gl.getTexImage(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, gl.GL_UNSIGNED_BYTE)

# z0 = gl.glGetTexImageui(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE)
# z1 = gl.glGetTexImageui(gl.GL_TEXTURE_2D, 1, gl.GL_LUMINANCE)
# print z0, z1

k = 0
while (im.shape[0] > 512):
  k+=1
  start_t = time.clock()
  im = gl.glGetTexImageub(gl.GL_TEXTURE_2D, k, gl.GL_LUMINANCE, outputType=numpy.array)
  print im.shape
  print time.clock() - start_t
  img = fromarray(im)
  # img.save('/tmp/pygl_z'+str(k)+'.jpg')

