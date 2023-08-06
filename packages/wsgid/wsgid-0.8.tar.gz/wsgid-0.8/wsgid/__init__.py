"""
wsgid
~~~~~

A backgrounding front-end over cherrypy (builtin), twisted.web, circuits,
spawning, fapws3, and werkzeug, With server-independent support for code
reloading and pid file management.

Examples
========

Run a server in the foreground after importing `mywebapp.app` as the application
instance::

    wsgid --application mywebapp.app

Run a server in the foreground after importing and calling `mywebapp.create_app`
as the application factory::

    wsgid --application_factory mywebapp.create_app

Run a server using the pidfile `mypid.pid` after importing and
calling `mywebapp.create_app` as the application factory::

    wsgid --application_factory mywebapp.create_app --pidfile mypid.pid

Stop a server using the pidfile `mypid.pid`::

    wsgid --pidfile mypid.pid --stop

Use twisted.web's server to display builtin hello-world::

    wsgid --server=twistedweb

All these options have short versions, and can override defaults in config
files or the environment.


Using config files
==================

Ini-style config files can be used to provide any of the options available. For
example, myserver.ini::

    [ config ]

    pidfile = mypid.pid
    application_factory = mywebapp.crate_app

And then::

    wsgid -c myserver.ini

Is equivalent to the above examples. Note that the actual section titles in the
config file are ignored, and the file is essentially flattened.


Using the environment
=====================

Additionally any config variable can be overriden using the environment
variables. The variable name is uppercased, and prefixed with `WSGID_` to avoid
collisions with other apps for common names. For example::

    export WSGID_PIDFILE=mypid.pid

Is equivalent to passing the `--pidfile` on the command line.


Using the Werkzeug Debugger
===========================

Passing the option -d/--debug will wrap your WSGI application in the Werkzeug
debugger. It is not recommended to do this in production::

    wsgid --application mywebapp.app --foreground --debug


Using SSL
=========

The default CherryPy backend supports SSL, and this is enabled using the two
options --ssl_certificate/-C with --ssl_private_key/-K, To generate these as
an example::

    openssl genrsa 1024 > host.key
    openssl req -new -x509 -nodes -sha1 -days 365 -key host.key > host.cert

Then you can run your server like::

    wsgid --application mywebapp.app --foreground --ssl_certificate=host.cert --ssl_private_key=host.key




Complete options
================
Usage: wsgid [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file=CONFIG_FILE
                        The configuration file
  -p PIDFILE, --pidfile=PIDFILE
                        The PID file
  -s, --stop            Stop the server.
  -a APPLICATION, --application=APPLICATION
                        The WSGI Applciation instance to import
  -A APPLICATION_FACTORY, --application_factory=APPLICATION_FACTORY
                        The WSGI Applciation factory to import
  -d, --debug           Run in the werkzeug debugger.
  -P PORT, --port=PORT  The port to listen on.
  -H HOST, --host=HOST  The host to listen on.
  -N, --no_reloader     Do not use the reloader.
  -L LOGDIR, --logdir=LOGDIR
                        The directory for logs.
  -w WORKDIR, --workdir=WORKDIR
                        The working directory for the daemon.
  -n SERVERNAME, --servername=SERVERNAME
                        The server name
  -C SSL_CERTIFICATE, --ssl_certificate=SSL_CERTIFICATE
                        The ssl certificate
  -K SSL_PRIVATE_KEY, --ssl_private_key=SSL_PRIVATE_KEY
                        The ssl private key
  -e VIRTUALENV, --virtualenv=VIRTUALENV
                        Path to a virtualenv to use
  -v, --verbose         Verbose logging
  -T, --no_log_stdout   Do not log on stdout
  -O SERVER, --server=SERVER
                        Server type to use, can be:
                            cherrypy (default)
                            twistedweb
                            circuitsweb
                            fapws3
                            spawningweb
                            wz



Developer Information
=====================

Repository/tracker/wiki/etc at:

    http://bitbucket.org/aafshar/wsgid-main/

Latest tip package:

    http://bitbucket.org/aafshar/wsgid-main/get/tip.zip#egg=wsgid-dev
"""

version = '0.8'

