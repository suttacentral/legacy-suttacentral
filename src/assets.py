import glob
import json
import logging
import os
import os.path
import webassets
from webassets.script import CommandLineEnvironment

import config

"""Asset (CSS, JavaScript) compilation."""

manifest_path = os.path.join(config.base_dir, 'db', 'webassets', 'manifest')
cache_dir = os.path.join(config.base_dir, 'db', 'webassets', 'cache')
compiled_css_dir = os.path.join(config.static_root, 'css', 'compiled')
compiled_js_dir = os.path.join(config.static_root, 'js', 'compiled')

# For some reason, webassets does not create these directories if
# they do not exist...
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

env = webassets.Environment(config.static_root, '/')
env.auto_build = not config.compile_assets
env.cache = cache_dir
env.debug = not config.compile_assets
env.manifest = 'json:%s' % manifest_path

css_normalize = webassets.Bundle(
    'css/vendor/normalize-2.1.3.css'
)

css_utf8 = webassets.Bundle(
    'css/utf8.css'
)

css_main_free = webassets.Bundle(
    'css/main-free.scss',
    depends='css/*.scss',
    filters='pyscss',
    output='css/compiled/main-free-%(version)s.css'
)

css_main_nonfree = webassets.Bundle(
    'css/main-nonfree.scss',
    depends='css/*.scss',
    filters='pyscss',
    output='css/compiled/main-nonfree-%(version)s.css'
)

css_free = webassets.Bundle(
    css_normalize,
    css_main_free,
    css_utf8,
    filters='cssmin',
    output='css/compiled/free-%(version)s.css'
)

css_nonfree = webassets.Bundle(
    css_normalize,
    css_main_nonfree,
    css_utf8,
    filters='cssmin',
    output='css/compiled/nonfree-%(version)s.css'
)

env.register('css_free', css_free)
env.register('css_nonfree', css_nonfree)

js_core = webassets.Bundle(
    'js/vendor/ZeroClipboard-1.2.3.js',
    'js/easytabs.js',
    'js/nav.js',
    'js/sc_functions.js',
    'js/sc_init.js',
    'js/sc_formatter.js',
    filters='rjsmin',
    output='js/compiled/core-%(version)s.js'
)
env.register('js_core', js_core)

def compile():
    """Compile assets."""
    log = logging.getLogger(__name__)
    cmd = CommandLineEnvironment(env, log)
    cmd.build()

def clean(all=False):
    """Remove outdated compiled assets."""

    maximum_ctime = None
    try:
        maximum_ctime = os.path.getmtime(manifest_path)
        maximum_ctime -= 60 # seconds
    except OSError:
        all = True

    cache_glob = os.path.join(cache_dir, '*')
    css_glob = os.path.join(compiled_css_dir, '*.css')
    js_glob = os.path.join(compiled_js_dir, '*.js')
    paths = glob.glob(cache_glob) + glob.glob(css_glob) + glob.glob(js_glob)
    if all:
        paths += [ manifest_path ]

    for path in paths:
        try:
            if all or os.path.getctime(path) < maximum_ctime:
                os.unlink(path)
        except OSError:
            pass
