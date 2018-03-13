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

    self.name = 'cpp'
    self.mark = '[c++]'
    self.rank = 600
    self.debug_enabled = False
    self.filetypes = ['c', 'cpp', 'objc', 'objcpp']
    self.max_menu_width = 160
    self.max_abbr_width = 160

    self._init_vars()

  def _init_vars(self):
    v = self.vim.vars
    self._get_detail = v['deoplete#sources#cpp#get_detail']
    self.complete_paren = v['deoplete#sources#cpp#complete_paren']

    # include flags
    self._cflags = v['deoplete#sources#cpp#cflags']
    self._cppflags = v['deoplete#sources#cpp#cppflags']
    self._objcflags = v['deoplete#sources#cpp#objcflags']
    self._objcppflags = v['deoplete#sources#cpp#objcppflags']

    # include path
    self._c_include_path = v['deoplete#sources#cpp#c_include_path']
    self._cpp_include_path = v['deoplete#sources#cpp#cpp_include_path']
    self._objc_include_path = v['deoplete#sources#cpp#objc_include_path']
    self._objcpp_include_path = v['deoplete#sources#cpp#objcpp_include_path']

  def on_init(self, context):
    if context['filetype'] == 'c':
      self.input_pattern = (
          r'[^.\s\t\d\n_]\.\w*|'
          r'[^.\s\t\d\n_]->\w*')
      self._delimiter = ['.', '->']
    else:
      self.input_pattern = (
          r'[^.\s\t\d\n_]\.\w*|'
          r'[^.\s\t\d\n_]->\w*|'
          r'[\w\d]::\w*')
      self._delimiter = ['.', '->', '::']

    # cache the file
    self._update_file_cache(context)
    self._setup_completion_cache(context)

  def on_event(self, context):
    self._update_file_cache(context)
    self._setup_completion_cache(context)

    m = re.search(r'\w*$', context['input'])
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
