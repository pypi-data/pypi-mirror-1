
"""
sensible config
~~~~~~~~~~~~~~~

So you have some configuration variables, and you want them to be available to
be in any number of ini-like files, as well as overridable from the environment,
and overridable from the command line. Define once, and use.

Our basic example::

    from config import Config, Option

    options = [
        Option('debug', 'Run in debug mode', False,
               short_name='d', converter=bool, action='store_true'),
    ]

    conf = Config(options)

    # Will start as the default value
    assert conf.debug == False
"""

import os, optparse, ConfigParser, pprint


class Option(object):

    def __init__(self, name, help, default, short_name=None, converter=unicode,
                       **optparse_kw):
        self.name = name
        if short_name is None:
            short_name = self.name[0]
        self.short_name = short_name
        self.help = help
        self.default = default
        self.converter = converter
        self.optparse_kw = optparse_kw

    @property
    def long_opt(self):
        return '--%s' % self.name

    @property
    def short_opt(self):
        return '-%s' % self.short_name


class ConfigFile(ConfigParser.ConfigParser):
    """Flat config parser"""

    def __init__(self, path):
        ConfigParser.ConfigParser.__init__(self)
        self.read(path)
        options = {}
        for section in self.sections():
            for name in self.options(section):
                options[name] = self.get(section, name)
        self.flat_options = options


class Config(object):

    def __init__(self, options, env_prefix=None):
        self._env_prefix = env_prefix
        self._parser = optparse.OptionParser()
        self._options = {}
        for opt in options:
            self.add_option(opt)

    def add_option(self, opt):
        self._options[opt.name] = opt
        self._parser.add_option(opt.short_opt, opt.long_opt,
                                help=opt.help, **opt.optparse_kw)
        setattr(self, opt.name, opt.default)

    def add_from_env(self, env=os.environ):
        for name, opt in self._options.items():
            if self._env_prefix:
                env_name = '%s_%s' % (self._env_prefix, name.upper())
            else:
                env_name = name.upper()
            raw = env.get(env_name)
            if raw:
                val = opt.converter(raw)
                setattr(self, name, val)

    def add_from_file(self, path):
        file = ConfigFile(path)
        for name, opt in file.flat_options.items():
            if name in self._options:
                val = self._options[name].converter(opt)
                setattr(self, name, val)

    def add_from_argv(self, argv):
        opts, args = self._parser.parse_args(argv)

        for name, opt in self._options.items():
            raw = getattr(opts, name, None)
            if raw:
                val = opt.converter(raw)
                setattr(self, name, val)

    def items(self):
        for name in self._options:
            yield name, getattr(self, name)


