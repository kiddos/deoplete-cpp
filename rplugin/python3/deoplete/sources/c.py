# -*- coding: utf-8 -*-

import os
import sys

from .base import Base
from deoplete.util import load_external_module


try:
  current = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  sys.path.insert(0, current)

  from clang_source_base import import_library
  from clang_source_base import ClangDeopleteSourceBase
  from clang_source_base import ClangCompletionWrapper
except Exception as e:
  pass


class Source(Base, ClangDeopleteSourceBase):
  def __init__(self, vim):
    Base.__init__(self, vim)
    argument_manager = self.setup_arg_manager(vim)
    completer = ClangCompletionWrapper(argument_manager)
    ClangDeopleteSourceBase.__init__(self, vim, completer)

    # The description of a source.
    self.description = 'clang completion'
    # Available filetype list.
    self.filetypes = ['c']
    # The mark of a source
    self.mark = '[c]'
    # The unique name of a source.
    self.name = 'c'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

  def setup_arg_manager(self, vim):
    clang_completer = import_library()
    argument_manager = clang_completer.CArgumentManager()

    v = vim.vars
    definitions = v['deoplete#sources#c#definitions']
    include_paths = v['deoplete#sources#c#include_paths']

    try:
      standard = int(v['deoplete#sources#c#standard'])
    except Exception:
      standard = 99

    for ip in include_paths:
      argument_manager.AddIncludePath(ip)
    for d in definitions:
      argument_manager.AddDefinition(d)
    argument_manager.SetCStandard(standard)

    self.maybe_add_kernel_include_path(v, argument_manager)
    self.maybe_add_pio_include_paths(v, argument_manager)
    return argument_manager

  def maybe_add_kernel_include_path(self, v, argument_manager):
    kernel_dev = v['deoplete#sources#c#enable_kernel_dev']
    kernel_root = v['deoplete#sources#c#kernel_root']
    if kernel_dev:
      argument_manager.AddIncludePath(kernel_root)
      argument_manager.AddIncludePath(os.path.join(kernel_root, 'include'))

  def maybe_add_pio_include_paths(self, v, argument_manager):
    pio_dev = v['deoplete#sources#c#enable_platformio_dev']
    pio_root = os.path.expanduser(v['deoplete#sources#c#platformio_root'])

    if pio_dev and os.path.isdir(pio_root):
      avr_path = os.path.join(pio_root,
          'packages', 'framework-arduinoavr', 'cores', 'arduino')
      if os.path.isdir(avr_path):
        argument_manager.AddIncludePath(avr_path)

      # stm32
      arduino_stm32 = os.path.join(pio_root, 'packages',
        'framework-arduinostm32')
      if os.path.isdir(arduino_stm32):
        for p in os.listdir(arduino_stm32):
          if p not in ['.', '..']:
            stm32_platform = os.path.join(arduino_stm32, p)
            if os.path.isdir(stm32_platform):
              stm32_path = os.path.join(stm32_platform, 'cores', 'maple')
              argument_manager.AddIncludePath(stm32_path)

      stm32_cube = os.path.join(pio_root, 'packages', 'framework-stm32cube')
      if os.path.isdir(stm32_cube):
        for p in os.listdir(stm32_cube):
          if p not in ['.', '..']:
            stm32_platform = os.path.join(stm32_cube, p)
            if os.path.isdir(stm32_platform):
              stm32_path = os.path.join(stm32_platform, 'Drivers',
                  'STM32%sxx_HAL_Driver' % (p.upper()), 'Inc')
              stm32_path = os.path.join(stm32_platform, 'Drivers'
                  'CMSIS', 'Include')
              argument_manager.AddIncludePath(stm32_path)

      # mbed
      mbed_path = os.path.join(pio_root, 'packages', 'framework-mbed')
      if os.path.isdir(mbed_path):
        argument_manager.AddIncludePath(mbed_path)

      # simba
      simba_path = os.path.join(pio_root, 'packages', 'framework-simba', 'src')
      if os.path.isdir(simba_path):
        argument_manager.AddIncludePath(simba_path)

  def on_event(self, context):
    self.update(context)

  def gather_candidates(self, context):
    return self.get_candidates(context)
