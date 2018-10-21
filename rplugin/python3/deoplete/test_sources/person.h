#ifndef PERSON_H
#define PERSON_H

class Person {
 public:
  Person() : id_(0) {}
  ~Person() {}

  void say() {}

  double age;

 private:
  int id_;
};

template <typename T>
class MutatedPerson : public Person {
};

#endif /* end of include guard: PERSON_H */
