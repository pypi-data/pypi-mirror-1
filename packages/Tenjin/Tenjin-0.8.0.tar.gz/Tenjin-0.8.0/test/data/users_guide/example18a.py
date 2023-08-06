import tenjin
from tenjin.helpers import *

def link_to(label, url):
    return '<a href="%s">%s</a>' % (escape(url), escape(label))

engine = tenjin.Engine()
context = { 'label': 'Top', 'url': '/' }
output = engine.render('example18.pyhtml', context)
print output,
