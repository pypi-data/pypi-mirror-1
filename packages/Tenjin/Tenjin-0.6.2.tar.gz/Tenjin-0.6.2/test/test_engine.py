###
### $Rev: 137 $
### $Release: 0.6.2 $
### copyright(c) 2007-2008 kuwata-lab.com all rights reserved.
###

import unittest
from test import test_support
import sys, os, re, time
from glob import glob

from testcase_helper import *
import tenjin
#from tenjin.helpers import escape, to_str
from tenjin.helpers import *


def _convert_data(data, lang='python'):
    if isinstance(data, dict):
        for k in data.keys():
            v = data[k]
            if k[-1] == '*':
                assert isinstance(v, dict)
                data[k[:-1]] = v.get(lang)
            if isinstance(v, dict) and v.has_key(lang):
                data[k] = v[lang]
            else:
                _convert_data(v, lang)
    elif isinstance(data, list):
        for k, v in enumerate(data):
            if isinstance(v, dict) and v.has_key(lang):
                data[k] = v[lang]
            else:
                _convert_data(v, lang)


def _remove_files(basenames=[]):
    for basename in basenames:
        for filename in glob("%s*" % basename):
            os.unlink(filename)


class EngineTest(unittest.TestCase, TestCaseHelper):

    #code = TestCaseHelper.generate_testcode(__file__)
    #exec code
    datalist = TestCaseHelper.load_testdata(__file__)
    testdata = dict([ (d['name'], d) for d in datalist ])
    _convert_data(testdata, lang='python')
    data = testdata['basic']
    for d in data['templates']:
        d['filename'] = d['filename'].replace('.xxhtml', '.pyhtml')
    templates = dict([(hash['filename'], hash['content']) for hash in data['templates']])
    expected  = dict([(hash['name'], hash['content']) for hash in data['expected']])
    contexts  = data['contexts']


    #def setUp(self):
    #    testdata = EngineTest.testdata['basic']
    #    for hash in testdata['templates']:
    #        open(hash['filename'], 'w').write(hash['content'])


    #def tearDown(self):
    #    for hash in EngineTest.testdata['basic']['templates']:
    #        filename = hash['filename']
    #        for fname in [filename, filename+'.cache', filename+'.marshal']:
    #            if os.path.exists(fname):
    #                os.unlink(fname)


    def _test_basic(self):
        if not self.is_target():
            return
        #
        try:
            testdata = EngineTest.testdata['basic']
            for hash in testdata['templates']:
                open(hash['filename'], 'w').write(hash['content'])
            #
            testname = self.testname()
            lst = testname[len('test_basic'):].split('_')
            action   = lst[1]                # 'list', 'show', 'create', or 'edit'
            shortp   = lst[2] == 'short'     # 'short' or 'long'
            layoutp  = lst[3] != 'nolayout'  # 'nolayout' or 'withlayout'
            layout   = layoutp and 'user_layout.pyhtml' or None
            engine   = tenjin.Engine(prefix='user_', postfix='.pyhtml', layout=layout)
            context  = EngineTest.contexts[action].copy()
            key      = 'user_' + action + (layout and '_withlayout' or '_nolayout')
            expected = EngineTest.expected[key]
            filename = 'user_%s.pyhtml' % action
            tplname  = shortp and ':'+action or filename
            if layout:
                output = engine.render(tplname, context)
            else:
                output = engine.render(tplname, context, layout=False)
            self.assertTextEqual(expected, output)
        finally:
            filenames = [ hash['filename'] for hash in EngineTest.testdata['basic']['templates'] ]
            _remove_files(filenames)
            #for hash in EngineTest.testdata['basic']['templates']:
            #    filename = hash['filename']
            #    for fname in [filename, filename+'.cache', filename+'.marshal']:
            #        if os.path.exists(fname):
            #            os.unlink(fname)


    ## long, nolayout

    def test_basic_list_long_nolayout(self):
        self._test_basic()

    def test_basic_show_long_nolayout(self):
        self._test_basic()

    def test_basic_create_long_nolayout(self):
        self._test_basic()

    def test_basic_edit_long_nolayout(self):
        self._test_basic()


    ## short, nolayout

    def test_basic_list_short_nolayout(self):
        self._test_basic()

    def test_basic_show_short_nolayout(self):
        self._test_basic()

    def test_basic_create_short_nolayout(self):
        self._test_basic()

    def test_basic_edit_short_nolayout(self):
        self._test_basic()


    ## long, withlayout

    def test_basic_list_long_withlayout(self):
        self._test_basic()

    def test_basic_show_long_withlayout(self):
        self._test_basic()

    def test_basic_create_long_withlayout(self):
        self._test_basic()

    def test_basic_edit_long_withlayout(self):
        self._test_basic()


    ## short, withlayout

    def test_basic_list_short_withlayout(self):
        self._test_basic()

    def test_basic_show_short_withlayout(self):
        self._test_basic()

    def test_basic_create_short_withlayout(self):
        self._test_basic()

    def test_basic_edit_short_withlayout(self):
        self._test_basic()


    ## ----------------------------------------


    def test_capture_and_echo(self):
        if not self.is_target():
            return
        hash = EngineTest.testdata['test_capture_and_echo']
        layout = hash['layout']
        content = hash['content']
        expected = hash['expected']
        layout_filename = 'user_layout.pyhtml'
        content_filename = 'user_content.pyhtml'
        context = { 'items': ['AAA', 'BBB', 'CCC'] }
        try:
            open(layout_filename, 'w').write(layout)
            open(content_filename, 'w').write(content)
            engine = tenjin.Engine(prefix='user_', postfix='.pyhtml', layout=':layout')
            output = engine.render(':content', context)
            self.assertTextEqual(expected, output)
        finally:
            _remove_files([layout_filename, content_filename])


    def test_captured_as(self):
        if not self.is_target():
            return
        hash = EngineTest.testdata['test_captured_as']
        files = ( ('content.pyhtml',      hash['content']),
                  ('customlayout.pyhtml', hash['customlayout']),
                  ('baselayout.pyhtml',   hash['baselayout']),
                  )
        context = hash['context']
        expected = hash['expected']
        try:
            for filename, content in files:
                open(filename, 'w').write(content)
            engine = tenjin.Engine(postfix='.pyhtml')
            output = engine.render(':content', context)
            self.assertTextEqual(expected, output)
        finally:
            _remove_files([ t[0] for t in files ])


    def test_local_layout(self):
        if not self.is_target():
            return
        hash = EngineTest.testdata['test_local_layout']
        context = hash['context']
        names = ['layout_html', 'layout_xhtml', 'content_html']
        def fname(base):
            return 'local_%s.pyhtml' % base
        try:
            for name in names:
                open(fname(name), 'w').write(hash[name])
            engine = tenjin.Engine(prefix='local_', postfix='.pyhtml', layout=':layout_html')
            ##
            def _test(expected, statement):
                content_html = hash['content_html'] + statement
                open(fname('content_html'), 'w').write(content_html)
                actual = engine.render(':content_html', context)
                self.assertTextEqual(expected, actual)
            ##
            _test(hash['expected_html'], '')
            time.sleep(1)
            _test(hash['expected_xhtml'], "<?py _context['_layout'] = ':layout_xhtml' ?>\n")
            time.sleep(1)
            _test(hash['expected_nolayout'], "<?py _context['_layout'] = False ?>\n")
            ##
        finally:
            #for name in names:
            #    for suffix in ['', '.cache', '.marshal']:
            #        filename = fname(name) + suffix
            #        if os.path.isfile(filename):
            #            os.unlink(filename)
            _remove_files([ fname(name) for name in names ])


    def test_cachefile(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_cachefile']
        filenames = { 'layout': 'layout.pyhtml',
                      'page': 'account_create.pyhtml',
                      'form': 'account_form.pyhtml',
                    }
        expected = data['expected']
        context = { 'params': { } }
        try:
            for key, filename in filenames.iteritems():
                open(filename, 'w').write(data[key])
            props = { 'prefix':'account_', 'postfix':'.pyhtml', 'layout':'layout.pyhtml' }
            ## no caching
            props['cache'] = False
            engine = tenjin.Engine(**props)
            output = engine.render(':create', context)
            self.assertTextEqual(expected, output)
            self.assertFalse(os.path.exists('account_create.pyhtml.cache'))
            self.assertFalse(os.path.exists('account_form.pyhtml.cache'))
            ## bytecode caching
            props['cache'] = True
            engine = tenjin.Engine(**props)
            output = engine.render(':create', context)
            self.assertTextEqual(expected, output)
            self.assertTrue(os.path.exists('account_create.pyhtml.cache'))
            self.assertTrue(os.path.exists('account_form.pyhtml.cache'))
            engine = tenjin.Engine(**props)
            output = engine.render(':create', context)
            self.assertTextEqual(expected, output)
        finally:
            _remove_files(filenames.values())


    def test_change_layout(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_change_layout']
        ## setup
        basenames = ['baselayout', 'customlayout', 'content']
        for basename in basenames:
            open('%s.pyhtml' % basename, 'w').write(data[basename])
        ## body
        try:
            engine = tenjin.Engine(layout='baselayout.pyhtml')
            output = engine.render('content.pyhtml')
            expected = data['expected']
            self.assertTextEqual(expected, output)
        ## teardown
        finally:
            _remove_files(basenames)


    def test_context_scope(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_context_scope']
        base = data['base']
        part = data['part']
        expected = data['expected']
        for basename in ('base', 'part'):
            open('%s.pyhtml' % basename, 'w').write(data[basename])
        #
        try:
            engine = tenjin.Engine()
            context = {}
            output = engine.render('base.pyhtml', context)
            expected = data['expected']
            self.assertTextEqual(expected, output)
        finally:
            _remove_files(['base', 'part'])


    def test_template_args(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_template_args']
        content = data['content']
        expected = data['expected']
        context = data['context']
        for basename in ('content', ):
            open('%s.pyhtml' % basename, 'w').write(data[basename])
        #
        try:
            def f1():
                engine = tenjin.Engine(cache=True)
                assert engine.get_template('content.pyhtml').args is not None
                output = engine.render('content.pyhtml', context)
            ex = self.assertRaises(NameError, f1)
            #import sys; sys.stderr.write("*** debug: ex=%s\n" % (repr(ex)))
            #engine = tenjin.Engine(cache=True)
            #assert engine.get_template('content.pyhtml').args is not None
            #output = engine.render('content.pyhtml', context)
            #self.assertTextEqual(expected, output)
            ex = self.assertRaises(NameError, f1)
        finally:
            _remove_files(['content'])


    def test_cached_contents(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_cached_contents']
        from glob import glob
        def _test(filename, cachename, cachemode, input, expected_script, expected_args):
            if input:
                open(filename, 'w').write(input)
            engine = tenjin.Engine(cache=cachemode)
            t = engine.get_template(filename)
            self.assertEqual(expected_args, t.args)
            self.assertTextEqual(expected_script, t.script)
            import marshal
            dct = marshal.load(open(engine.cachename(filename), 'rb'))
            self.assertEqual(expected_args, dct['args'])
            self.assertTextEqual(expected_script, dct['script'])
        ##
        try:
            ## args=[x,y,z], cache=1
            filename = 'input.pyhtml'
            for f in glob(filename+'*'): os.path.exists(f) and os.remove(f)
            script = data['script1']
            args  = data['args1']
            input = data['input1']
            cachename = filename+'.cache'
            self.assertFalse(os.path.exists(cachename))
            _test(filename, cachename, 1, input, script, args)
            self.assertTrue(os.path.exists(cachename))
            _test(filename, cachename, 1, None, script, args)
            ## args=[], cache=1
            cachename = filename+'.cache'
            input = data['input2']  # re.sub(r'<\?py #@ARGS.*?\?>\n', '<?py #@ARGS ?>\n', input)
            script = data['script2']  # re.sub(r'#@ARGS.*?\n', '#@ARGS \n', cache)
            args  = data['args2']   # []
            time.sleep(1)
            #self.assertTrue(os.path.exists(cachename))
            _test(filename, cachename, 1, input, script, args)
            #self.assertTrue(os.path.exists(cachename))
            _test(filename, cachename, 1, None, script, args)
        finally:
            _remove_files(['input.pyhtml'])


    def _test_template_path(self, keys):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_template_path']
        basedir = 'test_templates'
        try:
            os.mkdir(basedir)
            os.mkdir(basedir + '/common')
            os.mkdir(basedir + '/user')
            d = { 'layout':keys[0], 'body':keys[1], 'footer':keys[2], }
            for key in ('layout', 'body', 'footer'):
                filename = '%s/common/%s.pyhtml' % (basedir, key)
                open(filename, 'w').write(data['common_'+key])
                if d[key] == 'user':
                    filename = '%s/user/%s.pyhtml' % (basedir, key)
                    open(filename, 'w').write(data['user_'+key])
            #
            path = [basedir+'/user', basedir+'/common']
            engine = tenjin.Engine(postfix='.pyhtml', path=path, layout=':layout')
            context = {'items':('AAA', 'BBB', 'CCC')}
            output = engine.render(':body', context)
            #
            expected = data['expected_' + '_'.join(keys)]
            self.assertTextEqual(expected, output)
        finally:
            #os.removedirs(basedir)
            #pass
            for filename in glob('%s/*/*' % basedir):
                os.unlink(filename)
            for filename in glob('%s/*' % basedir):
                os.rmdir(filename)
            os.rmdir(basedir)

    def test_template_path_common_common_common(self):
        self._test_template_path(('common', 'common', 'common'))
    def test_template_path_user_common_common(self):
        self._test_template_path(('user',   'common', 'common'))
    def test_template_path_common_user_common(self):
        self._test_template_path(('common', 'user',   'common'))
    def test_template_path_user_user_common(self):
        self._test_template_path(('user',   'user',   'common'))
    def test_template_path_common_common_user(self):
        self._test_template_path(('common', 'common', 'user'))
    def test_template_path_user_common_user(self):
        self._test_template_path(('user',   'common', 'user'))
    def test_template_path_common_user_user(self):
        self._test_template_path(('common', 'user',   'user'))
    def test_template_path_user_user_user(self):
        self._test_template_path(('user',   'user',   'user'))


    def test_preprocessor(self):
        if not self.is_target():
            return
        data = EngineTest.testdata['test_preprocessor']
        try:
            basenames = ('form', 'create', 'update', 'layout', )
            filenames = []
            for name in basenames:
                filename = 'prep_%s.pyhtml' % name
                filenames.append(filename)
                open(filename, 'w').write(data[name])
            engine = tenjin.Engine(prefix='prep_', postfix='.pyhtml', layout=':layout', preprocess=True)
            #
            context = {
                'title': 'Create',
                'action': 'create',
                'params': { 'state': 'NY' },
            }
            actual = engine.render(':create', context)  # 1st
            self.assertTextEqual(data['expected1'], actual)
            context['params'] = {'state': 'xx'}
            actual = engine.render(':create', context)  # 2nd
            #self.assertEqual(data['expected1'], actual)
            self.assertEqual(data['expected1'].replace(r' checked="checked"', ''), actual)
            #
            context = {
                'title': 'Update',
                'action': 'update',
                'params': { 'state': 'NY' },
            }
            actual = engine.render(':update', context)  # 1st
            self.assertTextEqual(data['expected2'], actual)
            context['params'] = { 'state': 'xx' }
            actual = engine.render(':update', context)  # 2nd
            self.assertEqual(data['expected2'], actual) # not changed!
            #
            self.assertTextEqual(data['cache1'], engine.get_template(':form').script)
            self.assertTextEqual(data['cache2'], engine.get_template(':create').script)
            self.assertTextEqual(data['cache3'], engine.get_template(':layout').script)
            self.assertTextEqual(data['cache4'], engine.get_template(':update').script)
            #
        finally:
            _remove_files(filenames)



def test_main():
    test_support.run_unittest(EngineTest)


if __name__ == '__main__':
    test_main()

