
from distutils.core import setup

import wsgid

setup(

    name='wsgid',
    version=wsgid.version,

    long_description = wsgid.__doc__,

    packages=[
        'wsgid',
    ],

    author='Ali Afshar',
    author_email='aafshar@gmail.com',

    scripts={
        'bin/wsgid': 'wsgid'
    },

    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server'
    ]
)



