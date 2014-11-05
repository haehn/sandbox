#include <opencv2/opencv.hpp>
#include <time.h>
using namespace cv;
int main() {
  Mat src = imread("test.tif", 0);
  if (!src.data) exit(1);

  int rows = src.rows;
  int current_rows = rows;
  int target_rows = 512;

  Mat prev_zoom(src);
  Mat current_zoom;

  int k=0;

  while(current_rows > target_rows) {

    k++;

    // clock_t begin_time = clock();    

    resize(prev_zoom, current_zoom, Size(0,0), .5, .5, INTER_AREA);

    

    // std::cout << float( clock () - begin_time ) /  CLOCKS_PER_SEC << std::endl;
    

    std::ostringstream fn;
    fn << "/tmp/no_gpu_z" << k << ".jpg";

    imwrite(fn.str(), current_zoom);

    current_rows /= 2;

    prev_zoom = current_zoom;

  }

  return 0;
}

