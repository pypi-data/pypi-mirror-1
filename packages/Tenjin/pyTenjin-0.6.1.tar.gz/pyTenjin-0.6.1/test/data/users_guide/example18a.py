import tenjin
from tenjin.helpers import *

## Create to_str() function which encodes unicode object into string
## according to encoding.
to_str = tenjin.generate_tostrfunc('euc-jp')
         #  ex.  to_str(u'\u65e5\u672c\u8a9e')
         #         =>  '\xc6\xfc\xcb\xdc\xb8\xec' (euc-jp string)

engine = tenjin.Engine()
context = { 'name': u'\u65e5\u672c\u8a9e' }  # non-ascii characters
output = engine.render('encoding1.pyhtml', context)
print output,
