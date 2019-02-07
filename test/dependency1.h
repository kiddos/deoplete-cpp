#include <iostream>

void Foo() {}

bool Bar() { return false; }

class FooBar {
 public:
  FooBar() {}
};

class Abstract {
 public:
  Abstract();

  void Foo();
  void Bar();
};
