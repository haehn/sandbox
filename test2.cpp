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

  gpu::GpuMat gpu_prev_zoom(src);
  gpu::GpuMat gpu_current_zoom;

  int k=0;

  while(current_rows > target_rows) {

    k++;

    clock_t begin_time = clock();

    gpu::resize(gpu_prev_zoom, gpu_current_zoom, Size(0,0), .5, .5, INTER_AREA);
    Mat out(gpu_current_zoom);

    std::cout << float( clock () - begin_time ) /  CLOCKS_PER_SEC << std::endl;

    // std::ostringstream fn;
    // fn << "/tmp/z" << k << ".jpg";

    //imwrite(fn.str(), out);

    current_rows /= 2;

    gpu_prev_zoom = gpu_current_zoom;

  }

  return 0;
}

