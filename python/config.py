import os, sys
import cherrypy

class Config:

    base_dir         = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    source_dir       = os.path.join(base_dir, 'python')
    global_conf_path = os.path.join(base_dir, 'global.conf')
    local_conf_path  = os.path.join(base_dir, 'local.conf')

    ABSOLUTIZE_KEYS = [
        ['global', 'access_file'],
        ['global', 'error_file'],
        ['app', 'app_log_file'],
        ['app', 'dbr_cache_file'],
        ['app', 'static_root'],
        ['app', 'templates_root'],
        ['app', 'text_root'],
        ['sqlite', 'db'],
    ]

    def __init__(self):
        self.__setup()

    def __getattr__(self, name):
        if name in self.config['app']:
            return self.config['app'][name]
        elif name in self.config:
            return self.config[name]
        else:
            raise AttributeError("Config has no attribute '%s'" % name)

    def __setup(self):
        self.config = cherrypy.lib.reprconf.as_dict(self.global_conf_path)
        try:
            local_config = cherrypy.lib.reprconf.as_dict(self.local_conf_path)
            self.__deep_update(self.config, local_config)
        except IOError:
            pass

        for key, subkey in self.ABSOLUTIZE_KEYS:
            self.__absolutize(key, subkey)

        # Manually set tools.staticdir.root from static_root
        if '/' not in self.config:
            self.config['/'] = {}
        self.config['/']['tools.staticdir.root'] = self.static_root

        # Absolutize any relative filename paths for cherrypy.
        for key, subdict in self.config.items():
            if key[0] == '/':
                subkey = 'tools.staticfile.filename'
                if subkey in subdict:
                    self.__absolutize(key, subkey, self.static_root)

    def __deep_update(self, a, b):
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(b[k], dict):
                self.__deep_update(a[k], b[k])
            else:
                a[k] = v
        return a

    def __absolutize(self, key, subkey, base=None):
        if key in self.config:
            if subkey in self.config[key]:
                path = self.config[key][subkey]
                if path[0] != '/':
                    if base is None:
                        base = self.base_dir
                    self.config[key][subkey] = os.path.join(base, path)

# See http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
sys.modules[__name__] = Config()
