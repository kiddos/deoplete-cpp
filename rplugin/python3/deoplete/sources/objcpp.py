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
    self.filetypes = ['objcpp']
    # The mark of a source
    self.mark = '[objcpp]'
    # The unique name of a source.
    self.name = 'objcpp'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

  def setup_arg_manager(self, vim):
    clang_completer = import_library()
    argument_manager = clang_completer.OBJCPPArgumentManager()

    v = vim.vars
    definitions = v['deoplete#sources#objc#definitions']
    include_paths = v['deoplete#sources#objc#include_paths']

    for ip in include_paths:
      argument_manager.AddIncludePath(ip)
    for d in definitions:
      argument_manager.AddDefinition(d)
    return argument_manager

  def on_init(self, context):
    argument_manager = self.setup_arg_manager(self.vim)
    completer = ClangCompletionWrapper(argument_manager)
    self.set_completer(completer)

  def on_event(self, context):
    self.update(context)

  def gather_candidates(self, context):
    return self.get_candidates(context)
