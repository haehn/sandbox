#include <opencv2/opencv.hpp>
#include <opencv2/gpu/gpu.hpp>
#include <time.h>

using namespace cv;
int main() {
  Mat src = imread("test.tif", 0);
  if (!src.data) exit(1);

  int rows = src.rows;
  int current_rows = rows;
  int target_rows = 512;


  gpu::GpuMat gpu_src(src);
  gpu::GpuMat gpu_dst = gpu_src;
  gpu::GpuMat gpu_new_dst;


  Point2f src_center(-0.00283685, 0.00271015);



  Mat M = getRotationMatrix2D(src_center, 0., 1.0);//= (Mat_<double>(3,2) << 1, 0, -0.00283685, 0, 1, 0.00271015);


  gpu::warpAffine(gpu_src, gpu_dst, M, src.size(), INTER_LINEAR);


  int k=0;

  while(current_rows > target_rows) {

    k++;

    current_rows /= 2;

    clock_t begin_time = clock();    

    gpu::pyrDown(gpu_dst, gpu_new_dst);
    // gpu::resize(gpu_dst, gpu_new_dst, Size(0,0), .5, .5, INTER_AREA);

    std::cout << float( clock () - begin_time ) /  CLOCKS_PER_SEC << std::endl;    

    std::ostringstream fn;
    fn << "/tmp/newopencv_gpu_" << k << ".jpg";

    Mat out(gpu_new_dst);

    // imwrite(fn.str(), out);

    gpu_dst = gpu_new_dst;


  }  

  return 0;
}

