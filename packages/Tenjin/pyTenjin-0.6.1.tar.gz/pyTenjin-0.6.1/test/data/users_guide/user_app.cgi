#!/usr/bin/env python

## set action ('create' or 'edit')
import sys, os, cgi
action = None
form = None
if os.getenv('REQUEST_METHOD'):
    form = cgi.FieldStorage()
    action = form.getFirst('action')
elif len(sys.argv) >= 2:
    action = sys.argv[1]
if action is None or action not in ['create', 'edit']:
    action = 'create'

## set context data
if action == 'create':
    title = 'Create User'
    params = {'name': None, 'email': None, 'gender': None}
else:
    title = 'Edit User'
    params = {'name': 'Margalette',
              'email': 'meg@example.com',
	      'gender': 'f',
	      'id': 123 }
context = {'title': title, 'params': params}

## create engine object
import tenjin
from tenjin.helpers import *
from tenjin.helpers.html import *
layout = ':layout'   # or 'user_layout.pyhtml'
engine = tenjin.Engine(prefix='user_', postfix='.pyhtml', layout=layout)

## evaluate template
template_name = ':' + action   # ':create' or ':edit'
output = engine.render(template_name, context)
if form:
    print "Content-Type: text/html\r\n\r\n",
print output,
