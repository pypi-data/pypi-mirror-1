import tenjin
from tenjin.helpers import *

## generate to_str() function which decode unicode object
## into string object according to encoding name.
encoding = 'euc-jp'
to_str = tenjin.generate_tostrfunc(encoding)

engine = tenjin.Engine()
context = { 'title': u'\u65e5\u672c\u8a9e' }
output = engine.render('ex11.euc-jp.pyhtml', context)
assert isinstance(output, str)
print output
