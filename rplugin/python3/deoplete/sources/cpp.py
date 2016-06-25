from .base import Base
import os
import re
from clang.cindex import TranslationUnit as tu

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.vim = vim
        self.name = 'cpp'
        self.mark = '[cpp]'
        self.rank = 600
        self.debug_enabled = False
        self.filetypes = ['c', 'cpp', 'objc', 'objc++', 'cuda', 'arduino']
        self.input_pattern = (
            r'[^.\s\t\d\n_]\.\w*|'
            r'[^.\s\t\d\n_]->\w*|'
            r'[\w\d]::\w*')
        self.max_menu_width = 160
        self.max_abbr_width = 160

        self._get_detail = \
            self.vim.vars['deoplete#sources#cpp#get_detail']
        # include flags
        self._clang_cflags = \
            self.vim.vars['deoplete#sources#cpp#cflags']
        self._clang_cppflags = \
            self.vim.vars['deoplete#sources#cpp#cppflags']
        self._clang_objcflags = \
            self.vim.vars['deoplete#sources#cpp#objcflags']
        self._clang_objcppflags = \
            self.vim.vars['deoplete#sources#cpp#objcppflags']
        # include path
        self._cpp_include_path = \
            self.vim.vars['deoplete#sources#cpp#cpp_include_path']
        self._objc_include_path = \
            self.vim.vars['deoplete#sources#cpp#objc_include_path']
        # arduino path
        self._arduino_path = \
            self.vim.vars['deoplete#sources#cpp#arduino_path']
        self._setup_arduino_path()
        # cuda path
        self._cuda_path = \
            self.vim.vars['deoplete#sources#cpp#cuda_path']

        # cache
        self._file_cache = {}
        self._translation_unit_cache = {}
        self._position_cache = {}
        self._result_cache = {}


    def _setup_arduino_path(self):
        arduino_core = os.path.join(self._arduino_path,
                                    'hardware/arduino/cores/arduino')
        arduino_library = os.path.join(self._arduino_path, 'libraries')
        self._arduino_include_path = [arduino_core] + \
            [os.path.join(arduino_library, l)
             for l in os.listdir(arduino_library)]


    def _get_buffer_name(self, context):
        if context['bufname'].endswith('.ino'):
            buffer_name = context['bufname'].replace('.ino', '.cpp')
        if context['bufname'].endswith('.cu'):
            buffer_name = context['bufname'].replace('.cu', '.cpp')
        return os.path.join(context['cwd'], buffer_name)


    def _update_file_cache(self, context):
        filepath = self._get_buffer_name(context)
        content = '\n'.join(self.vim.current.buffer)

        # add default library for arduino
        if context['bufname'].endswith('.ino'):
            arduino = re.compile(r'\s*#include\s<Arduino.h>')
            if not arduino.findall(content):
                content = '#include <Arduino.h>\n' + content
        elif context['bufname'].endswith('.cu'):
            arduino = re.compile(r'\s*#include\s<cuda_runtime_api.h>')
            if not arduino.findall(content):
                content = '#include <cuda_runtime_api.h>\n' + content
                content = '#include <cuda.h>\n' + content

        self._file_cache[filepath] = content


    def on_event(self, context):
        # change input pattern
        if context['filetype'] == 'c':
            self.input_pattern = (
                r'[^.\s\t\d\n_]\.\w*|'
                r'[^.\s\t\d\n_]->\w*')
        else:
            self.input_pattern = (
                r'[^.\s\t\d\n_]\.\w*|'
                r'[^.\s\t\d\n_]->\w*|'
                r'[\w\d]::\w*')

        # cache the file
        self._update_file_cache(context)

        # setup completion cache
        if not self._result_cache:
            # parse if not yet been parse
            position = [1, 1]
            cache_key = self._get_current_cache_key(context, position)
            self._gather_completion(context, position, cache_key)
        else:
            # remove old result
            filepath = self._get_buffer_name(context)
            keys_to_remove = []
            for key in self._result_cache:
                if key.startswith(filepath):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                self._result_cache.pop(key, None)


    def _get_closest_delimiter(self, context):
        delimiter = ['.', '->', '::']
        current_line = self.vim.current.buffer[context['position'][1]-1]
        return max([current_line.rfind(d) + len(d) for d in delimiter])


    def _get_completion_position(self, context):
        return (context['position'][1], self._get_closest_delimiter(context)+1)


    def _get_completion_flags(self, context):
        include_flags = self._cpp_include_path
        if context['filetype'] in ['objc', 'objcpp']:
            include_flags = self._objc_include_path

        if context['bufname'].endswith('.ino'):
            for path in self._arduino_include_path:
                if path not in include_flags:
                    include_flags.append(path)

        if context['bufname'].endswith('.cu'):
            for path in self._cuda_path:
                if path not in include_flags:
                    include_flags.append(path)

        flags = []
        if context['filetype'] == 'c':
            flags = self._clang_cflags
        elif context['filetype'] == 'cpp':
            flags = self._clang_cppflags
        elif context['filetype'] == 'objc':
            flags = self._clang_objcflags
        elif context['filetype'] == 'objcpp':
            flags = self._clang_objcppflags
        else:
            flags = self._clang_cppflags
        flags += ['-I' + inc for inc in include_flags]
        return flags


    def _get_completion_result(self, context, filepath, position):
        # get flags and files
        flags = self._get_completion_flags(context)
        all_files = [(f, self._file_cache[f]) for f in self._file_cache]

        # get translation unit options
        tu_options = tu.PARSE_CACHE_COMPLETION_RESULTS | \
                     tu.PARSE_PRECOMPILED_PREAMBLE | \
                     tu.PARSE_INCOMPLETE
        if self._get_detail:
            tu_options |= tu.PARSE_DETAILED_PROCESSING_RECORD

        # cache translation unit
        if filepath not in self._translation_unit_cache:
            tunit = tu.from_source(filepath, flags,
                                   unsaved_files=all_files,
                                   options=tu_options)
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

        pattern = re.compile(r'\'([^\']*?)\',\s' + key)
        match = pattern.findall(result)
        if match:
            return ','.join(match)
        else:
            return ''


    def _get_parsed_completion_result(self, completion_result):
        parsed_result = []
        f = open('/home/joseph/test.log', 'w')
        for result in completion_result.results:
            try:
                f.write(str(result) + '\n')
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
        f.close()
        return parsed_result


    def _get_current_cache_key(self, context, position):
        line = self.vim.current.buffer[position[0]-1]
        column = position[1]
        delimiter = ['->', '.', '::']
        first = max([line.rfind(d, 0, column-1) for d in delimiter])
        fileid = os.path.join(context['cwd'], context['bufname']) + ':'

        if first < 0:
            function_name = re.compile(r'\s*([\w\d])\s*\([^\(&^\)]*\)\s*{')
            content = '\n'.join(self.vim.current.buffer[:position[0]])
            target = function_name.findall(content)
            if target:
                return fileid + target[-1]
            else:
                return fileid + 'start'

        second = max([line.rfind(d, 0, first-1) for d in delimiter])
        if second < 0:
            return fileid + line[0:first].strip()
        else:
            return fileid + line[second+1:first].strip()


    def _gather_completion(self, context, position, key):
        buffer_name = self._get_buffer_name(context)
        completion_result = \
            self._get_completion_result(context, buffer_name, position)
        parsed_result = \
            self._get_parsed_completion_result(completion_result)
        self._result_cache[key] = parsed_result
        self._position_cache[key] = position
        return parsed_result


    def _get_candidates(self, parsed_result):
        candidates = []
        for pr in parsed_result:
            candidate = {'word': pr['TypedText'],
                         'kind': pr['Placeholder'],
                         'menu': pr['ResultType']}
            candidates.append(candidate)
        return candidates


    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1


    def gather_candidates(self, context):
        self._update_file_cache(context)

        cache_key = self._get_current_cache_key(context,
                                                context['position'][1:])
        position = self._get_completion_position(context)

        parsed_result = []
        if cache_key not in self._result_cache:
            parsed_result = self._gather_completion(context, position,
                                                    cache_key)
        else:
            parsed_result = self._result_cache[cache_key]
        return self._get_candidates(parsed_result)
