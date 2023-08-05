import tenjin
engine = tenjin.Engine(escapefunc='cgi.escape', tostrfunc='str')
template = engine.get_template('ex4.pyhtml')
print template.script,
