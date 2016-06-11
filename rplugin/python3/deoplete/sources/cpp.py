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
        self._cache = ['test']

        #  f = open('/home/joseph/test.log', 'w')
        #  f.write(str(self._clang_flags) + '\n')
        #  f.write(str(self._clang_include_path) + '\n')
        #  f.close()


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
                r'[\w\d]::\w*')



        #  f = open('/home/joseph/test.log', 'w')
        #  for c in context:
        #      f.write(str(c) + ': ' + str(context[c]) + '\n')

        #  current_line = self.vim.current.buffer[context['position'][1]]
        #  f = open('/home/joseph/test.log', 'w')
        #  f.write(str('\n'.join(self.vim.current.buffer)) +'\n')
        #  f.write(current_line +'\n')
        #  f.write(str(self._get_complete_position(context)) + '\n')
        #  f.close()

    def _get_closest_delimiter(self, context):
        delimiter = ['.', '->', '::']
        current_line = self.vim.current.buffer[context['position'][1]-1]
        return max([current_line.rfind(d) for d in delimiter]) + 1

    def _get_completion_position(self, context):
        return (context['position'][1], self._get_closest_delimiter(context)+1)

    def _get_completion_result(self, current_buffer, current_position):
        files = [current_buffer]
        translation_unit = tu.from_source(current_buffer[0],
                                          self._clang_flags +
                                          self._clang_include_path,
                                          unsaved_files=files)
        return translation_unit.codeComplete(current_buffer[0],
                                             current_position[0],
                                             current_position[1],
                                             unsaved_files=files)

    def _parse_completion_result(self, result, key):
        pattern = re.compile(key + r':\s(.*?)(\s\||$)')
        match = pattern.findall(result)
        if match:
            return match[0][0]

        #  pattern = re.compile(r'\'([^.\w\d\s\t]+)\',\s' + key)
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

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        current_buffer = '\n'.join(self.vim.current.buffer)
        buffer_name = context['bufname'].replace('.ino', '.cpp')
        completion_result = self._get_completion_result(
            (os.path.join(context['cwd'], buffer_name),
            current_buffer),
            self._get_completion_position(context))

        parsed_result = self._get_parsed_completion_result(completion_result)

        #  f = open('/home/joseph/test.log', 'w')
        #  f.write(str('\n'.join(self.vim.current.buffer)) +'\n')
        #  current_line = current_buffer.split('\n')[context['position'][1]-1]
        #  f.write(current_line +'\n')
        #  f.write(str(self._get_completion_position(context)) + '\n')

        #  for result in parsed_result:
        #      f.write(str(result) + '\n')
        #  f.close()

        return [{'word': r['TypedText'],
                 'kind': r['Placeholder'],
                 'menu': r['ResultType']}
                for r in parsed_result]
