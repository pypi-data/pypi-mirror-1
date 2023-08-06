
from distutils.core import setup

import wsgid

setup(

    name='wsgid',
    version=wsgid.version,

    description = 'WSGI Server with SSL, code reloading.',
    long_description = wsgid.__doc__,
    url = 'http://bitbucket.org/aafshar/wsgid-main',


    packages=[
        'wsgid',
        'wsgid.servers',
        'wsgid.servers.cherrypy'
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



