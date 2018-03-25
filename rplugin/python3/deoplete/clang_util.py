# -*- coding: utf-8 -*-

from __future__ import absolute_import
from past import autotranslate

import re
import sys
import subprocess
import os

autotranslate(['clang'])


def setup_libclang(version):
  try:
    from clang.cindex import Config as conf
  except:
    return False

  locate_command = 'ldconfig -p | grep libclang'
  locations = subprocess.check_output(locate_command, shell=True)
  locations = locations.decode('ascii').replace('\t', '').split('\n')

  for location in locations:
    loc = location.split('=>')[-1].strip()
    if loc.find(version) >= 0:
      conf.loaded = False
      conf.set_library_file(loc)
      conf.set_compatibility_check(False)
      return True

  if len(locations) > 0:
    first = locations[0].split('=>')[-1].strip()
    conf.loaded = False
    conf.set_library_file(first)
    conf.set_compatibility_check(False)
    return True
  return False


def get_translation_unit(filepath, flags, all_files):
  try:
    from clang.cindex import TranslationUnit as tu

    options = tu.PARSE_CACHE_COMPLETION_RESULTS | \
      tu.PARSE_PRECOMPILED_PREAMBLE | tu.PARSE_INCOMPLETE | \
      tu.PARSE_DETAILED_PROCESSING_RECORD

    return tu.from_source(filepath, flags, unsaved_files=all_files,
      options=options)
  except:
    return None


def get_value(result, key):
  pattern = re.compile(key + r':\s(.*?)(\s\||$)')
  match = pattern.findall(result)
  if match:
    return match[0][0]

  pattern = re.compile(r'\'([^\']*?)\',\s' + key)
  match = pattern.findall(result)
  if match:
    return ','.join(match)
  else:
    return ''


def parse_raw_result(raw_result):
  parsed_result = []
  for result in raw_result.results:
    try:
      r = str(result)
      parsed_result.append({
        'ResultType': get_value(r, 'ResultType'),
        'TypedText': get_value(r, 'TypedText'),
        'LeftAngle': get_value(r, 'LeftAngle'),
        'RightAngle': get_value(r, 'RightAngle'),
        'LeftParen': get_value(r, 'LeftParen'),
        'RightParen': get_value(r, 'RightParen'),
        'Availability': get_value(r, 'Availability'),
        'Priority': int(get_value(r, 'Priority')),
        'Brief comment': get_value(r, 'Brief comment'),
        'Placeholder': get_value(r, 'Placeholder'),
        'Informative': get_value(r, 'Informative'),
      })
    except:
      continue
  return parsed_result


class ClangCompletion(object):
  def __init__(self, vim, version):
    self._libclang_found = setup_libclang(version)

    self.vim = vim
    # cache
    self._file_cache = {}
    self._translation_unit_cache = {}
    self._result_cache = {}

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

  def get_buffer_name(self, context):
    buffer_name = context['bufname']
    return os.path.join(context['cwd'], buffer_name)

  def _update_file_cache(self, context):
    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)
    self._file_cache[filepath] = content

  def _setup_completion_cache(self, context):
    if not self._result_cache:
      # parse if not yet been parse
      position = [1, 1]
      cache_key = self._get_current_cache_key(context, position)
      self._gather_and_cache_completion(context, position, cache_key)
    else:
      # remove old result
      filepath = self.get_buffer_name(context)
      keys_to_remove = []
      for key in self._result_cache:
        if key.startswith(filepath):
          keys_to_remove.append(key)
      for key in keys_to_remove:
        self._result_cache.pop(key, None)

  def _get_closest_delimiter(self, context):
    current_line = self.vim.current.buffer[context['position'][1]-1]
    return max([current_line.rfind(d) + len(d) for d in self._delimiter])

  def _get_completion_position(self, context):
    return (context['position'][1], self._get_closest_delimiter(context)+1)

  def _process_include_flag(self, include_paths):
    include_flags = []
    for p in include_paths:
      if os.path.isdir(p):
        include_flags.append('-I%s' % (p))
    return include_flags

  def _get_completion_flags(self, context):
    include_flags = self._process_include_flag(self._cpp_include_path)
    flags = []
    if context['filetype'] == 'c':
      flags = ['-x', 'c'] + self._cflags
      include_flags = self._process_include_flag(self._c_include_path)
    elif context['filetype'] == 'cpp':
      flags = ['-x', 'c++'] + self._cppflags
    elif context['filetype'] == 'objc':
      flags = ['-ObjC'] + self._objcflags
      include_flags = self._process_include_flag(self._objc_include_path)
    elif context['filetype'] == 'objcpp':
      flags = ['-ObjC++'] + self._objcppflags
      include_flags = self._process_include_flag(self._objcpp_include_path)
    else:
      # default to cpp flag if filetype not known
      flags = ['-x', 'c++'] + self._cppflags

    flags += include_flags
    return flags


  def _get_completion_result(self, context, filepath, position):
    if not self._libclang_found:
      return ''

    all_files = [(f, self._file_cache[f]) for f in self._file_cache]

    if filepath not in self._translation_unit_cache:
      # cache translation unit
      flags = self._get_completion_flags(context)
      tunit = get_translation_unit(filepath, flags, all_files)
      result = tunit.codeComplete(filepath,
        position[0], position[1], unsaved_files=all_files)
      self._translation_unit_cache[filepath] = tunit
    else:
      # use the cached translation unit
      tunit = self._translation_unit_cache[filepath]
      result = tunit.codeComplete(filepath,
        position[0], position[1], unsaved_files=all_files)
    return result

  def _get_current_cache_key(self, context, position):
    fileid = os.path.join(context['cwd'], self.get_buffer_name(context))
    return fileid + ':(%d,%d)' % (position[0], position[1])

  def _gather_and_cache_completion(self, context, position, key):
    try:
      buffer_name = self.get_buffer_name(context)
      raw_result = \
          self._get_completion_result(context, buffer_name, position)
      parsed_result = parse_raw_result(raw_result)
      self._result_cache[key] = parsed_result
      return parsed_result
    except:
      return []

  def _cache_delimiter_completion(self, context):
    if not hasattr(self, '_delimiter'): return

    for r, lines in enumerate(self.vim.current.buffer):
      for d in self._delimiter:
        c = lines.find(d)
        if c >= 0:
          position = [r + 1, c + 1]
          cache_key = self._get_current_cache_key(context, position)
          self._gather_and_cache_completion(
            context, position, cache_key)

  def _get_candidates(self, parsed_result, include_paren=False):
    candidates = []
    for pr in parsed_result:
      if include_paren:
        word = pr['TypedText'] + pr['LeftAngle'] + pr['RightAngle'] + \
            pr['LeftParen'] + pr['RightParen']
        candidate = {
          'word': word,
          'kind': pr['Placeholder'],
          'menu': pr['ResultType']
        }
      else:
        candidate = {
          'word': pr['TypedText'],
          'kind': pr['Placeholder'],
          'menu': pr['ResultType']
        }
      candidates.append(candidate)
    return candidates
