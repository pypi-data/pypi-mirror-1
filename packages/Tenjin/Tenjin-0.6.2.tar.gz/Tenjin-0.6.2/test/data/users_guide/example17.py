filename = 'example16.pyhtml'
import tenjin
from tenjin.helpers import escape, to_str
template = tenjin.Template(filename, escapefunc='cgi.escape', tostrfunc='str')
print template.script

import cgi
title = 'pyTenjin Example'
items = ['<foo>', '&bar', '"baz"', None, True, False]
output = template.render({'title':title, 'items':items})
print output,
