## import all helper methods
import tenjin
from tenjin.helpers import *
## render with preprocessing
engine = tenjin.Engine(preprocess=True)
context = { 'params': { 'weekday': 3, 'day': 19 } }
print '***** preprocessed *****'
print engine.get_template('weekday2.pyhtml').script,
print '***** output *****'
print engine.render('weekday2.pyhtml', context),
