import tenjin
from tenjin.helpers import *
from my_template import MyTemplate

import sys
template_name = len(sys.argv) > 1 and sys.argv[1] or 'flexibleindent.pyhtml'
engine = tenjin.Engine(templateclass=MyTemplate)
print("-------------------- script")
print(engine.get_template(template_name).script)
print("-------------------- html")
html = engine.render(template_name, {'items': ['AAA', None, 'CCC']})
print(html)
