from .base import Base
import os
import re
from clang.cindex import TranslationUnit as tu


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.vim = vim
        self.name = 'cpp-complete'
        self.mark = '[clang]'
        self.rank = 600
        self.debug_enabled = True
        self.filetypes = ['c', 'cpp', 'objc', 'objc++', 'arduino']
        self.input_pattern = (
            r'[^.\s\t\d\n]\.\w*|'
            r'[^.\s\t\d\n]->\w*|'
            r'[\w\d]::\w*')
        self.max_menu_width = 160
        self.max_abbr_width = 160

        # include flags
        self._clang_flags = \
            self.vim.vars['deoplete#sources#cpp#flags']
        self._clang_include_path = \
            self.vim.vars['deoplete#sources#cpp#include_path']

        # cache
        self._file_cache = {}
        self._translation_unit_cache = {}
        self._result_cache = {}

    def _get_buffer_name(self, context):
        buffer_name = context['bufname'].replace('.ino', '.cpp')
        return os.path.join(context['cwd'], buffer_name)

    def _update_file_cache(self, context):
        filepath = self._get_buffer_name(context)
        content = '\n'.join(self.vim.current.buffer)
        self._file_cache[filepath] = content

    def on_event(self, context):
        # change input pattern
        if context['filetype'] == 'c':
            self.input_pattern = (
                r'[^.\s\t\d\n]\.\w*|'
                r'[^.\s\t\d\n]->\w*')
        else:
            self.input_pattern = (
                r'[^.\s\t\d\n]\.\w*|'
                r'[^.\s\t\d\n]->\w*|'
                r'\w[\w\d]*::\w*')

        # cache the file
        self._update_file_cache(context)

    def _get_closest_delimiter(self, context):
        delimiter = ['.', '->', '::']
        current_line = self.vim.current.buffer[context['position'][1]-1]
        return max([current_line.rfind(d) + len(d) for d in delimiter])

    def _get_completion_position(self, context):
        return (context['position'][1], self._get_closest_delimiter(context)+1)

    def _get_completion_result(self, filepath, position):
        all_files = [(f, self._file_cache[f]) for f in self._file_cache]
        # cache translation unit
        if filepath not in self._translation_unit_cache:
            tunit = tu.from_source(filepath,
                                   self._clang_flags + self._clang_include_path,
                                   unsaved_files=all_files,
                                   options=tu.PARSE_CACHE_COMPLETION_RESULTS |
                                           tu.PARSE_DETAILED_PROCESSING_RECORD |
                                           tu.PARSE_PRECOMPILED_PREAMBLE |
                                           tu.PARSE_INCOMPLETE)
            result = tunit.codeComplete(filepath,
                                        position[0],
                                        position[1],
                                        unsaved_files=all_files)
            self._translation_unit_cache[filepath] = tunit
            return result
        else:
            result = self._translation_unit_cache[filepath].\
                codeComplete(filepath,
                             position[0],
                             position[1],
                             unsaved_files=all_files)
            return result

    def _parse_completion_result(self, result, key):
        pattern = re.compile(key + r':\s(.*?)(\s\||$)')
        match = pattern.findall(result)
        if match:
            return match[0][0]

        pattern = re.compile(r'\'([^.^\']*?)\',\s' + key)
        match = pattern.findall(result)
        if match:
            return match[0]
        else:
            return ''

    def _get_parsed_completion_result(self, completion_result):
        parsed_result = []
        for result in completion_result.results:
            try:
                r = str(result)
                parsed_result.append({
                    'TypedText':
                        self._parse_completion_result(r, 'TypedText'),
                    'ResultType':
                        self._parse_completion_result(r, 'ResultType'),
                    'Availability':
                        self._parse_completion_result(r, 'Availability'),
                    'Priority':
                        int(self._parse_completion_result(r, 'Priority')),
                    'Brief comment':
                        self._parse_completion_result(r, 'Brief comment'),
                    'LeftParen':
                        self._parse_completion_result(r, 'LeftParen'),
                    'RightParen':
                        self._parse_completion_result(r, 'RightParen'),
                    'Placeholder':
                        self._parse_completion_result(r, 'Placeholder'),
                    'Informative':
                        self._parse_completion_result(r, 'Informative'),
                })
            except:
                continue
        return parsed_result

    def _get_current_cache_key(self, position):
        line = self.vim.current.buffer[position[0]-1]
        column = position[1]
        delimiter = ['->', '.', '::']
        first = max([line.rfind(d, 0, column-1) for d in delimiter])
        if first < 0:
            return 'empty-function'
        second = max([line.rfind(d, 0, first-1) for d in delimiter])
        if second < 0:
            return line[0:first].strip()
        else:
            return line[second+1:first].strip()

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        self._update_file_cache(context)

        cache_key = self._get_current_cache_key(context['position'][1:])

        if cache_key not in self._result_cache:
            buffer_name = self._get_buffer_name(context)
            position = self._get_completion_position(context)
            completion_result = self._get_completion_result(buffer_name, position)
            parsed_result = self._get_parsed_completion_result(completion_result)

            self._result_cache[cache_key] = parsed_result
            return [{'word': r['TypedText'],
                     'kind': r['Placeholder'],
                     'menu': r['ResultType']}
                     for r in parsed_result]
        else:
            parsed_result = self._result_cache[cache_key]
            return [{'word': r['TypedText'],
                     'kind': r['Placeholder'],
                     'menu': r['ResultType']}
                     for r in parsed_result]
