#!/usr/bin/python2.4
# -*- coding: UTF-8 -*-
# adapted from:
#   http://blog.wordaligned.org/articles/2006/08/09/a-subversion-pre-commit-hook
# by Tarek Ziadé

from subprocess import Popen
from subprocess import PIPE
import re
import os
import sys

re_options = re.IGNORECASE | re.MULTILINE | re.DOTALL


class EOL(object):
    def finditer(self, content):
        if content.endswith('\n'):
            return
        yield 'n'

tab_catcher = re.compile(r'^\s*\t', re_options)
windows_catcher = re.compile(r'\r\n$', re_options)

testers = (('found TAB', tab_catcher),
           ('found CR/LF', windows_catcher))
           #('no new line at the end', EOL()))  removed

def command_output(cmd):
    """ Capture a command's standard output."""
    return Popen(cmd.split(), stdout=PIPE).communicate()[0]

def files_changed(look_cmd):
    """ List the files added or updated by this transaction."""
    def filename(line):
        return line[4:]

    def added_or_updated(line):
        return line and line[0] in ("A", "U")

    return [filename(line) for line in
            command_output(look_cmd % "changed").split("\n")
            if added_or_updated(line)]

def file_contents(filename, look_cmd):
    """Return a file's contents for this transaction"""
    return command_output("%s %s" % (look_cmd % "cat", filename))

def line_number(item, content):
    """returns the line number"""
    return content[:item.start()].count('\n')

def test_expression(expr, filename, look_cmd):
    """test regexpr over file"""
    content = file_contents(filename, look_cmd)
    # returning all errors, with line numbers
    return [line_number(item, content) for item in expr.finditer(content)]

def check_file(look_cmd):
    """checks Python files in this transaction"""
    def is_python_file(fname):
        return os.path.splitext(fname)[1] in ".py".split()

    erroneous_files = []

    for file in files_changed(look_cmd):
        if not is_python_file(file):
            continue

        for error_type, tester in testers:
            expr_res = test_expression(tester, file, look_cmd)
            if len(expr_res) == 0:
                continue
            for line in expr_res:
                erroneous_files.append((error_type, file, line))

    num_failures = len(erroneous_files)

    if num_failures > 0:
        sys.stderr.write("[ERROR] please check your files:\n")
        for error_type, file, line in erroneous_files:
            sys.stderr.write("[ERROR] %s in %s line %d\n" % (error_type,
                                                             file,
                                                             line))

    return num_failures

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-r", "--revision",
                        help="Test mode. TXN actually refers to a revision.",
                        action="store_true", default=False)
    errors = 0
    (opts, (repos, txn_or_rvn)) = parser.parse_args()
    look_opt = ("--transaction", "--revision")[opts.revision]
    look_cmd = "svnlook %s %s %s %s" % (
        "%s", repos, look_opt, txn_or_rvn)
    errors += check_file(look_cmd)

    return errors

if __name__ == "__main__":
    import sys
    sys.exit(main())

