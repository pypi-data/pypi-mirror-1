#!/usr/bin/env python

from distutils.core import setup
import py2exe
from wxdebuglib import meta

setupOptions = { 
    'windows': ['wxdebug.py'],
    'name' : meta.filename,
    'author' : meta.author,
    'author_email' : meta.author_email,
    'description' : meta.description,
    'version' : meta.version,
    'url' : meta.url,
    'license' : meta.license,
    'packages' : ['wxdebuglib'] + 
        ['wxdebuglib.' + subpackage for subpackage in ('gui', 'patterns')],
    'scripts' : ['wxdebug.py', 'wxdebug.pyw'],
    'classifiers' : [\
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: PHP',
        'Topic :: Software Development :: Debuggers'],
}

if __name__ == '__main__':
    setup(**setupOptions)
