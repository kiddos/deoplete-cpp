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


def main():
    setup_libclang(conf, '3.8')


if __name__ == '__main__':
    main()
