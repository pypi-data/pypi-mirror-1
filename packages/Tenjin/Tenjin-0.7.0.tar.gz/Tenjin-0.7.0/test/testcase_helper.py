###
### $Release: 0.7.0 $
### copyright(c) 2007-2009 kuwata-lab.com all rights reserved.
###

#import unittest
import os, sys, difflib, re, traceback
import yaml

__all__ = ['TestCaseHelper', 'read_file', 'write_file',
           'remove_unmatched_test_methods',
           'python3', 'python2', '_unicode', '_bytes']

python3 = sys.version_info[0] == 3
python2 = sys.version_info[0] == 2
if python2:
    _unicode = unicode
    _bytes   = str
elif python3:
    _unicode = str
    _bytes   = bytes


def read_file(filename, mode='rb'):
    f = None
    try:
        f = open(filename, mode)
        return f.read()
    finally:
        if f: f.close()

def write_file(filename, content, mode='wb'):
    if isinstance(content, _unicode):
        content = content.encode('utf-8')
    f = None
    try:
        f = open(filename, mode)
        f.write(content)
    finally:
        if f: f.close()

def remove_unmatched_test_methods(testcase_class, pattern=None):
    pattern = pattern or os.environ.get('TEST')
    if not pattern: return
    rexp = re.compile(pattern)
    for m in dir(testcase_class):
        if m.startswith('test_'):
            name = m[len('test_'):]
            if not rexp.search(name):
                delattr(testcase_class, m)


class TestCaseHelper:

    def _testname(self):
        try:
            return self._TestCase__testMethodName
        except AttributeError:
            return self._testMethodName

    def assertTextEqual(self, text1, text2, encoding=None):
        if text1 == text2:
            self.assertEqual(text1, text2)
        else:
            file1, file2 = '.tmp.file1', '.tmp.file2'
            if encoding:
                if isinstance(text1, _unicode):
                    text1 = text1.encode(encoding or 'utf-8')   # unicode to binary
                if isinstance(text2, _unicode):
                    text2 = text2.encode(encoding or 'utf-8')   # unicode to binary
            write_file(file1, text1)
            write_file(file2, text2)
            f = os.popen("diff -u %s %s" % (file1, file2))
            output = f.read()
            f.close()
            os.unlink(file1)
            os.unlink(file2)
            mesg = re.sub(r'.*?\n', '', output, 2)
            self.assertEqual(text1, text2, mesg)

    def assertRaise(self, exc_class, callable_, *args, **kwargs):
        try:
            callable_(*args, **kwargs)
        except exc_class:
            ex = sys.exc_info()[1]
            return ex
        else:
            exc_class_name = getattr(exc_class, '__name__', None) or str(exc_class)
            self.fail("%s not raised" % exc_class_name)

    def assertNotRaise(self, callable_, *args, **kwargs):
        try:
            return callable_(*args, **kwargs)
        except Exception:
            ex = sys.exc_info()[1]
            self.fail("unexpected exception raised: " + repr(ex))

    def assertExists(self, filename):
        if not os.path.exists(filename):
            self.fail("file not exist: " + repr(filename))

    def assertNotExist(self, filename):
        if os.path.exists(filename):
            self.fail("file exists: " + repr(filename))

    def load_testdata(filename, untabify=True):
        i = filename.rfind('.')
        if filename[i:] != '.yaml' and filename[i:] != '.yml':
            filename = filename[:i] + '.yaml'
        input = read_file(filename)
        if untabify:
            input = input.expandtabs()
        ydoc = yaml.load(input)
        return ydoc
    load_testdata = staticmethod(load_testdata)

    def generate_testcode(filename, untabify=True, testmethod='_test', lang='python'):
        doclist = TestCaseHelper.load_testdata(filename, untabify)
        table = {}
        buf = []
        for doc in doclist:
            if 'name' not in doc:
                raise Exception("'name:' is required.")
            name = doc['name']
            if name in table:
                raise Exception("'name: %s' is duplicated." % name)
            table[name] = doc
            buf.append(        "def test_%s(self):" % name)
            for key, val in doc.items():
                if key[-1] == '*':
                    key = key[:-1]
                    val = val.get(lang)
                if key == 'exception':
                    buf.append("    self.%s = %s" % (key, val))
                elif isinstance(val, str):
                    buf.append('    self.%s = r"""%s"""' % (key, val))
                else:
                    buf.append("    self.%s = %s" % (key, repr(val)))
            buf.append(        "    self.%s()" % testmethod)
            buf.append(        "#")
        buf.append('')
        code = "\n".join(buf)
        return code
    generate_testcode = staticmethod(generate_testcode)
