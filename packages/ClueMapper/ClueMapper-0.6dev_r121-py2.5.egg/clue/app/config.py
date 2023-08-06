import StringIO
import ConfigParser
import md5
import os
from clue.app import utils


class ConfigError(Exception):
    """An error regarding configuration."""


class Config(object):
    """A configuration helper for dealing with ini style files.  Makes
    configuration more dict-like.

      >>> import os
      >>> from clue.tools.testing import gen_tempfile
      >>> tmp = gen_tempfile()
      >>> config = Config(tmp)
      >>> config['foo']['sub1'] = 'bar'
      >>> config.save()

      >>> print config._configdata()
      [foo]
      sub1 = bar

      >>> print config
      <Config sections=foo>

      >>> config.update_from_string('[another]\\nabc=def')
      >>> print config
      <Config sections=foo,another>

      >>> config.save()

    Make sure some of the error handling is in place.

      >>> oldfilename = config.filename
      >>> config.filename = None
      >>> config.save()
      Traceback (most recent call last):
      ConfigError: Cannot save file since filename was never specified
      >>> config.filename = oldfilename

      >>> olddigest = config._digest
      >>> config._digest = None
      >>> config._file_changed
      Traceback (most recent call last):
      ConfigError: Configuration data has not yet been read for ...

      >>> config._digest = olddigest
      >>> f = open(config.filename, 'a')
      >>> f.write('\\n[abc]\\ndef=ghi')
      >>> f.close()
      >>> config.save()
      Traceback (most recent call last):
      ConfigError: Configuration data on the filesystem has changed for ...
      >>> config.load_if_changed()
      True

    Make sure updating is working.

      >>> config.update({'anothersect': {'param1': 'value1'}})
      >>> config['anothersect']
      {'param1': 'value1'}

      >>> print config.pretty_string()
      [another]
      abc = def
      <BLANKLINE>
      [anothersect]
      param1 = value1
      <BLANKLINE>
      [foo]
      sub1 = bar
      <BLANKLINE>
      [abc]
      def = ghi
      <BLANKLINE>
      <BLANKLINE>

    See if the initial config instantiation works.

      >>> tmp2 = gen_tempfile()
      >>> ensure_cm_config(tmp2)
      <ClueMapperConfig projects=; managers=>

    """

    def __init__(self, filename=None):
        self._data = {}
        self._digest = None

        self.filename = filename
        if filename:
            if os.path.exists(filename):
                self.load(empty=True)

    def __getitem__(self, k):
        self.load_if_changed()

        subdict = self._data.get(k, None)
        if subdict is None:
            subdict = self._data[k] = {}
        return subdict

    def _configdata(self):
        f = open(self.filename)
        configdata = f.read().strip()
        f.close()
        return configdata

    def load_if_changed(self):
        if self.filename and self._file_changed:
            self.load(True)
            return True
        return False

    @property
    def _file_changed(self):
        if self._digest is None:
            raise ConfigError('Configuration data has not yet been read '
                              'for %r' % self.filename)
        digested = md5.new(self._configdata()).digest()
        return digested != self._digest

    def load(self, empty=False):
        configdata = self._configdata()
        self._digest = md5.new(configdata).digest()

        parser = ConfigParser.RawConfigParser()
        parser.read([self.filename])

        if empty:
            self._data.clear()

        self.update_from_config_parser(parser)

    def _config_parser(self):
        parser = ConfigParser.RawConfigParser()
        for section, subdict in self._data.items():
            parser.add_section(section)
            for k, v in subdict.items():
                parser.set(section, k, v)
        return parser

    def save(self):
        if not self.filename:
            raise ConfigError('Cannot save file since filename was '
                              'never specified')

        if os.path.exists(self.filename) and self._file_changed:
            raise ConfigError('Configuration data on the filesystem has '
                              'changed for %r, save aborted' % self.filename)
        parser = self._config_parser()
        f = open(self.filename, 'w')
        parser.write(f)
        f.close()

        configdata = self._configdata()
        self._digest = md5.new(configdata).digest()

    def update(self, anotherdict):
        for section, subdict in anotherdict.items():
            if section not in self._data:
                self._data[section] = {}
            d = self._data[section]
            for k, v in subdict.items():
                d[k] = v

    def update_from_string(self, s):
        parser = ConfigParser.RawConfigParser()
        parser.readfp(StringIO.StringIO(s))
        self.update_from_config_parser(parser)

    def update_from_config_parser(self, parser):
        for section in parser.sections():
            subdict = self._data.get(section, None)
            if subdict is None:
                self._data[section] = subdict = {}
            for opt in parser.options(section):
                subdict[opt] = parser.get(section, opt)

    def has_key(self, k):
        self.load_if_changed()
        return k in self._data

    def keys(self):
        self.load_if_changed()
        return self._data.keys()

    def pretty_string(self):
        parser = self._config_parser()
        sio = StringIO.StringIO()
        parser.write(sio)
        return sio.getvalue()

    def __repr__(self):
        s = '<Config sections='
        for x in self._data.keys():
            s += x + ','
        s = s[:-1] + '>'
        return s

    __str__ = __repr__


class ClueMapperConfig(Config):
    """Configuration with helper attributes for ClueMapper.

      >>> config = ClueMapperConfig()
      >>> config['project:myproject']['name'] = 'My Project'
      >>> config['base']['managers'] = 'foo,bar'
      >>> config['bar']['xyz'] = '34'
      >>> config.projects
      [('myproject', {'name': 'My Project'})]

      >>> config
      <ClueMapperConfig projects=myproject; managers=foo,bar>
    """

    @property
    def projects(self):
        prjs = []
        for k, v in self._data.items():
            if k.startswith('project:'):
                prjs.append((k[8:], v))
        return prjs

    @property
    def managers(self):
        mgrs = []
        s = self._data.get('base', {}).get('managers', None)
        if s is not None:
            for x in s.split(','):
                mgrs.append(x.strip())
        return mgrs

    def __repr__(self):
        projects = ','.join([prjid for prjid, p in self.projects])
        managers = ','.join([x for x in self.managers])
        return '<ClueMapperConfig projects=%s; managers=%s>' \
               % (projects, managers)

    __str__ = __repr__


DEFAULT_CM_CONFIG = {
    'base': {
        'svnrepo_base': '',
        'tracenv_base': '',
        'auth_file': '',
        },
    'base:permissions': {
        },
    }


def ensure_cm_config(filename):
    config = ClueMapperConfig(filename)
    if not os.path.exists(filename):
        config.update(DEFAULT_CM_CONFIG)
        config.save()

    return config


def load_config(workingdir):
    pb = utils.PathBuilder(workingdir)
    config = ensure_cm_config(pb(os.path.join('etc', 'cluemapper.ini')))
    changed = False
    if not config['base'].get('svnrepo_base', None):
        config['base']['svnrepo_base'] = pb(os.path.join('var', 'svnrepos'))
        changed = True
    if not config['base'].get('tracenv_base', None):
        config['base']['tracenv_base'] = pb(os.path.join('var', 'tracenvs'))
        changed = True
    if not config['base'].get('auth_file', None):
        rel = os.path.join('etc', 'cluemapper.passwd')
        af = config['base']['auth_file'] = pb(rel)
        changed = True
        if not os.path.exists(af):
            f = open(af, 'w')
            f.close()
    if changed:
        config.save()
    return config
