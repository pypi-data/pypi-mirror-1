======
README
======

Release: 0.6.2
copyright(c) 2007-2008 kuwata-lab.com all rights reserved.


About
-----

pyTenjin is a very fast and full-featured template engine based on embedded Python.
You can embed Python statements and expressions into your text file.
pyTenjin converts it into Python program and evaluate it.


Features
--------

* Very fast (three times faster than Cheetah, nine times faster than Djano).
* Lightweight (only one file which contains about 1000 lines)
* Not break HTML design because it uses XML Processing
  Instructions (PI) as embedded notation for Python statements.
* Secure because it supports escaping expression value by default.
* Auto caching of converted Python code.
* Nestable layout template
* Inlucde other templates
* Capture part of template
* Load YAML file as context data
* Preprocessing support

See 'doc/*.html' for details.


Install
-------

1. Just type 'python setup.py install' with administrator or root user,
   or copy 'lib/tenjin.py' and 'bin/pytenjin' into proper directory.
2. (Optional) Install `PyYAML <http://pyyaml.org>`_.


Attention
---------

pyTenjin is beta released. It means that API or specification may change
in the future.


License
-------

MIT License.
