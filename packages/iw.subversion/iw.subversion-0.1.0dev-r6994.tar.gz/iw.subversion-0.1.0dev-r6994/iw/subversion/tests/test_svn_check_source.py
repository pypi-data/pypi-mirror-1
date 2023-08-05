import os
import unittest
import sys

dirname = os.path.dirname(__file__)
if dirname == '':
    dirname = '.'
dirname = os.path.realpath(dirname)
dirname = os.path.split(dirname)[0]

if dirname not in sys.path:
    sys.path.append(dirname)

rotten = os.path.join(os.path.dirname( __file__), 'rotten.py')

import svn_check_source

# patching so rotten is returned all the time
def get_rotten(filename, look_cmd):
    """returns rotten content"""
    return open(rotten).read()

svn_check_source.file_contents = get_rotten

# patching command_output
def _command_output(cmd):
    return 'A \nU \n'

svn_check_source.command_output = _command_output

# patching files_changed
def _files_changed(look_cmd):
    return ['ok.py']

svn_check_source.files_changed = _files_changed

# patching sys.stderr to get what a committer gets

class FakeSTD(object):
    def __init__(self):
        self._msg = []

    def write(self, msg):
        self._msg.append(msg)

    def __str__(self):
        return ''.join(self._msg)

std = FakeSTD()
sys.stderr = std

class TestSVNChecker(unittest.TestCase):

    def test_error_displayer(self):

        result = svn_check_source.check_file('%s')
        wanted = ('[ERROR] please check your files:\n'
                  '[ERROR] found TAB in ok.py line 5\n'
                  '[ERROR] found TAB in ok.py line 9\n')

        self.assertEquals(str(std), wanted)


def test_suite():
    tests = [unittest.makeSuite(TestSVNChecker)]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

