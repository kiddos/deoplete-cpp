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
    home_dir = os.environ['HOME']
    platformio_dir = os.path.join(home_dir, '.platformio', 'packages')
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'toolchain-atmelavr/include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'toolchain-atmelavr/avr/include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'toolchain-atmelavr/x86_64-pc-linux-gnu/avr/include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-arduinoavr/cores/arduino'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'toolchain-gccarmnoneeabi/arm-none-eabi/include'))

    arduino_libs = os.path.join(platformio_dir,
      'framework-arduinoavr', 'libraries')
    for lib in os.listdir(arduino_libs):
      lib_path = os.path.join(arduino_libs, lib, 'src')
      self._cpp_include_path.append(lib_path)

  def _get_platformio_libs(self, context):
    current_path = context['cwd']
    lib_folder = os.path.join(current_path, '.piolibdeps')
    if os.path.isdir(lib_folder):
      libs = os.listdir(lib_folder)
      for l in libs:
        self._cpp_include_path.append(os.path.join(lib_folder, l))

  def on_init(self, context):
    self._delimiter = ['.', '->', '::']

    self._update_cache(context)
    self._get_platformio_libs(context)

  def on_event(self, context):
    self._update_cache(context)

    m = re.search(r'[^\s-]*$', context['input'])
    return m.start() if m else -1

  def get_complete_position(self, context):
    m = re.search(r'[^\s-]*$', context['input'])
    return m.start() if m else -1

  def gather_candidates(self, context):
    self._update_file_cache(context)

    position = self._get_completion_position(context)
    if position[-1] == 1:
      cache_key = self._get_default_cache_key(context)
    else:
      cache_key = self._get_current_cache_key(context, position)

    parsed_result = []
    if cache_key in self._result_cache:
      parsed_result = self._result_cache[cache_key]
    else:
      self._async_gather_completion(context, position, cache_key)

    self.log('cache: %d, result: %d' %
      (len(self._result_cache), len(parsed_result)))
    return self._get_candidates(parsed_result, self.complete_paren)
