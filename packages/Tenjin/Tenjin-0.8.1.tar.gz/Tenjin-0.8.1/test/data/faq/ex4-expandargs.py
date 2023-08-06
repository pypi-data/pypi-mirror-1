import tenjin
from tenjin.helpers import *
import re

def _expand(code):
    """expand '@var' into '_context.get("var", None)'"""
    return re.sub(r"@(\w+)", r"_context.get('\1', None)", code)

class MyTemplate(tenjin.Template):

    def add_stmt(self, buf, code):
        tenjin.Template.add_stmt(self, buf, _expand(code))

    def add_expr(self, buf, code, flag_escape=None):
        tenjin.Template.add_expr(self, buf, _expand(code), flag_escape)

print("----- script -----")
print(MyTemplate('ex4-expandargs.pyhtml').script)

print("----- result -----")
tenjin.Engine.templateclass = MyTemplate
engine = tenjin.Engine()
html = engine.render('ex4-expandargs.pyhtml')
print(html)
