import os
import ctypes
import glob
import threading


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


clang_completer = import_library()


class ClangCompletionWrapper(object):
  def __init__(self, arg_manager):
    self._completer = clang_completer.ClangCompleter()
    self._arg_manager = arg_manager
    self._runner = None
    self._updating = False

  def update_sync(self, filepath, content):
    self._updating = True
    self._completer.Parse(filepath, content, self._arg_manager)
    self._completer.Update(self._arg_manager)
    self._updating = False

  def update_async(self, filepath, content):
    """
    reparse the translation unit in completer
    if the translation unit is not in the completer
    the completer will add the translation unit
    """
    if not self._updating:
      self._updating = True
      self._runner = threading.Thread(target=self.update_sync,
                                      args=(filepath,content,))
      self._runner.daemon = True
      self._runner.start()

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
  def __init__(self, vim):
    self.vim = vim
    self._completer = None

  def set_completer(self, completer):
    self._completer = completer

  def log(self, msg):
    """
    log message to vim console
    """
    self.vim.command('echom "%s"' % (msg))

  def get_buffer_name(self):
    """
    retrieve buffer name from current content
    """
    return self.vim.eval('expand("%:p")')

  def get_buffer_content(self):
    return self.vim.eval('join(getline(1, "$"), "\n")')
    #  return '\n'.join(self.vim.current.buffer)

  def search_for_includes(self):
    current_dir = self.vim.command_output('pwd')
    includes = glob.glob(current_dir + '/**/include/', recursive=True)
    includes += glob.glob(current_dir + '/**/src/', recursive=True)
    includes += glob.glob(current_dir + '/**/build/', recursive=True)
    return includes

  def update(self, context):
    """
    update both file content and source object
    """
    if self._completer:
      filepath = self.get_buffer_name()
      content = self.get_buffer_content()
      self._completer.update_async(filepath, content)

  def get_candidates(self, context):
    """
    retrive candidate from source object
    """
    if self._completer:
      line = self.vim.eval('line(".")')
      col = self.vim.eval('col(".")')
      filepath = self.get_buffer_name()
      content = self.get_buffer_content()
      return self._completer.code_complete(filepath, content, line, col)
    return []
