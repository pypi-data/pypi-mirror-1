languages = [
  ('en', 'Engilish'),
  ('fr', 'French'),
  ('de', 'German'),
  ('es', 'Spanish'),
  ('ch', 'Chinese'),
  ('ja', 'Japanese'),
]

import urllib
def link_to(label, action=None, id=None):
    buf = ['/app']
    if action: buf.append(action)
    if id: buf.append(id)
    return '<a href="%s">%s</a>' % (urllib.quote('/'.join(buf)), label)
