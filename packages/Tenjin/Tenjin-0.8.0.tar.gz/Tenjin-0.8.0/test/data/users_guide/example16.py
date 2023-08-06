## template
filename = 'example16.pyhtml'

## convert into python code
import tenjin
from tenjin.helpers import *   # or escape, to_str
template = tenjin.Template(filename)
script = template.script
## or
# template = tenjin.Template()
# script = template.convert_file(filename)
## or
# template = tenjin.Template()
# input = open(filename).read()
# script = template.convert(input, filename)  # filename is optional

## show converted python code
print "---- python code ----"
print script,

## evaluate python code
context = {'title': 'pyTenjin Example', 'items': ['<AAA>','B&B','"CCC"']}
output = template.render(context)
print "---- output ----"
print output,
