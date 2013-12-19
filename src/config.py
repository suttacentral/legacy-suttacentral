import os, sys
import cherrypy

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
        ['app', 'dbr_cache_file'],
        ['app', 'exports_root'],
        ['app', 'processed_root'],
        ['app', 'static_root'],
        ['app', 'templates_root'],
        ['app', 'text_root'],
        ['app', 'data'],
        ['sqlite', 'db'],
        ['dict', 'db'],
        ['dict', 'sources'],
        ['textsearch', 'dbpath'],
    ]

    base_dir         = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    source_dir       = os.path.join(base_dir, 'src')
    global_conf_path = os.path.join(base_dir, 'global.conf')
    local_conf_path  = os.path.join(base_dir, 'local.conf')

    def reload(self):
        """Reload the configuration."""
        self.clear()
        self.__setup()

    def __init__(self):
        dict.__init__(self)
        # Manually copy these two function references because they seem to
        # disappear after the module is loaded...!
        self.__as_dict = cherrypy.lib.reprconf.as_dict
        self.__join = os.path.join
        self.__setup()

    def __getattr__(self, name):
        if 'app' in self and name in self['app']:
            return self['app'][name]
        elif name in self:
            return self[name]
        else:
            raise AttributeError("Config has no attribute '%s'" % name)

    def __setup(self):
        config = self.__as_dict(self.global_conf_path)
        try:
            local_config = self.__as_dict(self.local_conf_path)
            self.__deep_update(config, local_config)
        except IOError:
            pass
        self.update(config)

        for key, subkey in self.ABSOLUTE_PATHS:
            self.__absolutize(key, subkey)

        # Manually set tools.staticdir.root from static_root
        if '/' not in self:
            self['/'] = {}
        self['/']['tools.staticdir.root'] = self.static_root

        # Absolutize any relative filename paths for cherrypy.
        for key, subdict in self.items():
            if key[0] == '/':
                subkey = 'tools.staticfile.filename'
                if subkey in subdict:
                    self.__absolutize(key, subkey, self.static_root)
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
                    if base is None:
                        base = self.base_dir
                    self[key][subkey] = self.__join(base, path)

__config = Config()

# Add the configuration files to trigger autoreload.
cherrypy.engine.autoreload.files.add(__config.global_conf_path)
cherrypy.engine.autoreload.files.add(__config.local_conf_path)

# We manually add this file because cherrypy autoreloader doesn't recognize
# it, probably because of the module munging.
cherrypy.engine.autoreload.files.add(os.path.realpath(__file__))

# Do not use autoreloader against plumbum
cherrypy.engine.autoreload.match = r'^(?!plumbum).+'

# See http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
sys.modules[__name__] = __config
