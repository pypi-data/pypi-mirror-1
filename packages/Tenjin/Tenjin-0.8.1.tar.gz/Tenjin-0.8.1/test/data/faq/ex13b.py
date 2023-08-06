import tenjin
from tenjin.helpers import *

## include 'escape()' and 'to_str()' functions to context data
context = { 'title': 'Example', 'items': ['A', 'B', 'C'] }
context['escape'] = escape
context['to_str'] = to_str

## delete implicit call of 'to_str()' function
engine = tenjin.Engine(tostrfunc='')

## show python code and output
filename = 'ex13b.pyhtml'
template = engine.get_template(filename)
output = engine.render(filename, context)
print "--- python code ---"
print template.script
print "--- output ---"
print output,
