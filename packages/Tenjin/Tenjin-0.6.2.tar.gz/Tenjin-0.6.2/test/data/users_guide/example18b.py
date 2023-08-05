import tenjin
from tenjin.helpers import *

## If you specify encoding option for Template() or Engine(),
## content of template will be converted into unicode object.
engine = tenjin.Engine(encoding='euc-jp')
## If you want to see python code, try the following:
##   template = engine.get_template(filename)
##   print template.script

## You must encode output into string because output will be unicode.
context = { 'name': u'\u65e5\u672c\u8a9e' }  # non-ascii characters
output = engine.render('encoding1.pyhtml', context)
if isinstance(output, unicode):
   output = output.encode('euc-jp')
print output,
