import tenjin
from tenjin.helpers import *

def f1(label, url):
    return '<a href="%s">%s</a>' % (escape(url), escape(label))

engine = tenjin.Engine()
context = { 'label': 'Top', 'url': '/' }
globals = {'escape':escape, 'to_str':to_str, 'link_to':f1}
output = engine.render('example18.pyhtml', context, globals=globals)
print output,
