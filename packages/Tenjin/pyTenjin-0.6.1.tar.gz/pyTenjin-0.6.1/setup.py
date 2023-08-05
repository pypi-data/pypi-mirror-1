###
### $Rev: 132 $
### $Release: 0.6.1 $
### copyright(c) 2007 kuwata-lab.com all rights reserved.
###


import sys, re
if len(sys.argv) > 1 and sys.argv[1] == 'egg_info':
    from ez_setup import use_setuptools
    use_setuptools()
from distutils.core import setup

name     = 'pyTenjin'
version  = '0.6.1'
author   = 'makoto kuwata'
email    = 'kwa@kuwata-lab.com'
maintainer = author
maintainer_email = email
url      = 'http://www.kuwata-lab.com/tenjin/'
desc     = 'a fast and full-featured template engine based on embedded Python'
detail   = (
           'pyTenjin is a very fast and full-featured template engine.\n'
           'You can embed Python statements and expressions into your text file.\n'
           'pyTenjin converts it into Python program and evaluate it.\n'
           'In addition to high-performance, pyTenjin has many useful features\n'
	   'such as layout template, partial template, capturing, preprocessing, and so on.\n'
           )
license  = 'MIT License'
platforms = 'any'
download = 'http://downloads.sourceforge.net/tenjin/pyTenjin-%s.tar.gz' % version
#download = 'http://jaist.dl.sourceforge.net/sourceforge/tenjin/pyTenjin-%s.tar.gz' % version
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console'
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


setup(
    name=name,
    version=version,
    author=author,  author_email=email,
    maintainer=maintainer, maintainer_email=maintainer_email,
    description=desc,  long_description=detail,
    url=url,  download_url=download,  classifiers=classifiers,
    #license=license,  platforms=platforms,
    #
    py_modules=['tenjin'],
    package_dir={'': 'lib'},
    scripts=['bin/pytenjin'],
    #packages=['tenjin'],
    zip_safe = False,
)
