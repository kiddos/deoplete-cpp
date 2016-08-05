#include <iostream>

using std::cout;

namespace test {

struct Size {
  int width, height;
};

class Test {
 public:
  Test() : a(0), d(100) {}
  int geta() { return a; }
  double getd() { return d; }
  Size getsize() { return size; }
 private:
  int a;
  double d;
  Size size;
};

void test_func1() {
  cout << "hello world!!\n";

}

}

int main(void) {
  test::test_func1();
  test::Test t;
  cout << t.geta() << t.getd() <<
      t.getsize().width << t.getsize().height << '\n';
  return 0;
}
