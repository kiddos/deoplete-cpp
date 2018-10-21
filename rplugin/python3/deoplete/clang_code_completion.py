# -*- coding: utf-8 -*-

import subprocess
import re

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
      return True

  if len(locations) > 0:
    first = locations[0].split('=>')[-1].strip()
    Config.loaded = False
    Config.set_library_file(first)
    Config.set_compatibility_check(False)
    return True
  return False


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
      return match[0][0].strip(), match[0][1]
    elif scope_index > end_index and scope_index > op_index:
      pattern = re.compile(r'([^;\}\{]+)(::)')
      match = [i for i in reversed(re.findall(pattern, prev_content))]
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
      #  print(type.kind)
      if type.kind == TypeKind.RECORD:
        return type
      elif type.kind == TypeKind.POINTER:
        return peel(type.get_pointee())
      elif type.kind == TypeKind.CONSTANTARRAY:
        return peel(type.get_array_element_type())
      elif type.kind == TypeKind.FUNCTIONPROTO:
        return peel(type.get_result())
      elif type.kind == TypeKind.UNEXPOSED:
        return peel(type.get_canonical())
      elif type.kind == TypeKind.ELABORATED:
        return peel(type.get_canonical())

    identifiers = []

    def find(node, index):
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

    if n.kind == CursorKind.FUNCTION_DECL or \
      n.kind == CursorKind.FUNCTION_TEMPLATE:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': FUNCTION_MENU,
      }
    elif n.kind == CursorKind.CXX_METHOD:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': METHOD_MENU,
      }
    elif n.kind == CursorKind.FIELD_DECL:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': VARIABLE_MENU,
      }
    elif n.kind == CursorKind.NAMESPACE_REF or \
      n.kind == CursorKind.NAMESPACE_ALIAS or \
      n.kind == CursorKind.NAMESPACE:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': NAMESPACE_MENU,
      }
    elif n.kind == CursorKind.MACRO_DEFINITION:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': MACRO_MENU,
      }
    elif n.kind == CursorKind.CLASS_DECL or \
      n.kind == CursorKind.CLASS_TEMPLATE or \
      n.kind == CursorKind.TYPEDEF_DECL:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': CLASS_MENU,
      }
    elif n.kind == CursorKind.STRUCT_DECL:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': STRUCT_MENU,
      }
    elif n.kind == CursorKind.VAR_DECL:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': VARIABLE_MENU,
      }
    elif n.kind == CursorKind.USING_DECLARATION:
      d = n.get_definition()
      if d and d.displayname:
        return {
          'word': d.displayname,
          'kind': d.displayname,
          'menu': USING_MENU,
        }
    elif n.kind == CursorKind.CONSTRUCTOR:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': CONSTRUCTOR_MENU,
      }
    elif n.kind == CursorKind.DESTRUCTOR:
      return {
        'word': n.displayname,
        'kind': n.displayname,
        'menu': DESTRUCTOR_MENU,
      }
    return None

  def get_completion(self, cursors):
    """
    parse current cursor children into completion result
    """

    completion = []
    for cursor in cursors:
      # to be able to parse template class methods
      # require to reform cursor using this
      if cursor != self.tu.cursor:
        cursor = Cursor.from_location(self.tu, cursor.location)

      # iterate cursor
      for n in cursor.get_children():
        #  if n.displayname:
        #    print(n.displayname)
        #  if n.displayname and 'Release' in n.displayname:
        #    print(n.displayname, n.kind)
        c = self.process_completion(n)
        if c:
          completion.append(c)
    return completion

  def get_fixits(self, line, col):
    diags = []
    for diag in self.tu.diagnostics:
      diags.append(diag.fixits)
    return diags

  def test_template(self):
    for node in self.tu.cursor.get_children():
      print(node.kind, node.displayname)

  def code_complete(self, line, col):
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
