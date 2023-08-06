## import all helper methods
import tenjin
from tenjin.helpers import *
## render with preprocessing
engine = tenjin.Engine(preprocess=True)
print '***** preprocessed *****'
print engine.get_template('weekday1.pyhtml').script,
print '***** output *****'
print engine.render('weekday1.pyhtml'),
