from .base import Base
import re
import os


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.vim = vim
        self.name = 'cpp/include'
        self.mark = '[c++-i]'
        self.rank = 600
        self.debug_enable = False
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp', 'cuda', 'arduino']
        self.input_pattern = (r'\s*#include\s*<[^>]*')

        self.default_path = [
            '/usr/include'
        ]

        self.max_menu_width = 160
        self.max_abbr_width = 160

        # include path
        self._c_include_path = \
            self.vim.vars['deoplete#sources#cpp#c_include_path']
        self._cpp_include_path = \
            self.vim.vars['deoplete#sources#cpp#cpp_include_path']
        self._objc_include_path = \
            self.vim.vars['deoplete#sources#cpp#objc_include_path']
        self._objcpp_include_path = \
            self.vim.vars['deoplete#sources#cpp#objcpp_include_path']


    def _get_include_completion(self, context):
        pattern = re.compile(r'\s*#include\s*<([^>]*)')
        result = pattern.findall(context['input'])
        if result:
            # get the corresponding paths for different filetype
            paths = self._cpp_include_path
            if context['filetype'] == 'c':
                paths = self._c_include_path
            elif context['filetype'] == 'objc':
                paths = self._c_include_path
            elif context['filetype'] == 'objcpp':
                paths = self._c_include_path
            for path in self.default_path:
                if path not in paths:
                    paths = [path] + paths

            complete_path = result[0].rfind('/')
            # if no / is found
            if complete_path < 0:
                all_paths = []
                for path in paths:
                    if os.path.isdir(path):
                        all_paths += os.listdir(path)
                return all_paths
            else:
                start = result[0].rfind('<') + 1
                folder = result[0][start:complete_path]
                all_paths = []
                for path in paths:
                    diretory = os.path.join(path, folder)
                    if os.path.isdir(diretory):
                        all_paths += os.listdir(diretory)
                return all_paths
        return []


    def get_complete_position(self, context):
        m = re.search(r'[</.]$', context['input'])
        return m.end() if m else -1


    def gather_candidates(self, context):
        includes = self._get_include_completion(context)
        return [
            {'word': inc, 'kind': 'path'}
            for inc in includes
        ]
