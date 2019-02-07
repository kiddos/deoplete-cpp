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
  except ImportError as e:
    return False


clang_completer = import_library()


class ClangCompletionWrapper(object):
  def __init__(self, arg_manager):
    self._completer = clang_completer.ClangCompleter()
    self._arg_manager = arg_manager

  def add_file(self, filepath, content):
    """
    store file as translation unit in completer
    """
    self._completer.AddFile(filepath, content, self._arg_manager)

  def reparse_file(self, filepath, content):
    """
    reparse the translation unit in completer
    if the translation unit is not in the completer
    the completer will add the translation unit
    """
    self._completer.Reparse(filepath, content)

  def process_clang_result(self, result):
    processed = {
      'word': '',
      'kind': '',
      'menu': '',
      'info': '',
      'abbr': '',
    }
    completed = ''
    for pair in result:
      if pair[0] == 'TypedText':
        processed['word'] = processed['abbr'] = pair[1]
      if pair[0] == 'ResultType':
        processed['menu'] = pair[1]
      else:
        completed += pair[1]
    processed['kind'] = processed['info'] = completed
    return processed

  def process_clang_results(self, results):
    processed = []
    for result in results:
      processed.append(self.process_clang_result(result))
    return processed

  def code_complete(self, filepath, content, line, column):
    """
    retrive candidate from completer
    """
    results = self._completer.CodeComplete(filepath, content, line, column,
      self._arg_manager)
    return self.process_clang_results(results)


class ClangDeopleteSourceBase(object):
  def __init__(self, vim, completer):
    self.vim = vim
    self._completer = completer

  def log(self, msg):
    """
    log message to vim console
    """
    self.vim.command('echom "%s"' % (msg))

  def get_buffer_name(self, context):
    """
    retrieve buffer name from current content
    """
    return self.vim.eval('expand("%:p")')

  def update(self, context):
    """
    update both file content and source object
    """
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)
    self._completer.add_file(filepath, content)

  def get_candidates(self, context):
    """
    retrive candidate from source object
    """
    line = self.vim.eval('line(".")')
    col = self.vim.eval('col(".")')
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)
    return self._completer.code_complete(filepath, content, line, col)
