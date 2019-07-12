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
except Exception:
  pass


class Source(Base, ClangDeopleteSourceBase):
  def __init__(self, vim):
    Base.__init__(self, vim)
    ClangDeopleteSourceBase.__init__(self, vim)

    # The description of a source.
    self.description = 'clang completion'
    # Available filetype list.
    self.filetypes = ['arduino']
    # The mark of a source
    self.mark = '[arduino]'
    # The unique name of a source.
    self.name = 'arduino'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

  def setup_arg_manager(self, vim):
    clang_completer = import_library()
    argument_manager = clang_completer.CPPArgumentManager()

    v = vim.vars
    definitions = v['deoplete#sources#arduino#definitions']
    include_paths = v['deoplete#sources#arduino#include_paths']

    try:
      standard = int(v['deoplete#sources#arduino#standard'])
    except Exception:
      standard = 11

    for ip in include_paths:
      argument_manager.AddIncludePath(ip)
    for d in definitions:
      argument_manager.AddDefinition(d)
    argument_manager.SetCPPStandard(standard)

    self.maybe_add_pio_include_paths(v, argument_manager)
    return argument_manager

  def maybe_add_pio_include_paths(self, v, argument_manager):
    pio_dev = v['deoplete#sources#arduino#enable_platformio_dev']
    pio_root = os.path.expanduser(v['deoplete#sources#arduino#platformio_root'])

    if pio_dev:
      avr_path = os.path.join(pio_root,
          'packages', 'framework-arduinoavr', 'cores', 'arduino')
      if os.path.isdir(avr_path):
        argument_manager.AddIncludePath(avr_path)

      esp_path = os.path.join(pio_root,
          'packages', 'framework-arduinoespressif8266', 'cores', 'esp8266')
      if os.path.isdir(esp_path):
        argument_manager.AddIncludePath(esp_path)

      stm32 = os.path.join(pio_root, 'packages', 'framework-arduinostm32')
      if os.path.isdir(stm32):
        for p in os.listdir(stm32):
          if p not in ['.', '..']:
            stm32_platform = os.path.join(p)
            if os.path.isdir(stm32_platform):
              stm32_path = os.path.join(stm32_platform, 'cores', 'maple')
              argument_manager.AddIncludePath(stm32_path)

  def on_init(self, context):
    argument_manager = self.setup_arg_manager(self.vim)
    completer = ClangCompletionWrapper(argument_manager)
    self.set_completer(completer)

  def on_event(self, context):
    self.update(context)

  def gather_candidates(self, context):
    return self.get_candidates(context)
