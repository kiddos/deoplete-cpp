from __future__ import print_function
from clang.cindex import TranslationUnit as tu
import sys
import re

def code_complete(filepath, line, column, standard):
    f = open(filepath)
    content = str(f.read())
    files = [('~/' + filepath, r'' + content)]
    f.close()

    options = tu.PARSE_CACHE_COMPLETION_RESULTS | \
        tu.PARSE_DETAILED_PROCESSING_RECORD |  \
        tu.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION |   \
        tu.PARSE_INCOMPLETE |  \
        tu.PARSE_PRECOMPILED_PREAMBLE

    tunit = tu.from_source(filepath, args=['-std=' + standard],
        unsaved_files=files,
        options=options)

    cr = tunit.codeComplete(filepath, int(line), int(column),
        unsaved_files=files)
    return [str(c) for c in cr.results]


def main():
    if len(sys.argv) != 6:
        print('Usage:\n'
            'python test_code_complete.py '
            'filepath line column standard expected_string')
        return
    result = str(code_complete(sys.argv[1], sys.argv[2],
        sys.argv[3], sys.argv[4]))
    pattern = re.compile(r'' + sys.argv[5])
    if not pattern.findall(result):
        print('pattern: ' + sys.argv[5] + ' not found')
        raise Exception


if __name__ == '__main__':
    main()
