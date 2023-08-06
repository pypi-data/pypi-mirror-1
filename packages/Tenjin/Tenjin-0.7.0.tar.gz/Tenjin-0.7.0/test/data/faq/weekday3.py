## helper function
WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
def pp_select_weekday_tag(expr_str, name='weekday', indent=''):
    buf = []
    buf.append('<select name="%s">' % name)
    attr = 'selected="selected"'
    buf.append('%s<?py _selected = { str(%s): \' %s\' } ?>' % \
                      (indent, expr_str, attr))
    buf.append('  <option>-</option>')
    i = 0
    for wday in WEEKDAYS:
        i += 1
	expr = '_selected.get("%s")' % i
	buf.append('  <option value="%s"#{%s}>%s</option>' % \
                      (i, expr, wday))
    buf.append('</select>')
    return "\n".join(buf)

## import all helper methods
import tenjin
from tenjin.helpers import *

## 
engine = tenjin.Engine(preprocess=True)
context = { 'params': { 'weekday': 3, 'day': 19 } }
print '***** preprocessed *****'
print engine.get_template('weekday3.pyhtml').script,
print '***** output *****'
print engine.render('weekday3.pyhtml', context),
