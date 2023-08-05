import tenjin
from tenjin.helpers import *

## set encoding option
encoding = 'euc-jp'
engine = tenjin.Engine(encoding=encoding)  
context = { 'title': u'\u65e5\u672c\u8a9e' }
output = engine.render('ex11.euc-jp.pyhtml', context)
assert isinstance(output, unicode)
print output.decode(encoding)   # decode unicode object into string
