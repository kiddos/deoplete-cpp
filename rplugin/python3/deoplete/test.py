import os
import ctypes


def import_library():
  current_dir = os.path.dirname(os.path.realpath(__file__))
  clang_location = os.path.join(current_dir,
    '../../../build/clang/lib/libclang.so')

  ctypes.cdll.LoadLibrary(clang_location)

  try:
    import clang_completer
    return clang_completer
  except ImportError:
    return False


from clang_source_base import ClangCompletionWrapper

clang_completer = import_library()

argument_manager = clang_completer.ArgumentManager()
argument_manager.AddIncludePath('/usr/local/include')
argument_manager.AddDefinition('DEBUG')
completer = ClangCompletionWrapper(argument_manager)

filepath = 'test_sources/source.cc'
with open(filepath) as f:
  content = f.read()

completer.add_file(filepath, content)
result = completer.code_complete(filepath, content, 8, 5)
for r in result:
  #  if r['word'] == 'printf':
  print(r)
print(result)
