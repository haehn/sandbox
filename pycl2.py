
import pyopencl as cl
#** This module allows for the creation of arrays that can be passed through the buffer.
import pyopencl.array
import numpy

class CL(object):
    #** Create the context and commandQueue.
    def __init__(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)

    #** Load the OpenCL C-like code from another file.
    def loadProgram(self, filename):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())
        print fstr
        #create the program
        self.program = cl.Program(self.ctx, fstr).build()

    #Create the data arrays and the buffers needed to pass them to 
    def popCorn(self):
        #initialize client side (CPU) arrays
        # This creates a numpy 3 dimensional array of the size (1000,251,100).
        # The array is filled with random numbers that are of the type float.
        self.a = numpy.random.randn(1000,251,100).astype(numpy.float32)
        # This creates a numpy 3 dimension array of the same size and type but filled with zeros.    
        output = numpy.zeros((1000,251,100),numpy.float32)
        # This creates an empty array of the size of self.a.
        self.c = numpy.empty_like(self.a)

        # This creates a pyOpenCL array that can be passed to the OpenCL kernel.
        # The pyOpenCL array.to_device function creates the buffer with the GPU.
        # This allows for the calling of the array within OpenCL
        self.aArray = cl.array.to_device(self.ctx, self.queue, self.a)
        # This is a dummy variable used to hold the shape of the array we're passing.
        self.arrayShape = numpy.array(self.aArray.shape, numpy.int8)
        # This creates the pyOpenCL array for the output matrix. As above, it also creates the buffer.
        self.outputArray = cl.array.to_device(self.ctx, self.queue, output)

    # This runs the kernel on the data arrays created in the popCorn function.
    def execute(self):
        # This runs the kernel. You have to use the .data on self.aArray and self.outputArray.
        # Otherwise you are passing a buffer object instead of the actual array.
        # self.arrayShape[0] and self.arrayShape[1] give the OpenCL Kernel the size of your array.
        # Even though you are passing a 3 dimensional array, you have to treat it as a flattened array.
        self.program.cos3D(self.queue, self.a.shape, None, self.aArray.data,
                           self.outputArray.data, self.arrayShape[0], self.arrayShape[1])
        # Reads the output into the local variable.
        cl.enqueue_read_buffer(self.queue, self.outputArray.data, self.c).wait()

    # This does the same thing as CL.execute but does it without using OpenCL
    def local(self):
        self.c = numpy.cos(self.a)

if __name__ == "__main__":
    example = CL()
    example.loadProgram("cos3D.cl")
    import time
    example.popCorn()
    starttime = time.time()
    for i in range(0,20):
        onelooptime = time.time()
        example.execute()
        print "OpenCL One Iteration: ", time.time() - onelooptime
    print "OpenCL Time: ", (time.time() - starttime) / 20.0
    starttime = time.time()
    for i in range(0,20):
        onelooptime = time.time()
        example.local()
        print "Python One Iteration: ", time.time() - onelooptime
    print "Python Time: ", (time.time() - starttime) / 20.0