# -*- coding: utf-8 -*-

import subprocess
import re
import os
import threading

from clang.cindex import Config
from clang.cindex import TranslationUnit
from clang.cindex import Index
from clang.cindex import Cursor
from clang.cindex import CursorKind
from clang.cindex import File
from clang.cindex import SourceLocation
from clang.cindex import TypeKind


def setup_libclang(version):
  locate_command = 'ldconfig -p | grep libclang'
  locations = subprocess.check_output(locate_command, shell=True)
  locations = locations.decode('ascii').replace('\t', '').split('\n')

  for location in locations:
    loc = location.split('=>')[-1].strip()
    if loc.find(version) >= 0:
      Config.loaded = False
      Config.set_library_file(loc)
      Config.set_compatibility_check(False)
      return loc

  if len(locations) > 0:
    first = locations[0].split('=>')[-1].strip()
    Config.loaded = False
    Config.set_library_file(first)
    Config.set_compatibility_check(False)
    return first
  return None


def create_index():
  return Index.create()


FUNCTION_MENU = 'function'
METHOD_MENU = 'method'
VARIABLE_MENU = 'variable'
NAMESPACE_MENU = 'namespace'
MACRO_MENU = 'macro'
CLASS_MENU = 'class'
STRUCT_MENU = 'struct'
USING_MENU = 'using'
CONSTRUCTOR_MENU = 'constructor'
DESTRUCTOR_MENU = 'destructor'
UNKNOWN_MENU = 'unknown'


class Source(object):
  """
  source code completion for a file
  """

  def __init__(self, index, filepath, args, unsaved_files):
    """
    setup translation unit with filepath, args, and unsaved_files
    Noted that unsaved_files may change, so caching it is unnecessary
    """

    self.index = index

    self.filepath = filepath
    self.args = args
    self.options = \
      TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD | \
      TranslationUnit.PARSE_INCOMPLETE | \
      TranslationUnit.PARSE_PRECOMPILED_PREAMBLE
    self.tu = self.index.parse(
      self.filepath,
      args=self.args,
      unsaved_files=unsaved_files,
      options=self.options)
    self.get_content(unsaved_files)

    self.complete_full = False

  def reparse(self, unsaved_files):
    """
    reparse the translation unit
    """

    self.tu.reparse(unsaved_files=unsaved_files,
      options=self.options)
    self.get_content(unsaved_files)

  def get_content(self, unsaved_files):
    """
    get the current filepath content
    """
    for filepath, content in unsaved_files:
      if filepath == self.filepath:
        self.content = content
        break

  def get_index(self, line, col):
    """
    convert (line, col) to index of content
    if the computed index exceed the content size,
      return the max index of content
    """
    lines = self.content.split('\n')
    if line > len(lines):
      return len(self.content)
    return min(len('\n'.join(lines[:line - 1])) + col, len(self.content))

  def find_closest_token(self, line, col):
    """
    find the closest token
    if semicolon is found first,
      then return None
    if dot, pointer operator is found first,
      then return the previous token and that operator
    if scope operator is found first
      then return the full token with full namespace and the scope operator
    """

    prev_content = self.content[:self.get_index(line, col)]

    semicolon_index = prev_content.rfind(';')
    double_quote_index = prev_content.rfind('"')
    dot_index = prev_content.rfind('.')
    pointer_index = prev_content.rfind('->')
    scope_index = prev_content.rfind('::')

    end_index = max(semicolon_index, double_quote_index)
    op_index = max(dot_index, pointer_index)
    if op_index > end_index and op_index > scope_index:
      pattern = re.compile(r'([^;\}\{]+)(\.|->)')
      match = [i for i in reversed(re.findall(pattern, prev_content))]
      if '#' in match[0][0]:
        return None, None
      return match[0][0].strip(), match[0][1]
    elif scope_index > end_index and scope_index > op_index:
      pattern = re.compile(r'([^;\}\{]+)(::)')
      match = [i for i in reversed(re.findall(pattern, prev_content))]
      if '#' in match[0][0]:
        return None, None
      return match[0][0].strip(), match[0][1]
    return None, None

  def find_closest_parent(self, line, col):
    """
    find the closest parent cursor given current line and column
    """

    min_dist = None
    closest = None

    def find(node):
      nonlocal min_dist
      nonlocal closest
      if node.displayname and node.location and node.location.file and \
        node.location.file.name == self.filepath:
        location = node.location
        dist = abs(location.line - line) + abs(location.column - col)
        closest = Cursor.from_location(self.tu, location)
        if (not min_dist or dist < min_dist) and closest.semantic_parent:
          min_dist = dist
          closest = Cursor.from_location(self.tu, location)

      for n in node.get_children():
        # limit the searching scope to this file
        if n.location and n.location.file and \
          n.location.file.name == self.filepath:
          find(n)

    find(self.tu.cursor)

    if closest:
      if closest.kind == CursorKind.TYPE_REF:
        return closest.get_definition()
      return closest.semantic_parent
    return None

  def find_identifier_type(self, cursor, name):
    """
    find variable type given cursor scope
    """

    # remove array index
    if '[' in name:
      name = name[:name.find('[')]

    pattern = re.compile(r'->|\.')
    names = re.split(pattern, name)
    #  print(names)

    def peel(type):
      if type.kind == TypeKind.POINTER:
        return peel(type.get_pointee())
      elif type.kind == TypeKind.CONSTANTARRAY:
        return peel(type.get_array_element_type())
      elif type.kind == TypeKind.FUNCTIONPROTO:
        return peel(type.get_result())
      elif type.kind == TypeKind.UNEXPOSED:
        return peel(type.get_canonical())
      elif type.kind == TypeKind.ELABORATED:
        return peel(type.get_canonical())
      return type

    identifiers = []

    def find(node, index):
      if not node:
        return

      try:
        if node.kind == CursorKind.VAR_DECL:
          #  print(node.kind, node.displayname, node.location, names[index])
          if node.displayname == names[index]:
            t = peel(node.type)
            if index == len(names) - 1:
              identifiers.append(t.get_declaration())
            else:
              find(t.get_declaration(), index + 1)
        elif node.kind == CursorKind.CXX_METHOD:
          if names[index].startswith(node.spelling):
            t = peel(node.type)
            if index == len(names) - 1:
              identifiers.append(t.get_declaration())
            else:
              find(t.get_declaration(), index + 1)
        elif node.kind == CursorKind.FIELD_DECL:
          if node.displayname == names[index]:
            t = peel(node.type)
            if index == len(names) - 1:
              d = t.get_declaration()
              identifiers.append(d)
            else:
              find(t.get_declaration(), index + 1)
      except ValueError:
        pass

      for n in node.get_children():
        find(n, index)

    find(cursor, 0)
    return identifiers

  def find_namespace(self, name):
    """
    find namespace cursors given name
    """

    names = name.split('::')
    cursors = []

    def find(node, index):
      try:
        #  print(node.kind, node.displayname, node.location, names[index])
        if node.kind == CursorKind.NAMESPACE:
          if node.displayname and node.displayname == names[index]:
            if index == len(names) - 1:
              cursors.append(node)
            else:
              find(node, index + 1)
        elif node.kind == CursorKind.NAMESPACE_REF:
          if node.displayname and node.displayname == names[index]:
            if index == len(names) - 1:
              cursors.append(node)
            else:
              find(node, index + 1)
        elif node.kind == CursorKind.CLASS_DECL:
          if node.displayname and node.displayname == names[index]:
            if index == len(names) - 1:
              cursors.append(node)
            else:
              find(node, index + 1)
      except ValueError:
        pass

      for n in node.get_children():
        find(n, index)
    find(self.tu.cursor, 0)
    return cursors

  def process_completion(self, n):
    """
    process completion result
    """

    if n.displayname:
      word = n.spelling
      if self.complete_full or not n.spelling:
        word = n.displayname

      kind = n.displayname
      menu = self.get_menu_kind(n.kind)

      return {
        'word': word,
        'kind': kind,
        'menu': menu,
      }
    return None

  def get_completion(self, cursors):
    """
    parse current cursor children into completion result
    """

    completion = []

    def find(cursor):
      for n in cursor.get_children():
        #  if n.displayname:
        #    print(n.displayname, n.kind)
        #  if n.displayname and 'Release' in n.displayname:
        #    print(n.displayname, n.kind)
        c = self.process_completion(n)
        if c:
          completion.append(c)
        if n.kind == CursorKind.UNEXPOSED_DECL:
          find(n)

    for cursor in cursors:
      # to be able to parse template class methods
      # require to reform cursor using this
      if cursor != self.tu.cursor:
        cursor = Cursor.from_location(self.tu, cursor.location)
      find(cursor)

    return completion

  def get_fixits(self, line, col):
    diags = []
    for diag in self.tu.diagnostics:
      diags.append(diag.fixits)
    return diags

  def test_template(self):
    for node in self.tu.cursor.get_children():
      print(node.kind, node.displayname)

  def code_complete_semantic(self, line, col):
    """
    get code completion result at this line and column
    """

    #  self.test_template()

    token, op = self.find_closest_token(line, col)
    #  print(token, op)
    if token:
      if op == '::':
        # find target namespace members
        cursors = self.find_namespace(token)
      else:
        # find target variable type and list its members
        parent = self.find_closest_parent(line, col)
        cursors = self.find_identifier_type(parent, token)
        #  print(cursor.displayname)
    else:
      # return global visiable functions and namespaces
      cursors = [self.tu.cursor]
    return self.get_completion(cursors)

  def process_clang_result(self, result):
    result_obj = {}
    try:
      s = str(result)
      #  print(s)
      attr_pattern = re.compile(r'\{\'([^\']+?)\', (\w+?)\}')
      attrs = re.findall(attr_pattern, s)
      #  print(attrs)
      for i in range(len(attrs)):
        done = False
        attr = attrs[i]
        key = attr[1].strip()
        value = attr[0].strip()
        if key == 'LeftParen':
          full = result_obj['TypedText']
          for j in range(i, len(attrs)):
            attr = attrs[j]
            key = attr[1].strip()
            value = attr[0].strip()
            full += value
            if key == 'RightParen':
              result_obj['CompleteText'] = full
              done = True
              break
        else:
          result_obj[key] = value
        if done:
          break

      prop_pattern = re.compile(r'([^\|]+?): ([^\|]+)')
      props = re.findall(prop_pattern, s)
      for p in props:
        result_obj[p[0].strip()] = p[1].strip()
      #  print(props)

      return result_obj, result.kind
    except Exception:
      pass
    return None, None

  def get_menu_kind(self, cursor_kind):
    if cursor_kind == CursorKind.FUNCTION_DECL or \
      cursor_kind == CursorKind.FUNCTION_TEMPLATE:
      return FUNCTION_MENU
    elif cursor_kind == CursorKind.CXX_METHOD:
      return METHOD_MENU
    elif cursor_kind == CursorKind.FIELD_DECL or \
      cursor_kind == CursorKind.VAR_DECL:
      return VARIABLE_MENU
    elif cursor_kind == CursorKind.NAMESPACE_REF or \
      cursor_kind == CursorKind.NAMESPACE_ALIAS or \
      cursor_kind == CursorKind.NAMESPACE:
      return NAMESPACE_MENU,
    elif cursor_kind == CursorKind.MACRO_DEFINITION:
      return MACRO_MENU
    elif cursor_kind == CursorKind.CLASS_DECL or \
      cursor_kind == CursorKind.TYPEDEF_DECL or \
      cursor_kind == CursorKind.CLASS_TEMPLATE:
      return CLASS_MENU
    elif cursor_kind == CursorKind.STRUCT_DECL:
      return STRUCT_MENU
    elif cursor_kind == CursorKind.USING_DECLARATION:
      return USING_MENU
    elif cursor_kind == CursorKind.CONSTRUCTOR:
      return CONSTRUCTOR_MENU
    elif cursor_kind == CursorKind.DESTRUCTOR:
      return DESTRUCTOR_MENU
    return UNKNOWN_MENU

  def process_clang_results(self, results, full_completion=False):
    processed = []
    for result in results:
      r, kind = self.process_clang_result(result)
      if r:
        word = r['TypedText']
        if full_completion and 'CompleteText' in r:
          word = r['CompleteText']

        kind = 'None'
        if 'ResultType' in r:
          kind = r['ResultType']

        menu = self.get_menu_kind(kind)

        info = r['Brief comment']
        if info == 'None' and 'CompleteText' in r:
          info = r['CompleteText']

        abbr = r['TypedText']

        processed.append({
          'word': word,
          'kind': kind,
          'menu': menu,
          'info': info,
          'abbr': abbr,
        })
    return processed

  def code_complete(self, line, col, unsaved_files,
      include_macros=True, include_code_patterns=True,
      include_brief_comments=True):
    cc_results = self.tu.codeComplete(
      self.filepath,
      line,
      col,
      unsaved_files=unsaved_files,
      include_macros=include_macros,
      include_code_patterns=include_code_patterns,
      include_brief_comments=include_brief_comments)
    if cc_results:
      return self.process_clang_results(cc_results.results)
    return []


def get_translation_unit(filepath, flags, all_files):
  try:
    from clang.cindex import TranslationUnit as tu

    options = \
      tu.PARSE_DETAILED_PROCESSING_RECORD | \
      tu.PARSE_INCOMPLETE | \
      tu.PARSE_PRECOMPILED_PREAMBLE | \
      tu.PARSE_SKIP_FUNCTION_BODIES

    return tu.from_source(filepath, flags, unsaved_files=all_files,
      options=options)
  except Exception:
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
    except Exception:
      continue
  return parsed_result


class ClangCompletion(object):
  def __init__(self, vim):
    self.vim = vim
    self._init_vars()

    #  self._translation_unit_cache = {}
    #  self._result_cache = {}
    self._file_contents = {}
    self._file_sources = {}

  def setup(self):
    # setup libclang
    clang_version = self.vim.vars['deoplete#sources#cpp#clang_version']
    libfile = setup_libclang(clang_version)
    self.log('setup libclang: %s' % (libfile))

    # create index
    self._index = create_index()

  def log(self, msg):
    """
    log message to vim console
    """

    #  if self.is_debug_enabled:
    #    self.vim.command('echom "%s"' % (msg))

    self.vim.command('echom "%s"' % (msg))

  def _init_vars(self):
    """
    get variables settings from vim
    """

    v = self.vim.vars
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

    self._full_completion = v['deoplete#sources#cpp#full_completion']

    #  self._gathering = False

  def get_buffer_name(self, context):
    """
    retrieve buffer name from current content
    """

    return self.vim.eval('expand("%:p")')

  def _update_file_content(self, context):
    """
    store file contents
    """

    filepath = self.get_buffer_name(context)
    content = '\n'.join(self.vim.current.buffer)
    self._file_contents[filepath] = content

  def _get_source_args(self, context):
    """
    get source arguments with include flags and compile flags
    """

    include_flags = ['-I%s' % (p)
      for p in self._cpp_include_path if os.path.isdir(p)]
    flags = []
    if context['filetype'] == 'c':
      flags = ['-x', 'c'] + self._cflags
      include_flags = ['-I%s' % (p)
        for p in self._c_include_path if os.path.isdir(p)]
    elif context['filetype'] == 'cpp':
      flags = ['-x', 'c++'] + self._cppflags
    elif context['filetype'] == 'objc':
      self.log('objc flags')
      flags = ['-ObjC'] + self._objcflags
      include_flags = ['-I%s' % (p)
        for p in self._objc_include_path if os.path.isdir(p)]
    elif context['filetype'] == 'objcpp':
      self.log('objcpp flags')
      flags = ['-ObjC++'] + self._objcppflags
      include_flags = ['-I%s' % (p)
        for p in self._objcpp_include_path if os.path.isdir(p)]
    else:
      # default to cpp flag if filetype not known
      flags = ['-x', 'c++'] + self._cppflags

    flags += include_flags
    flags += ['-fsyntax-only']
    return flags

  def _update_file_source(self, context):
    """
    update file source object
    """

    filepath = self.get_buffer_name(context)
    unsaved_files = [(filepath, content)
      for filepath, content in self._file_contents.items()]
    if filepath in self._file_sources:
      self._file_sources[filepath].reparse(unsaved_files)
    else:
      args = self._get_source_args(context)
      source = Source(self._index, filepath, args, unsaved_files)
      self._file_sources[filepath] = source

  def _update(self, context):
    """
    update both file content and source object
    """

    self._update_file_content(context)
    self._update_file_source(context)

  def _get_cursor_pos(self):
    """
    get current cursor position
    """

    line = self.vim.eval('line(".")')
    col = self.vim.eval('col(".")')
    return line, col

  def _get_candidates(self, context):
    """
    retrive candidate from source object
    """

    filepath = self.get_buffer_name(context)
    if filepath in self._file_sources:
      self._file_sources[filepath].complete_full = self._full_completion

      line, col = self._get_cursor_pos()
      # original completion way
      unsaved_files = [(filepath, content)
        for filepath, content in self._file_contents.items()]
      results = self._file_sources[filepath].code_complete(line, col,
        unsaved_files)
      #  results = self._file_sources[filepath].code_complete_semantic(line, col)
      self.log('%s completion: (%s, %s) | %s' % (filepath, line, col, len(results)))
      return results
    return []

  def _get_current_cache_key(self, context, position):
    fileid = os.path.join(context['cwd'], self.get_buffer_name(context))
    return '%s:(%d,%d)' % (fileid, position[0], position[1])

  def _get_default_cache_key(self, context):
    fileid = os.path.join(context['cwd'], self.get_buffer_name(context))
    return '%s:default' % (fileid)

  def _async_complete(self, task):
    thread = threading.Thread(target=task)
    thread.start()

  def _setup_completion_cache(self, context):
    if not self._result_cache:
      # parse if not yet been parse
      position = [1, 1]
      cache_key = self._get_current_cache_key(context, position)
      self._gather_and_cache_completion(context, position, cache_key)
      # remove old result
      #  filepath = self.get_buffer_name(context)
      #  keys_to_remove = []
      #  for key in self._result_cache:
      #    if key.startswith(filepath):
      #      keys_to_remove.append(key)
      #  for key in keys_to_remove:
      #    self._result_cache.pop(key, None)

  def _get_closest_delimiter(self, context):
    try:
      current_line = self.vim.current.buffer[context['position'][1]-1]
      delimiter_pos = []
      for d in self._delimiter:
        found = current_line.rfind(d)
        if found >= 0:
          delimiter_pos.append(found + len(d))
        else:
          delimiter_pos.append(found)
      return max(delimiter_pos + [0])
    except Exception as e:
      self.log('error: %s' % (str(e)))
      return 0

  def _get_completion_position(self, context):
    return (context['position'][1],
      self._get_closest_delimiter(context)+1)

  def _get_completion_result(self, context, filepath, position):
    if not self._libclang_found:
      return ''

    all_files = [(f, self._file_cache[f]) for f in self._file_cache]

    if filepath not in self._translation_unit_cache:
      # cache translation unit
      flags = self._get_completion_flags(context)
      tunit = get_translation_unit(filepath, flags, all_files)
      result = tunit.codeComplete(filepath,
        position[0], position[1], unsaved_files=all_files,
        include_macros=True)
      self._translation_unit_cache[filepath] = tunit
    else:
      # use the cached translation unit
      tunit = self._translation_unit_cache[filepath]

      try:
        from clang.cindex import TranslationUnit as tu

        options = \
          tu.PARSE_DETAILED_PROCESSING_RECORD | \
          tu.PARSE_INCOMPLETE | \
          tu.PARSE_PRECOMPILED_PREAMBLE | \
          tu.PARSE_CACHE_COMPLETION_RESULTS | \
          tu.PARSE_SKIP_FUNCTION_BODIES
        tunit.reparse(unsaved_files=all_files, options=options)
      except Exception:
        pass

      result = tunit.codeComplete(filepath,
        position[0], position[1], unsaved_files=all_files,
        include_macros=True)
    return result

  def _gather_and_cache_completion(self, context, position, key):
    try:
      buffer_name = self.get_buffer_name(context)
      raw_result = \
          self._get_completion_result(context, buffer_name, position)
      parsed_result = parse_raw_result(raw_result)
      self._cache_result(parsed_result, key)
    except Exception:
      pass

  def _async_gather_completion(self, context, position, key):
    def gather():
      self._gather_and_cache_completion(context, position, key)
      self._gathering = False

    if not self._gathering:
      self._gathering = True
      task = threading.Thread(target=gather)
      task.start()
