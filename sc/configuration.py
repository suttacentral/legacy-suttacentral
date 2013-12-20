import cherrypy
import copy
import sys
from cherrypy.lib.reprconf import as_dict
from pathlib import Path

_file_path = Path(__file__).resolve()

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

    base_dir          = _file_path.parents[1]
    global_conf_path  = base_dir / 'global.conf'
    local_conf_path   = base_dir / 'local.conf'

    static_dir        = base_dir / 'static'
    templates_dir     = base_dir / 'templates'
    exports_dir       = static_dir / 'exports'
    tmp_dir           = base_dir / 'tmp'

    db_dir            = base_dir / 'db'
    dict_db_path      = db_dir / 'dictionaries.sqlite'
    dict_sources_dir  = base_dir / 'dicts'

    webassets_manifest_path = db_dir / 'webassets' / 'manifest'
    webassets_cache_dir = db_dir / 'webassets' / 'cache'
    compiled_css_dir  = static_dir / 'css' / 'compiled'
    compiled_js_dir   = static_dir / 'js' / 'compiled'

    @property
    def table_dir(self):
        return self.data_dir / 'table'

    @property
    def text_dir(self):
        return self.data_dir / 'text'

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
        config = as_dict(str(self.global_conf_path))
        try:
            local_config = as_dict(str(self.local_conf_path))
            self.__deep_update(config, local_config)
        except IOError:
            pass
        self.update(config)

        for key, subkey in self.ABSOLUTE_PATHS:
            self.__absolutize(key, subkey, self.base_dir)

        # Manually set tools.staticdir.root from static_dir
        if '/' not in self:
            self['/'] = {}
        self['/']['tools.staticdir.root'] = self.static_dir

        # Absolutize any relative filename paths for cherrypy.
        for key, subdict in self.items():
            if key[0] == '/':
                subkey = 'tools.staticfile.filename'
                if subkey in subdict:
                    self.__absolutize(key, subkey, self.static_dir)
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

# Add the configuration files to trigger autoreload.
cherrypy.engine.autoreload.files.add(str(Config.global_conf_path))
cherrypy.engine.autoreload.files.add(str(Config.local_conf_path))

# Do not use autoreloader against plumbum
cherrypy.engine.autoreload.match = r'^(?!plumbum).+'
