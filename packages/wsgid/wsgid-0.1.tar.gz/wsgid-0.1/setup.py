
from distutils.core import setup

setup(

    name='wsgid',
    version='0.1',

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



