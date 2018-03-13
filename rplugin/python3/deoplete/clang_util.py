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


def get_buffer_name(context):
  buffer_name = context['bufname']
  return os.path.join(context['cwd'], buffer_name)


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

  def _update_file_cache(self, context):
    filepath = get_buffer_name(context)
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
      filepath = get_buffer_name(context)
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

  def _get_completion_flags(self, context):
    flags = []
    if context['filetype'] == 'c':
      flags = ['-x', 'c'] + self._cflags
    elif context['filetype'] == 'cpp':
      flags = ['-x', 'c++'] + self._cppflags
    elif context['filetype'] == 'objc':
      flags = ['-ObjC'] + self._objcflags
    elif context['filetype'] == 'objcpp':
      flags = ['-ObjC++'] + self._objcppflags
    else:
      # default to cpp flag if filetype not known
      flags = ['-x', 'c++'] + self._cppflags

    # set up include path flags
    include_flags = self._cpp_include_path
    if context['filetype'] in ['objc', 'objcpp']:
      include_flags = self._objc_include_path

    flags += ['-I' + inc for inc in include_flags]
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
      return result
    else:
      # use the cached translation unit
      tunit = self._translation_unit_cache[filepath]
      result = tunit.codeComplete(filepath,
        position[0], position[1], unsaved_files=all_files)
      return result

  def _get_current_cache_key(self, context, position):
    line = self.vim.current.buffer[position[0]-1]
    column = position[1]
    first = max([line.rfind(d, 0, column-1) for d in self._delimiter])
    fileid = os.path.join(context['cwd'], get_buffer_name(context)) + ':'

    # if no delimiter is found try to find the function name
    if first < 0:
      # find the closest function name to current position
      function_name = re.compile(r'\s*([\w\d]*)\s*\([^\(&^\)]*\)\s*\n*{')
      content = '\n'.join(self.vim.current.buffer[0:position[0]])
      target = function_name.findall(content)
      if target:
        return fileid + target[-1]
      else:
        return fileid + 'line' + str(position[0])

    # try to find the second delimiter
    second = max([line.rfind(d, 0, first-1) for d in self._delimiter])
    if second < 0:
      return fileid + line[0:first].strip()
    else:
      return fileid + line[second+1:first].strip()

  def _gather_and_cache_completion(self, context, position, key):
    try:
      buffer_name = get_buffer_name(context)
      raw_result = \
          self._get_completion_result(context, buffer_name, position)
      parsed_result = parse_raw_result(raw_result)
      self._result_cache[key] = parsed_result
      return parsed_result
    except:
      return []

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
