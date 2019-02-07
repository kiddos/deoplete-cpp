#include <stdio.h>
#include <stdlib.h>

struct simple {
  int i;
  double d;
};

void test_func1() {
  printf("hello world!!\n");

}

struct simple test_func2() {
  struct simple s = {1, 6.0};
  return s;
}

int main(void) {
  test_func1();
  struct simple s = test_func2();
  printf("s.i=%d, s.d=%lf\n", s.i, s.d);
  s.
  return 0;
}
