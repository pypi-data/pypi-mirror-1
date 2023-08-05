# -*- python -*-
from distutils.core import setup
setup( name='egd',
       version='1.0',
       py_modules=['egd'],
       author='Deron Meranda',
       author_email='deron.meranda@gmail.com',
       url='http://deron.meranda.us/python/egd/',
       download_url='http://deron.meranda.us/python/egd/dist/egd-1.0.tar.gz',
       description='Client to get random numbers from an EGD (entropy gathering daemon) source.',
       long_description="""This module provides a simple implementation of a client-side interface
to the EGD (entropy gathering daemon) protocol for obtaining cryptographically
strong pseudo-random numbers on Unix-like systems that do not natively
support a /dev/random device.  Requires Python 2.4; probably not suitable for
Python 3.x at this point.  Also works with EGD-compatible entropy sources such
as prngd.""",
       license='Public Domain',
       keywords=['egd','prngd','random'],
       platforms=['Unix'],
       classifiers=['Development Status :: 6 - Mature',
                    'Intended Audience :: Developers',
                    'License :: Public Domain',
                    'Operating System :: Unix',
                    'Programming Language :: Python',
                    'Topic :: Security :: Cryptography',
                    'Topic :: Software Development :: Libraries :: Python Modules'
                    ]
       )

