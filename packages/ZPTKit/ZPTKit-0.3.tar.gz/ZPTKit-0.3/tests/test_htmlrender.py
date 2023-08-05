import os
from ZPTKit.htmlrender import *
import difflib

def print_diff(s1, s2):
    differ = difflib.Differ()
    result = list(differ.compare(s1.splitlines(), s2.splitlines()))
    print '\n'.join(result)

def all_char(line, char):
    """
    Does the given line consist of only `char` characters?
    """
    return line.strip() and line.strip() == char*len(line.strip())

def split_file(filename):
    tests = []
    last_source = []
    last_dest = None
    f = open(filename)
    for line in f:
        if all_char(line, '-'):
            last_dest = []
        elif all_char(line, '='):
            tests.append((''.join(last_source), ''.join(last_dest)))
            last_source = []
            last_dest = None
        elif last_dest is None:
            last_source.append(line)
        else:
            last_dest.append(line)
    if last_dest is not None:
        tests.append((''.join(last_source), ''.join(last_dest)))
    return tests

def test_transformations():
    tests = split_file(os.path.splitext(__file__)[0] + '.data')
    for source, dest in tests:
        if not render(source).strip() == dest.strip():
            print "Bad comparison:"
            print "Source:   %r" % source
            print "Dest:     %r" % dest
            print "Rendered: %r" % render(source)
            print 'SOURCE:'
            print source
            print 'DEST:'
            print dest
            print 'RENDERED:'
            print render(source)
            assert 0

if __name__ == '__main__':
    test_transformations()
