void function1() {}

int function2(int a, int b) { return a + b; }

template <typename T>
T function3(T a, T b) {
  return a - b;
}

namespace A {

void function4() {}

double function5(double a, double b) { return a * b; }

template <typename T, typename U>
T function6(T a, U b) {
  return a / b;
}

namespace B {

void function7() {}

}
// namespace B

}  // namespace A
