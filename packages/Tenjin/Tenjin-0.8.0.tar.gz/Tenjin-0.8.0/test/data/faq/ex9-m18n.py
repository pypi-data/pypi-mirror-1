# -*- coding: utf-8 -*-
import tenjin
from tenjin.helpers import *
import re

##
## message catalog to translate message
##
MESSAGE_CATALOG = {
    'en': { 'Hello': 'Hello',
            'Good bye': 'Good bye',
	  },
    'fr': { 'Hello': 'Bonjour',
            'Good bye': 'Au revoir',
	  },
}

##
## create translation function and return it.
## ex.
##    _ = create_translation_func('fr')
##    print _('Hello')   #=> 'Bonjour'
##
def create_translation_func(lang):
    dict = MESSAGE_CATALOG.get(lang)
    if not dict:
        raise ValueError("%s: unknown lang." % lang)
    def func(message_key):
        return dict.get(message_key)
    return func
    
##
## cache storage class to cache template object for each language
##
class M17nCacheStorage(tenjin.MarshalCacheStorage):

    lang = 'en'       # default language

    def __init__(self, *args, **kwargs):
        if 'lang' in kwargs:
	    lang = kwargs.pop('lang')
	    if lang: 
	        self.lang = lang
	tenjin.MarshalCacheStorage.__init__(self, *args, **kwargs)

    ## change cache filename to 'file.pyhtml.lang.cache'
    def _cachename(self, fullpath):
        return "%s.%s.cache" % (fullpath, self.lang)

##
## test program
##
if __name__ == '__main__':

    template_name = 'ex9-m18n.pyhtml'
    common_context = { 'username': 'World' }

    ## create cache storage and engine for English
    m17ncache = M17nCacheStorage(lang='en')
    engine = tenjin.Engine(preprocess=True, cache=m17ncache)

    ## render html for English
    context = common_context.copy()
    context['_'] = create_translation_func('en')
    html = engine.render(template_name, context)
    print("--- lang: en ---")
    print(html)
    
    ## create cache storage and engine for French
    m17ncache = M17nCacheStorage(lang='fr')
    engine = tenjin.Engine(preprocess=True, cache=m17ncache)

    ## render html for French
    context = common_context.copy()
    context['_'] = create_translation_func('fr')
    html = engine.render(template_name, context)
    print("--- lang: fr ---")
    print(html)
