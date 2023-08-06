import tenjin, re
from tenjin.helpers import *

class MyTemplate(tenjin.Template):

    ## '[|expr|]' escapes HTML and '[:expr:]' doesn't
    EXPR_PATTERN = re.compile('\[(\|(.*?)\||:(.*?):)\]', re.S);

    ## return pattern object for embedded expressions
    def expr_pattern(self):
        return MyTemplate.EXPR_PATTERN

    ## return expression string and flag whether escape or not from matched object
    def get_expr_and_escapeflag(self, match):
        expr = match.group(2) or match.group(3)
	escapeflag = match.group(2) and True or False
	return expr, escapeflag

if __name__ == '__main__':
    context = {'value': 'AAA&BBB'}
    engine = tenjin.Engine(templateclass=MyTemplate)
    output = engine.render('ex8-expr-pattern.pyhtml', context)
    print output,
