#include <iostream>

struct Test {
  int a;
  double b;
};

int main(void) {
  Test t{1, 2.0};
  Test* t2 = &t;

  std::cout << t2->a << t.b << std::endl;
  return 0;
}
