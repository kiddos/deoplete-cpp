# -*- coding: utf-8 -*-

import subprocess
import traceback
import os
import re
import sys

from .base import Base
from deoplete.util import load_external_module

try:
  current = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  sys.path.insert(0, current)

  from clang_util import ClangCompletion
except Exception as e:
  pass

class Source(Base, ClangCompletion):
  def __init__(self, vim):
    Base.__init__(self, vim)
    clang_version = vim.vars['deoplete#sources#cpp#clang_version']
    ClangCompletion.__init__(self, vim, clang_version)

    self.name = 'cuda'
    self.mark = '[cuda]'
    self.rank = 600
    self.debug_enabled = False
    self.filetypes = ['cuda']
    self.input_pattern = (
        r'[^.\s\t\d\n_]\.\w*|'
        r'[^.\s\t\d\n_]->\w*|'
        r'[\w\d]::\w*')
    self.max_menu_width = 160
    self.max_abbr_width = 160

    self._c_include_path = \
        self.vim.vars['deoplete#sources#cpp#c_include_path']
    self._cpp_include_path = \
        self.vim.vars['deoplete#sources#cpp#cpp_include_path']
    # cuda path
    self._cuda_path = self.vim.vars['deoplete#sources#cpp#cuda_path']

  def _setup_cuda_includes(self):
    for p in self._cuda_path:
      self._cppflags.append('-I%s' % (p))

  def _update_file_cache(self, context):
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)

    cuda = re.compile(r'\s*#include\s*<cuda_runtime_api.h>')
    if not cuda.findall(content):
      content = '#include <cuda.h>\n' + content
      content = '#include <cuda_runtime_api.h>\n' + content
    self._file_cache[filepath] = content

  def on_init(self, context):
    self._delimiter = ['.', '->', '::']

    self._update_file_cache(context)
    self._setup_completion_cache(context)

  def on_event(self, context):
    self.on_init(context)

  def get_complete_position(self, context):
    m = re.search(r'[^\s-]*$', context['input'])
    return m.start() if m else -1

  def gather_candidates(self, context):
    self._update_file_cache(context)

    cache_key = self._get_current_cache_key(context, context['position'][1:])
    position = self._get_completion_position(context)
    parsed_result = []
    if cache_key not in self._result_cache:
      parsed_result = self._gather_and_cache_completion(
        context, position, cache_key)
    else:
      parsed_result = self._result_cache[cache_key]
    return self._get_candidates(parsed_result, self.complete_paren)
