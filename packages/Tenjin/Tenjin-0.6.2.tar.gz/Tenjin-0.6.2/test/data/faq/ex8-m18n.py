# -*- coding: utf-8 -*-
import tenjin
from tenjin.helpers import *
import re

##
## message catalog to translate message
##
MESSAGE_CATALOG = {
    'en': { 'Hello': 'Hello',
            'Good bye': 'Good bye', },
    'fr': { 'Hello': 'Bonjour',
            'Good bye': 'Au revoir', },
    }


##
## engine class which supports M17N
##
class M17NEngine(tenjin.Engine):

    lang = 'en'     # default language name

    ## __ini__() takes 'lang' argument
    def __init__(self, *args, **kwargs):
        lang = kwargs.has_key('lang') and kwargs.pop('lang') or None
        tenjin.Engine.__init__(self, *args, **kwargs)
        if lang: self.lang = lang     # set language name

    ## change cache filename to 'file.html.lang.cache'
    def cachename(self, filename):
        return "%s.%s.cache" % (filename, self.lang)

    ## translate message according to self.lang
    def translate(self, message_key):
        message_dict = MESSAGE_CATALOG.get(self.lang)
        if not message_dict:
            return message_key
        return message_dict.get(message_key, message_key)

    ## set self.translate() to context['_']
    def hook_context(self, context):
        tenjin.Engine.hook_context(self, context)
        context['_'] = self.translate


##
## test program
##
if __name__ == '__main__':

    template_name = 'ex8-m18n.pyhtml'
    context = { 'username': 'World' }
    
    ## engine for english
    engine = M17NEngine(preprocess=True, cache=None)
    output = engine.render(template_name, context)
    print "--- lang: %s ---" %  engine.lang
    print output
    
    ## engine for French
    engine = M17NEngine(preprocess=True, cache=None, lang='fr')
    output = engine.render(template_name, context)
    print "--- lang: %s ---" %  engine.lang
    print output
