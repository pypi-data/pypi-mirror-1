#
# auto generated
#

import unittest, os, re
from test import test_support

from testcase_helper import *

class FaqTest(unittest.TestCase, TestCaseHelper):

    basedir = '../test/data/faq'
    DIR = (os.path.dirname(__file__) or '.') + '/' + basedir
    CWD = os.getcwd()

    def setUp(self):
        os.chdir(self.__class__.DIR)

    def tearDown(self):
        os.chdir(self.__class__.CWD)

    def _test(self):
        filename = self.filename;
        dirname = os.path.dirname(filename)
        pwd = os.getcwd()
        if dirname:
            os.chdir(dirname)
            filename = os.path.basename(filename)
        s = open(filename).read()
        pat = r'\A\$ (.*?)\n'
        m = re.match(pat, s)
        command = m.group(1)
        expected = re.sub(pat, '', s)
        result = os.popen(command).read()
        self.assertTextEqual(expected, result)

    from glob import glob
    import os
    filenames = []
    filenames.extend(glob('%s/*.result' % basedir))
    filenames.extend(glob('%s/*/*.result' % basedir))
    filenames.extend(glob('%s/*.source' % basedir))
    filenames.extend(glob('%s/*/*.source' % basedir))
    for filename in filenames:
        #name = os.path.basename(filename).replace('.result', '')
        name = filename.replace(basedir+'/', '')
        s = "\n".join((\
             "def test_%s(self):" % re.sub('[^\w]', '_', name),
             "    self.filename = '%s'" % name,
             "    self._test()",
             ))
        exec s

def test_main():
    test_support.run_unittest(FaqTest)

if __name__ == '__main__':
    test_main()
