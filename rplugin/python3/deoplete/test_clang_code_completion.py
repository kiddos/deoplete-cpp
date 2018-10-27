# -*- coding: utf-8 -*-

import os
import unittest

import clang_util as cc


class TestSetup(unittest.TestCase):
  def test_setup_libclang(self):
    self.assertTrue(cc.setup_libclang('6.0'))


def load_source(index, filepath, unsaved_files):
  args = ['-O0', '-g', '-x', 'c++', '-std=c++11']

  dirname = os.path.realpath(os.path.dirname(__file__))
  filepath = os.path.join(dirname, filepath)
  with open(filepath, 'r') as f:
    content = f.read()

    unsaved_files.append((filepath, content))
    return cc.Source(index, filepath, args, unsaved_files)


class TestCppSourceBasic(unittest.TestCase):
  def setUp(self):
    cc.setup_libclang('6.0')
    self.index = cc.create_index()
    self.unsaved_files = []

    self.source = load_source(self.index,
      './test_sources/source.cc', self.unsaved_files)
    self.object_source = load_source(self.index,
      './test_sources/objects.cc', self.unsaved_files)

    self.source.complete_function = True
    self.source.complete_template = True
    self.source.complete_constructor = True
    self.source.complete_destructor = True

  def test_setup(self):
    self.assertNotEqual(self.source.tu, None)

  def test_code_completion_with_fake_file(self):
    filepath = './test_sources/does_not_exists.cc'
    args = ['-O0', '-g', '-x', 'c++']
    content = ''
    cc.Source(self.index, filepath, args, [(filepath, content)])

  def test_clang_code_complete(self):
    print(self.unsaved_files)
    self.source.code_complete(8, 5, self.unsaved_files)

  def test_reparse(self):
    self.source.reparse(self.unsaved_files)

  def test_get_index(self):
    index = self.source.get_index(7, 10)
    self.assertEqual(self.source.content[index], 'p')

    index = self.source.get_index(8, 3)
    self.assertEqual(self.source.content[index], 'p')

  def test_get_closest_token(self):
    token, operator = self.source.find_closest_token(8, 5)
    self.assertEqual(token, 'p')
    self.assertEqual(operator, '.')

    token, operator = self.source.find_closest_token(11, 15)
    self.assertEqual(token, 'cool_mouse')
    self.assertEqual(operator, '->')

    token, operator = self.source.find_closest_token(13, 6)
    self.assertEqual(token, 'A')
    self.assertEqual(operator, '::')

    token, operator = self.source.find_closest_token(18, 9)
    self.assertEqual(token, 'A::B')
    self.assertEqual(operator, '::')

    token, operator = self.source.find_closest_token(9, 1)
    self.assertEqual(token, None)
    self.assertEqual(operator, None)

  def test_find_closest_cursor(self):
    closest = self.source.find_closest_parent(8, 4)
    self.assertEqual(closest.displayname, 'main()')

    closest = self.source.find_closest_parent(11, 11)
    self.assertEqual(closest.displayname, 'main()')

    closest = self.source.find_closest_parent(38, 2)
    self.assertEqual(closest.displayname, 'main()')

    closest = self.source.find_closest_parent(39, 11)
    self.assertEqual(closest.displayname, 'main()')

  def test_code_complete_object(self):
    completion = self.source.code_complete_semantic(8, 5)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

  def test_code_complete_pointer_object(self):
    completion = self.source.code_complete_semantic(16, 7)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

  def test_code_complete_namespace(self):
    completion = self.source.code_complete_semantic(13, 6)
    completion = [c['word'] for c in completion]
    self.assertIn('function4()', completion)
    self.assertIn('function5(double, double)', completion)
    self.assertIn('function6(T, U)', completion)
    self.assertIn('B', completion)
    self.assertIn('Object', completion)
    self.assertIn('A<T>', completion)

  def test_code_complete_inner_namespace(self):
    completion = self.source.code_complete_semantic(18, 9)
    completion = [c['word'] for c in completion]
    self.assertIn('function7()', completion)
    self.assertIn('B<T, U>', completion)
    self.assertNotIn('EmptyB()', completion)

  def test_code_complete_empty(self):
    completion = self.source.code_complete_semantic(14, 1)
    completion = [c['word'] for c in completion]
    self.assertIn('function1()', completion)
    self.assertIn('function2(int, int)', completion)
    self.assertIn('function3(T, T)', completion)
    self.assertIn('A', completion)
    self.assertIn('Person', completion)
    self.assertIn('MutatedPerson<T>', completion)
    self.assertIn('Group', completion)
    self.assertIn('Bag', completion)
    self.assertIn('Mouse<T>', completion)
    self.assertIn('B', completion)
    self.assertIn('main()', completion)

  def test_code_complete_spaces(self):
    completion = self.source.code_complete_semantic(32, 1)
    completion = [c['word'] for c in completion]
    self.assertIn('function1()', completion)
    self.assertIn('function2(int, int)', completion)
    self.assertIn('function3(T, T)', completion)
    self.assertIn('A', completion)
    self.assertIn('Person', completion)
    self.assertIn('MutatedPerson<T>', completion)
    self.assertIn('Group', completion)
    self.assertIn('Bag', completion)
    self.assertIn('Mouse<T>', completion)
    self.assertIn('B', completion)
    self.assertIn('main()', completion)

  def test_code_complete_global(self):
    completion = self.source.code_complete_semantic(5, 1)
    completion = [c['word'] for c in completion]
    self.assertIn('function1()', completion)
    self.assertIn('function2(int, int)', completion)
    self.assertIn('function3(T, T)', completion)
    self.assertIn('A', completion)
    self.assertIn('Person', completion)
    self.assertIn('MutatedPerson<T>', completion)
    self.assertIn('Group', completion)
    self.assertIn('Bag', completion)
    self.assertIn('Mouse<T>', completion)
    self.assertIn('B', completion)
    self.assertIn('main()', completion)

  def test_code_completion_array_element(self):
    completion = self.source.code_complete_semantic(24, 13)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

  def test_code_completion_function_proto(self):
    completion = self.source.code_complete_semantic(26, 19)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

  def test_code_completion_class_template_method(self):
    completion = self.source.code_complete_semantic(29, 9)
    completion = [c['word'] for c in completion]
    self.assertIn('Move()', completion)
    self.assertIn('x', completion)
    self.assertIn('y', completion)

  def test_code_completion_object_members_parts(self):
    completion = self.source.code_complete_semantic(31, 9)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

    completion = self.source.code_complete_semantic(31, 7)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

    completion = self.source.code_complete_semantic(31, 5)
    completion = [c['word'] for c in completion]
    self.assertIn('say()', completion)
    self.assertIn('age', completion)
    self.assertIn('id_', completion)

  def test_object_constructor_completion(self):
    completion = self.object_source.code_complete_semantic(4, 10)
    completion = [c['word'] for c in completion]
    self.assertIn('data', completion)
    self.assertIn('a', completion)
    self.assertIn('Stuff()', completion)

  def test_object_destructor_completion(self):
    completion = self.object_source.code_complete_semantic(8, 10)
    completion = [c['word'] for c in completion]
    self.assertIn('data', completion)
    self.assertIn('a', completion)
    self.assertIn('Stuff()', completion)

  def test_object_method_implementation(self):
    completion = self.object_source.code_complete_semantic(11, 6)
    completion = [c['word'] for c in completion]
    self.assertIn('Bag()', completion)
    self.assertIn('~Bag()', completion)
    self.assertIn('Release()', completion)
    self.assertIn('stuff_', completion)
    self.assertIn('size_', completion)
    self.assertIn('count', completion)

  def test_recursive_inner_members(self):
    completion = self.source.code_complete_semantic(34, 9)
    completion = [c['word'] for c in completion]
    self.assertIn('Outer()', completion)
    self.assertIn('Inner', completion)
    self.assertIn('inner_', completion)

    completion = self.source.code_complete_semantic(35, 16)
    completion = [c['word'] for c in completion]
    self.assertIn('InnerInner', completion)
    self.assertIn('inner_inner_', completion)

    completion = self.source.code_complete_semantic(36, 29)
    completion = [c['word'] for c in completion]
    self.assertIn('InnerInnerInner', completion)
    self.assertIn('inner_inner_inner_', completion)

    completion = self.source.code_complete_semantic(37, 48)
    completion = [c['word'] for c in completion]
    self.assertIn('data', completion)

  def test_crash(self):
    content = self.source.content
    lines = content.split('\n')

    try:
      for line, l in enumerate(lines):
        for i in range(len(l)):
          self.source.code_complete_semantic(line + 1, i + 1)
    except Exception:
      self.assertTrue(False)


class TestStdSource(unittest.TestCase):
  def setUp(self):
    print(cc.setup_libclang('6.0'))
    self.index = cc.create_index()
    self.unsaved_files = []
    self.std_source = load_source(self.index,
      './test_sources/std_source.cc', self.unsaved_files)

    self.std_source.complete_function = True
    self.std_source.complete_template = True
    self.std_source.complete_constructor = True
    self.std_source.complete_destructor = True

    self.std_source2 = load_source(self.index,
      './test_sources/std_source2.cc', self.unsaved_files)
    #  self.std_source2.reparse(self.unsaved_files)
    self.std_source2.complete_function = True
    self.std_source2.complete_template = True
    self.std_source2.complete_constructor = True
    self.std_source2.complete_destructor = True

  def test_std_members(self):
    completion = self.std_source.code_complete_semantic(16, 8)
    completion = [c['word'] for c in completion]
    self.assertIn('vector<_Tp, _Alloc>', completion)

    self.assertIn('initializer_list<_E>', completion)

    self.assertIn('thread', completion)
    self.assertIn('this_thread', completion)

    self.assertIn('cout', completion)
    self.assertIn('cerr', completion)
    self.assertIn('clog', completion)

    self.assertIn('basic_string<char>', completion)

    self.assertIn('ofstream', completion)
    self.assertIn('ifstream', completion)
    self.assertIn('stringstream', completion)

    self.assertIn('normal_distribution<_RealType>', completion)
    self.assertIn('uniform_int_distribution<_IntType>', completion)
    self.assertIn('mt19937', completion)
    self.assertIn('mt19937_64', completion)

    self.assertIn('complex<_Tp>', completion)

    self.assertIn('exception', completion)
    self.assertIn('bad_exception', completion)

    self.assertIn('shared_ptr<_Tp>', completion)
    self.assertIn('unique_ptr<_Tp, _Dp>', completion)
    self.assertIn('weak_ptr<_Tp>', completion)
    self.assertIn('auto_ptr<_Tp>', completion)
    self.assertIn('make_shared(_Args &&...)', completion)

    self.assertIn(
      'all_of(_InputIterator, _InputIterator, _Predicate)',
      completion)

    self.assertIn('copy(_IIter, _IIter, _OIter)', completion)
    self.assertIn('copy_if(_IIter, _IIter, _OIter, _Predicate)',
      completion)
    self.assertIn('copy_n(_IIter, _Size, _OIter)', completion)

    self.assertIn('setw(int)', completion)
    self.assertIn('setprecision(int)', completion)
    self.assertIn('setfill(_CharT)', completion)
    self.assertIn('setbase(int)', completion)

  def test_vector_members(self):
    completion = self.std_source.code_complete_semantic(19, 5)
    completion = [c['word'] for c in completion]
    self.assertIn('size()', completion)

    completion = self.std_source2.code_complete_semantic(6, 5)
    completion = [c['word'] for c in completion]
    print(completion)

  def test_crash(self):
    content = self.std_source.content
    lines = content.split('\n')
    try:
      for line, l in enumerate(lines):
        for i in range(len(l)):
          self.std_source.code_complete_semantic(line + 1, i + 1)
    except Exception:
      self.assertTrue(False)


class TestOpenCVSource(unittest.TestCase):
  def setUp(self):
    cc.setup_libclang('6.0')
    self.index = cc.create_index()
    self.unsaved_files = []
    self.opencv_source = load_source(self.index,
      './test_sources/opencv_source.cc', self.unsaved_files)

  def test_clang_code_complete(self):
    self.opencv_source.code_complete(6, 7, self.unsaved_files)

  def test_opencv_source(self):
    completion = self.opencv_source.code_complete_semantic(6, 7)
    completion = [c['word'] for c in completion]
    self.assertIn('Mat', completion)
    self.assertIn('Mat_<_Tp>', completion)

    completion = self.opencv_source.code_complete_semantic(10, 7)
    completion = [c['word'] for c in completion]
    self.assertIn('rows', completion)
    self.assertIn('cols', completion)
    self.assertIn('size', completion)
    self.assertIn('data', completion)
    self.assertIn('at(int)', completion)
    self.assertIn('ptr(int)', completion)
    self.assertIn('empty()', completion)
    self.assertIn('total()', completion)


class TestGRPCSource(unittest.TestCase):
  def setUp(self):
    cc.setup_libclang('6.0')
    self.index = cc.create_index()
    self.unsaved_files = []
    self.grpc_source = load_source(self.index,
      './test_sources/grpc_source.cc', self.unsaved_files)

  def test_grpc_source(self):
    completion = self.grpc_source.code_complete_semantic(13, 9)
    completion = [c['word'] for c in completion]
    self.assertIn('Channel', completion)
    self.assertIn('Server', completion)
    self.assertIn('ServerBuilder', completion)


class TestCSourceBasic(unittest.TestCase):
  def setUp(self):
    cc.setup_libclang('6.0')
    self.index = cc.create_index()
    self.unsaved_files = []

    self.source = load_source(self.index,
      './test_sources/source.c', self.unsaved_files)

  def test_completion(self):
    completion = self.source.code_complete_semantic(5, 1)
    completion = [c['word'] for c in completion]
    print(completion)


def main():
  unittest.main()


if __name__ == '__main__':
  main()
