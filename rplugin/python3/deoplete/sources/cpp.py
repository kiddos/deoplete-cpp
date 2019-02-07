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
    self.description = 'clang cpp completion'
    # Available filetype list.
    self.filetypes = ['cpp']
    # The mark of a source
    self.mark = '[c++]'
    # The unique name of a source.
    self.name = 'cpp'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

  def setup_arg_manager(self, vim):
    clang_completer = import_library()
    argument_manager = clang_completer.CPPArgumentManager()

    v = vim.vars
    definitions = v['deoplete#sources#cpp#cpp_definitions']
    include_paths = v['deoplete#sources#cpp#cpp_include_paths']

    try:
      standard = int(v['deoplete#sources#cpp#cpp_standard'])
    except Exception:
      standard = 11

    for ip in include_paths:
      argument_manager.AddIncludePath(ip)
    for d in definitions:
      argument_manager.AddDefinition(d)
    argument_manager.SetCPPStandard(standard)

    self.maybe_add_qt_include_paths(v, argument_manager)
    self.maybe_add_ros_include_paths(v, argument_manager)
    self.maybe_add_cuda_include_paths(v, argument_manager)
    return argument_manager

  def maybe_add_qt_include_paths(self, v, argument_manager):
    qt_dev = v['deoplete#sources#cpp#cpp_enable_qt_dev']
    qt_root = v['deoplete#sources#cpp#cpp_qt_root']

    if qt_dev:
      argument_manager.AddIncludePath(qt_root)
      self.log(qt_root)
      for submod in os.listdir(qt_root):
        submod_path = os.path.join(qt_root, submod)
        if os.path.isdir(submod_path):
          argument_manager.AddIncludePath(submod_path)

  def maybe_add_ros_include_paths(self, v, argument_manager):
    ros_dev = v['deoplete#sources#cpp#cpp_enable_ros_dev']
    ros_root = v['deoplete#sources#cpp#cpp_ros_root']
    ros_user_ws = os.path.expanduser(v['deoplete#sources#cpp#cpp_ros_user_ws'])

    if ros_dev:
      local_dev = os.path.join('devel', 'include')
      argument_manager.AddIncludePath(local_dev)
      argument_manager.AddIncludePath(os.path.join('..', local_dev))
      argument_manager.AddIncludePath(os.path.join('..', '..', local_dev))
      argument_manager.AddIncludePath(os.path.join(ros_root, 'include'))
      argument_manager.AddIncludePath(
        os.path.join(ros_user_ws, 'devel', 'include'))

  def maybe_add_cuda_include_paths(self, v, argument_manager):
    cuda_dev = v['deoplete#sources#cpp#cpp_enable_cuda_dev']
    cuda_root = v['deoplete#sources#cpp#cpp_cuda_root']

    if cuda_dev:
      argument_manager.AddIncludePath(cuda_root)
      argument_manager.AddIncludePath(os.path.join(cuda_root, 'include'))

  def on_event(self, context):
    self.update(context)

  def gather_candidates(self, context):
    return self.get_candidates(context)
