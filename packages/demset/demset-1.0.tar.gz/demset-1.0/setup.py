# -*- python -*-
from distutils.core import setup
setup( name='demset',
       version='1.0',
       py_modules=['demset'],
       author='Deron Meranda',
       author_email='deron.meranda@gmail.com',
       url='http://deron.meranda.us/python/demset/',
       download_url='http://deron.meranda.us/python/demset/dist/demset-1.0.tar.gz',
       description='set and frozenset classes for Python 2.2 and 2.3 compatible with Python 2.4 builtin types',
       long_description="""This module provides an implementation of the 'set' and 'frozenset' types which
        were introduced in Python 2.4, but which work under older versions (Python 2.2
        or 2.3).  It is a standalone module written entirely in Python, and can easily
        be used as a substitute for the built-in types when runing under older Pythons.
        Care was taken to try to provide nearly 100% compatibility with Python 2.4's
        behavior.""",
       license='Python',
       keywords=['set','frozenset'],
       platforms=[],
       classifiers=['Development Status :: 6 - Mature',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: Python Software Foundation License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries :: Python Modules'
                    ]
       )

