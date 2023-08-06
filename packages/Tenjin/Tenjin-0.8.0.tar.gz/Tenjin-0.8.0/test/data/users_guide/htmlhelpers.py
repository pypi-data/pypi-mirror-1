class Item(object):
  def __init__(self, id, name, readonly=False):
    self.id = id
    self.name = name
    self.readonly = readonly
items = [ Item(1, 'Foo'), Item(2, 'Bar', True) ]
params = {'item_id': 2}
import tenjin
from tenjin.helpers import *
from tenjin.helpers.html import *
engine = tenjin.Engine()
html = engine.render('htmlhelpers.pyhtml', {'items': items, 'params': params})
import sys
sys.stdout.write(html)
