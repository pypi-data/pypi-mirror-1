# -*- coding: utf-8 -*-

###
### $Release: 0.8.0 $
### copyright(c) 2007-2009 kuwata-lab.com all rights reserved.
###

import unittest
import sys, os, re

from testcase_helper import *
import tenjin
from tenjin.helpers import *


class EncodingTest(unittest.TestCase, TestCaseHelper):


    def _test_render(self, template=None, to_str=None,
                     expected_buf=None, expected_output=None,
                     expected_errcls=None, expected_errmsg=None):
        buf = []
        context = {'to_str': to_str}
        template.render(context, _buf=buf)
        self.assertEquals(expected_buf, buf)
        if expected_errcls:
            ex = self.assertRaise(expected_errcls, lambda: template.render(context))
            if expected_errmsg:
                self.assertEquals(expected_errmsg, str(ex))
        elif expected_output:
            self.assertNotRaise(lambda: template.render(context))
            output = template.render(context)
            self.assertTextEqual(expected_output, output)
            self.assertTrue(isinstance(output, type(output)))
        else:
            raise "*** internal error"

    def test_with_binary_template_and_binary_data(self):
        t = tenjin.Template()
        input = "**あ**\n#{'あ'}\n"
        script = "_buf.extend(('''**\xe3\x81\x82**\n''', to_str('\xe3\x81\x82'), '''\\n''', ));\n"
        self.assertTextEqual(script, t.convert(input))
        ## do nothing in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode=None),
            expected_buf    = ['**\xe3\x81\x82**\n', '\xe3\x81\x82', '\n'],
            expected_output = "**あ**\nあ\n"
        )
        ## encode unicode into binary in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode='utf-8', decode=None),
            expected_buf    = ['**\xe3\x81\x82**\n', '\xe3\x81\x82', '\n'],
            expected_output = "**あ**\nあ\n"
        )
        ## decode binary into unicode in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode='utf-8'),
            expected_buf    = ['**\xe3\x81\x82**\n', u'\u3042', '\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 2: ordinal not in range(128)"
        )

    def test_with_unicode_template_and_binary_data(self):
        t = tenjin.Template(encoding='utf-8')
        input = "**あ**\n#{'あ'}\n"
        script = u"_buf.extend((u'''**\u3042**\n''', to_str('\u3042'), u'''\\n''', ));\n"
        self.assertTextEqual(script, t.convert(input))
        ## do nothing in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode=None),
            expected_buf    = [u'**\u3042**\n', '\xe3\x81\x82', u'\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 0: ordinal not in range(128)"
         )
        ## encode unicode in binary in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode='utf-8', decode=None),
            expected_buf    = [u'**\u3042**\n', '\xe3\x81\x82', u'\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 0: ordinal not in range(128)"
         )
        ## decode binary into unicode in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode='utf-8'),
            expected_buf    = [u'**\u3042**\n', u'\u3042', u'\n'],
            expected_output = u"**あ**\nあ\n"
        )

    def test_binary_template_with_unicode_data(self):
        t = tenjin.Template()
        input = "**あ**\n#{u'あ'}\n"
        script = "_buf.extend(('''**\xe3\x81\x82**\n''', to_str(u'\xe3\x81\x82'), '''\\n''', ));\n"
        self.assertTextEqual(script, t.convert(input))
        ## do nothing in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode=None),
            #expected_buf    = ['**\xe3\x81\x82**\n', u'\u3042', '\n'],
            expected_buf    = ['**\xe3\x81\x82**\n', u'\xe3\x81\x82', '\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 2: ordinal not in range(128)"
         )
        ## encode unicode in binary in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode='utf-8', decode=None),
            expected_buf    = ['**\xe3\x81\x82**\n', '\xc3\xa3\xc2\x81\xc2\x82', '\n'],
            expected_output = "**あ**\n\xc3\xa3\xc2\x81\xc2\x82\n"    ## GARGLED!!
         )
        ## decode binary into unicode in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode='utf-8'),
            expected_buf    = ['**\xe3\x81\x82**\n', u'\xe3\x81\x82', '\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 2: ordinal not in range(128)"
        )

    def test_unicode_template_with_unicode_data(self):
        t = tenjin.Template(encoding='utf-8')
        input = "**あ**\n#{u'あ'}\n"
        script = u"_buf.extend((u'''**\u3042**\n''', to_str(u'\u3042'), u'''\\n''', ));\n"
        self.assertTextEqual(script, t.convert(input))
        ## do nothing in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode=None),
            expected_buf    = [u'**\u3042**\n', u'\u3042', u'\n'],
            expected_output = u"**あ**\nあ\n"
         )
        ## encode unicode in binary in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode='utf-8', decode=None),
            expected_buf    = [u'**\u3042**\n', '\xe3\x81\x82', u'\n'],
            expected_errcls = UnicodeDecodeError,
            expected_errmsg = "'ascii' codec can't decode byte 0xe3 in position 0: ordinal not in range(128)"
         )
        ## decode binary into unicode in to_str()
        self._test_render(
            template        = t,
            to_str          = tenjin.generate_tostrfunc(encode=None, decode='utf-8'),
            expected_buf    = [u'**\u3042**\n', u'\u3042', u'\n'],
            expected_output = u"**あ**\nあ\n"
        )



if __name__ == '__main__':
    unittest.main()

