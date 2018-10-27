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
    self.filetypes = ['cuda']
    # The mark of a source
    self.mark = '[cuda]'
    # The unique name of a source.
    self.name = 'cuda'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

    self.max_menu_width = 160
    self.max_abbr_width = 160

    # cuda path
    self._cuda_path = self.vim.vars['deoplete#sources#cpp#cuda_path']
    self._add_cuda_includes()

  def _add_cuda_includes(self):
    for p in self._cuda_path:
      self._cppflags.append('-I%s' % (p))

  def on_init(self, context):
    # cache the file
    self.setup()
    self._update(context)

  def on_event(self, context):
    self._update(context)

  def _update_file_content(self, context):
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)

    include_pattern = re.compile(r'\s*#include\s*<cuda_runtime_api.h>')
    if not include_pattern.findall(content):
      content = '#include <cuda_runtime_api.h>\n' + content

    include_pattern = re.compile(r'\s*#include\s*<cuda.h>')
    if not include_pattern.findall(content):
      content = '#include <cuda.h>\n' + content

    self._file_contents[filepath] = content

  def gather_candidates(self, context):
    self._update(context)
    return self._get_candidates(context)
