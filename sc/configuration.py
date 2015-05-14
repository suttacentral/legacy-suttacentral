import cherrypy
import copy
import sys
from cherrypy.lib.reprconf import as_dict
from pathlib import Path


class Config(dict):
    """A flexible and convenient configuration class for SuttaCentral.

    To use it, add an entry in global.conf under the [app] section:

        [app]
            level: 123

    Then, you can access it as follows:

        >>> import config
        >>> config.level
        123

    Any entries specified in local.conf will override those entries in
    global.conf. This allows a local configuration to specify settings
    without having those settings be put into the global code repository.

    You can add any Python value, including arrays and dictionaries:

        [app]
            spain: {'color': 'purple'}

        >>> config.spain
        {'color': 'purple'}

    Dictionaries can also be added to the top-level and accessed easily:

        [brazil]
            color: 'green'
            sport: 'football'

        >>> config.brazil
        {'color': 'green', 'sport': 'football'}

    More explicitly, Config's magic getattr looks for entries under 'app',
    and if can't find it there, it then looks in the top-level.

    The config object is a regular Python dict. You can still access entries
    using the [] method:

        >>> config['app']['level']
        123
        >>> config['brazil']['a']
        1

    Entries listed under ABSOLUTE_PATHS will be automatically converted into
    absolute paths (e.g., required by cherrypy).

    The config object itself is intended to be fed directly into cherrypy. See
    server.py.
    """

    ABSOLUTE_PATHS = [
        ['global', 'log.access_file'],
        ['global', 'log.error_file'],
        ['app', 'app_log_file'],
        ['app', 'data_dir'],
    ]

    _base_dir = Path(__file__).resolve().parents[1]
    _static_dir = _base_dir / 'static'
    global_config_path = _base_dir / 'global.conf'
    local_config_path = _base_dir / 'local.conf'
    test_samples_dir = _base_dir / 'tests' / 'samples'
    log_dir = _base_dir / 'log'

    def reload(self):
        """Reload the configuration."""
        self.clear()
        self.__setup()

    def for_cherrypy(self):
        """Return a copy of this dictionary suitable for cherrypy.

        This will stringify any pathlib.Paths as cherrypy does not play
        nicely with such objects.
        """
        result = copy.deepcopy(self)
        def stringify(dct):
            for key, value in dct.items():
                if isinstance(value, Path):
                    dct[key] = str(value)
                elif isinstance(value, dict):
                    stringify(value)
        stringify(result)
        return result

    def __init__(self):
        dict.__init__(self)
        self.__setup()

    def __getattr__(self, name):
        if 'app' in self and name in self['app']:
            return self['app'][name]
        elif name in self:
            return self[name]
        else:
            raise AttributeError("Config has no attribute '%s'" % name)

    def __setup(self):
        config = as_dict(str(self.global_config_path))
        try:
            local_config = as_dict(str(self.local_config_path))
            self.__deep_update(config, local_config)
        except IOError:
            pass
        self.update(config)

        for key, subkey in self.ABSOLUTE_PATHS:
            self.__absolutize(key, subkey, self._base_dir)

        # Manually set tools.staticdir.root from static_dir
        if '/' not in self:
            self['/'] = {}
        self['/']['tools.staticdir.root'] = self._static_dir

        # Absolutize any relative filename paths for cherrypy.
        for key, subdict in self.items():
            if key[0] == '/':
                subkey = 'tools.staticfile.filename'
                if subkey in subdict:
                    self.__absolutize(key, subkey, self._static_dir)
        return config

    def __deep_update(self, a, b):
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(b[k], dict):
                self.__deep_update(a[k], b[k])
            else:
                a[k] = v
        return a

    def __absolutize(self, key, subkey, base=None):
        if key in self:
            if subkey in self[key]:
                path = self[key][subkey]
                if path[0] != '/':
                    self[key][subkey] = base / path
