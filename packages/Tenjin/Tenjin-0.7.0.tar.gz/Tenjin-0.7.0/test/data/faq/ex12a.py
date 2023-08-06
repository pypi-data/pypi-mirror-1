import tenjin
from tenjin.helpers import *

## include 'escape()' and 'to_str()' functions to context data
context = { 'title': 'Example', 'items': ['A', 'B', 'C'] }
context['escape'] = escape
context['to_str'] = to_str

engine = tenjin.Engine()
output = engine.render('ex12a.pyhtml', context)
