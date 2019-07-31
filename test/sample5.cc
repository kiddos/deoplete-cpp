namespace A {
namespace B {

struct Empty {
  int e;
};

class Parent {};

class Child : public Parent {
 public:
  void foo() {}
  Empty bar() { return Empty{}; }
};

}
}


int main(void) {
  A::B::Child c;
  c.foo();
  c.bar().e;
  return 0;
}
