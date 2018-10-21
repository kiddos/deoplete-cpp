#ifndef OBJECTS_H
#define OBJECTS_H

#include "person.h"

class Group {
 public:
  Person person(int i) const { return people[i]; }

 private:
  Person people[100];
};

struct Stuff {
  double data;
  int a[10];

  Stuff() {}
};

class Bag {
 public:
  Bag();
  ~Bag();

  void Release();

 private:
  Stuff stuff_;
  int size_;

  static int count;
};

template <typename T>
class Mouse {
 public:
  void Move() {}

 private:
  T x, y;
};

namespace B {

void EmptyB() {}

}

namespace A {

class Object {
 public:
  Object() : id_(0) {}

  int id() const { return id_; }

 private:
  int id_;
};

template <typename T>
class A {
};

namespace B {

template <typename T, typename U>
class B {
};

}

}  // namespace A

class Outer {
 public:
  Outer();

 private:
  class Inner {
   private:
    class InnerInner {
     private:
      struct InnerInnerInner {
        int data;
      };

      InnerInnerInner inner_inner_inner_;
    };

    InnerInner inner_inner_;
  };

  Inner inner_;
};

#endif /* end of include guard: OBJECTS_H */
