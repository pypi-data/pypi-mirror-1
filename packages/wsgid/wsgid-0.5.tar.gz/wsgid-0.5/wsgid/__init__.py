"""
wsgid
~~~~~

A backgrounding front-end over cherrypy (and potentially other web servers),
with support for code reloading.

Examples
========

Run a server in the foreground after importing `mywebapp.app` as the application
instance::

    wsgid --application mywebapp.app --foreground

Run a server in the foreground after importing and calling `mywebapp.create_app`
as the application factory::

    wsgid --application_factory mywebapp.create_app -f

Run a daemonized server using the pidfile `mypid.pid` after importing and
calling `mywebapp.create_app` as the application factory::

    wsgid --application_factory mywebapp.create_app --pidfile mypid.pid

Stop a daemonized server using the pidfile `mypid.pid`::

    wsgid --pidfile mypid.pid --stop

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


Complete options
================

Usage: wsgid [options]

Options:
  -h, --help            show this help message and exit

  -c CONFIG_FILE, --config_file=CONFIG_FILE
                        The configuration file

  -p PIDFILE, --pidfile=PIDFILE
                        The PID file

  -f, --foreground      Run the server in the foreground

  -s, --stop            Stop the server.

  -a APPLICATION, --application=APPLICATION
                        The WSGI Applciation instance to import

  -A APPLICATION_FACTORY, --application_factory=APPLICATION_FACTORY
                        The WSGI Applciation factory to import

  -d, --debug           Run in debug mode.

  -P PORT, --port=PORT  The port to listen on.

  -H HOST, --host=HOST  The host to listen on.

  -L LOGDIR, --logdir=LOGDIR
                        The directory for logs.

  -R STDREDIRECT, --stdredirect=STDREDIRECT
                        The file to redirect stdio to.

  -w WORKDIR, --workdir=WORKDIR
                        The working directory for the daemon.

  -U UMASK, --umask=UMASK
                        The umask for the spawned child.

  -n SERVERNAME, --servername=SERVERNAME
                        The server name

  -r, --reloader        Use the code reloader

Developer Information
=====================

Repository/tracker/wiki/etc at:

    http://bitbucket.org/aafshar/wsgid-main/

Latest tip package:

    http://bitbucket.org/aafshar/wsgid-main/get/tip.zip#egg=wsgid-dev
"""

version = '0.5'

