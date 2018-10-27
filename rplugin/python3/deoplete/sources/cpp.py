# -*- coding: utf-8 -*-

import os
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
    """
    Source constructor.  It is always called in initializing.  It
    must call super() constructor.  This function takes {self} and
    {vim} as its parameters.
    """

    Base.__init__(self, vim)
    ClangCompletion.__init__(self, vim)

    # The description of a source.
    self.description = 'clang cpp completion'
    # Available filetype list.
    self.filetypes = ['c', 'cpp', 'objc', 'objcpp']
    # The mark of a source
    self.mark = '[c++]'
    # The unique name of a source.
    self.name = 'cpp'
    # Source priority.  Higher values imply higher priority.
    self.rank = 600

    self.max_menu_width = 160
    self.max_abbr_width = 160

  def on_init(self, context):
    """
    It will be called before the source attribute is called.
    It takes {self} and {context} as its parameter.
    It should be used to initialize the internal variables.

    context
      A dictionary to give context information.
      The followings are the primary information.

      bufnr			(Integer)
          The current effective buffer number in event.
          Note: It may not be same with current buffer.

      candidates		(List[dict])
          The current candidates.

      complete_position	(Integer)
          The complete position of current source.

          " Example:
          pattern : r'fruits\.'

              01234567
          input   : fruits.

          complete_position : 7

      complete_str		(String)
          The complete string of current source.

      event			(String)
          The current event name.

      filetype		(String)
          Current 'filetype'.

      filetypes		(List[str])
          It contains current 'filetype', same
          filetypes and composite filetypes.

      input			(String)
          The input string of the current line, namely the part
          before the cursor.

      is_async		(Bool)
          If the gather is asynchronous, the source must set
          it to "True". A typical strategy for an asynchronous
          gather_candidates method to use this flag is to
          set is_async flag to True while results are being
          produced in the background (optionally, returning them
          as they become ready). Once background processing
          has completed, is_async flag should be set to False
          indicating that this is the last portion of the
          candidates.
    """

    # cache the file
    self.setup()
    self._update(context)

  def on_event(self, context):
    """
    Called for |InsertEnter|, |BufWritePost|, |BufReadPost| and
    |BufDelete| autocommands, through |deoplete#send_event()|.
    """

    self._update(context)

  def gather_candidates(self, context):
    """
    It is called to gather candidates.
    It takes {self} and {context} as its parameter and returns a
    list of {candidate}.
    If the error is occurred, it must return None.
    {candidate} must be String or Dictionary contains
    |deoplete-candidate-attributes|.
    Here, {context} is the context information when the source is
    called (|deoplete-notation-{context}|).
    Note: The source must not filter the candidates by user input.
    It is |deoplete-filters| work.  If the source filter the
    candidates, user cannot filter the candidates by fuzzy match.
    """

    self._update(context)
    return self._get_candidates(context)
