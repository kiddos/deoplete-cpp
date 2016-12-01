# -*- coding: utf-8 -*-

from __future__ import print_function
from clang.cindex import Config as conf
from clang.cindex import TranslationUnit as tu
import subprocess
import os
import re


def setup_libclang(config, version):
    locate_command = 'ldconfig -p | grep libclang'
    locations = subprocess.check_output(locate_command, shell=True)
    locations = locations.decode('ascii').replace('\t', '').split('\n')

    for location in locations:
        loc = location.split('=>')[-1].strip()
        if loc.find(version) >= 0:
            config.loaded = False
            config.set_library_file(loc)
            config.set_compatibility_check(False)
            return True

    if len(locations) > 0:
        first = locations[0].split('=>')[-1].strip()
        config.loaded = False
        config.set_library_file(first)
        config.set_compatibility_check(False)
        return True
    return False


def get_buffer_name(context):
        buffer_name = context['bufname']
        # if the filetype is not supported by clang, make it a cpp
        if context['filetype'] not in ['c', 'cpp', 'objc', 'objcpp']:
            buffer_name += '.cpp'
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
                'TypedText': get_value(r, 'TypedText'),
                'ResultType': get_value(r, 'ResultType'),
                'Availability': get_value(r, 'Availability'),
                'Priority': int(get_value(r, 'Priority')),
                'Brief comment': get_value(r, 'Brief comment'),
                'LeftParen': get_value(r, 'LeftParen'),
                'RightParen': get_value(r, 'RightParen'),
                'Placeholder': get_value(r, 'Placeholder'),
                'Informative': get_value(r, 'Informative'),
            })
        except:
            continue
    return parsed_result


def get_candidates(parsed_result):
    candidates = []
    for pr in parsed_result:
        candidate = {'word': pr['TypedText'],
                        'kind': pr['Placeholder'],
                        'menu': pr['ResultType']}
        candidates.append(candidate)
    return candidates


class ClangCompletion():
    files = {}
    translation_units = {}
    positions = {}
    results = {}
    delimiter = ['::', '.', '->']


    def __init__(self, nvim):
        self.nvim = nvim


    def update_file_cache(self, context):
        filepath = get_buffer_name(context)
        content = '\n'.join(self.nvim.current.buffer)
        self.files[filepath] = content
        return filepath, content


    def prepare_cache_key(self, filepath, position):
        line = self.nvim.current.buffer[position[0]-1]
        column = position[1]
        first = max([line.rfind(d, 0, column-1) for d in self.delimiter])
        fileid = filepath + ':'
        content = self.files[filepath][0:position[0]]

        # if no delimiter is found try to find the function name
        if first < 0:
            # find the closest function name to current position
            func_name_pattern = re.compile(r'\s*([\w\d]*)\s*\([^\(&^\)]*\)\s*\n*{')
            target = func_name_pattern.findall(content)
            if target:
                return fileid + target[-1]
            else:
                return fileid + 'line' + str(position[0])

        # try to find the second delimiter
        second = max([line.rfind(d, 0, first-1) for d in self.delimiter])
        if second < 0:
            return fileid + line[0:first].strip()
        else:
            return fileid + line[second+1:first].strip()


def main():
    setup_libclang(conf, '3.8')


if __name__ == '__main__':
    main()
