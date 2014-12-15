import pyopencl as cl
import numpy as np
import cv2 # OpenCV 2.3.1

# load a 512x512 image
Img = cv2.imread("testsmall.jpg", cv2.CV_LOAD_IMAGE_GRAYSCALE)

OutImg = np.empty(shape=(Img.shape[0]/2,Img.shape[1]/2), dtype=np.uint8) # create Output-Image
# OutImg = np.empty(shape=(100,100), dtype=np.uint8) # create Output-Image

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
dev_Img = cl.Image(ctx,
                     mf.READ_ONLY | mf.USE_HOST_PTR,
                     cl.ImageFormat(cl.channel_order.R,     
                     cl.channel_type.UNSIGNED_INT8),
                     hostbuf=Img)
dev_OutImg = cl.Image(ctx,
                     mf.WRITE_ONLY,
                     cl.ImageFormat(cl.channel_order.R,     
                     cl.channel_type.UNSIGNED_INT8),
                     shape=OutImg.shape)

prg = cl.Program(ctx, """
     const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | 
        CLK_FILTER_LINEAR | CLK_ADDRESS_CLAMP_TO_EDGE;

     __kernel void ImageDS(__read_only image2d_t sourceImage, __write_only image2d_t targetImage)
     {

        int w = get_image_width(targetImage);
        int h = get_image_height(targetImage);

        int outX = get_global_id(0);
        int outY = get_global_id(1);
        int2 posOut = {outX, outY};

        float inX = outX / (float) w;
        float inY = outY / (float) h;
        float2 posIn = (float2) (inX, inY);

        float4 pixel = read_imagef(sourceImage, sampler, posIn);
        write_imagef(targetImage, posOut, pixel);

     }
     """).build()

prg.ImageDS(queue, OutImg.shape, None, dev_Img, dev_OutImg)
cl.enqueue_read_image(queue, dev_OutImg, (0, 0), OutImg.shape, OutImg).wait()
cv2.imwrite("out.jpg", OutImg)
