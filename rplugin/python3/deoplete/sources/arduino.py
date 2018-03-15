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

    self.name = 'arduino'
    self.mark = '[arduino]'
    self.rank = 600
    self.debug_enabled = False
    self.filetypes = ['arduino']
    self.input_pattern = (
        r'[^.\s\t\d\n_]\.\w*|'
        r'[^.\s\t\d\n_]->\w*|'
        r'[\w\d]::\w*')
    self.max_menu_width = 160
    self.max_abbr_width = 160

    # arduino path
    self._arduino_path = self.vim.vars['deoplete#sources#cpp#arduino_path']
    self._setup_arduino_path()

  def _update_file_cache(self, context):
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)

    arduino = re.compile(r'\s*#include\s*<Arduino.h>')
    if not arduino.findall(content):
      content = '#include <Arduino.h>\n' + content
    self._file_cache[filepath] = content

  def _setup_arduino_path(self):
    self._arduino_include_path = []
    if os.path.isdir(self._arduino_path):
      arduino_core = os.path.join(self._arduino_path,
        'hardware/arduino/cores/arduino')
      arduino_library = os.path.join(self._arduino_path, 'libraries')
      self._arduino_include_path += [arduino_core] + \
        [os.path.join(arduino_library, lib)
          for lib in os.listdir(arduino_library)
          if os.path.isdir(os.path.join(arduino_library, lib))]
      self._cppflags += ['-I%s' % (p) for p in self._arduino_include_path]

  def _get_platformio_libs(self, context):
    current_path = context['cwd']
    lib_folder = os.path.join(current_path, '.piolibdeps')
    libs = os.listdir(lib_folder)
    for l in libs:
      self._cppflags.append('-I%s' % (os.path.join(lib_folder, l)))

    with open('/home/joseph/.vim-log', 'w') as f:
      f.write(str(self._cppflags))

  def on_init(self, context):
    self._delimiter = ['.', '->', '::']

    self._update_file_cache(context)
    self._setup_completion_cache(context)
    self._get_platformio_libs(context)

  def on_event(self, context):
    self._update_file_cache(context)

    if context['event'] == 'BufWritePost':
      self._setup_completion_cache(context)
    self._cache_delimiter_completion(context)

    m = re.search(r'[^\s-]*$', context['input'])
    return m.start() if m else -1

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
