# -*- coding: utf-8 -*-

import os
import sys
import re

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
    ClangCompletion.__init__(self, vim)

    # The description of a source.
    self.description = 'clang cpp completion'
    # Available filetype list.
    self.filetypes = ['arduino']
    # The mark of a source
    self.mark = '[arduino]'
    # The unique name of a source.
    self.name = 'arduino'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

    self.max_menu_width = 160
    self.max_abbr_width = 160

  def _setup_arduino_path(self):
    home_dir = os.environ['HOME']
    platformio_dir = os.path.join(home_dir, '.platformio', 'packages')
    # arduino
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-arduinoavr/cores/arduino/'))
    # simba
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-simba/src'))
    # stm32 boards
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f0/Drivers/STM32F0xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f0/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f1/Drivers/STM32F1xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f1/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f2/Drivers/STM32F2xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f2/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f3/Drivers/STM32F3xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f3/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f4/Drivers/STM32F4xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f4/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f7/Drivers/STM32F7xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/f7/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l0/Drivers/STM32L0xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l0/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l1/Drivers/STM32L1xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l1/Drivers/CMSIS/Include'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l4/Drivers/STM32L4xx_HAL_Driver/Inc'))
    self._cpp_include_path.append(os.path.join(platformio_dir,
      'framework-stm32cube/l4/Drivers/CMSIS/Include'))

    arduino_libs = os.path.join(platformio_dir,
      'framework-arduinoavr/libraries')
    for lib in os.listdir(arduino_libs):
      lib_path = os.path.join(arduino_libs, lib, 'src')
      self._cpp_include_path.append(lib_path)

    self._padd_include = 0

  def _add_pio_libs(self, context):
    current_path = context['cwd']
    lib_folder = os.path.join(current_path, '.piolibdeps')
    if os.path.isdir(lib_folder):
      libs = os.listdir(lib_folder)
      for l in libs:
        self._cpp_include_path.append(os.path.join(lib_folder, l))

  def on_init(self, context):
    self._add_pio_libs(context)
    # cache the file
    self.setup()
    self._update(context)

  def on_event(self, context):
    self._update(context)

  def get_buffer_name(self, context):
    buffer_name = context['bufname'] + '.cc'
    return os.path.join(context['cwd'], buffer_name)

  def _update_file_content(self, context):
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)

    include_pattern = re.compile(r'\s*#include\s*<Arduino.h>')
    if not include_pattern.findall(content):
      content = '#include <Arduino.h>\n' + content
      self._padd_include = 1

    self._file_contents[filepath] = content

  def _get_cursor_pos(self):
    line = self.vim.eval('line(".")') + self._padd_include
    col = self.vim.eval('col(".")')
    return line, col

  def gather_candidates(self, context):
    self._update(context)
    return self._get_candidates(context)
