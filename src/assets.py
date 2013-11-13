import config, logging, os, webassets
from webassets.script import CommandLineEnvironment

"""Asset (CSS, JavaScript) compilation."""

cache_dir = os.path.join(config.base_dir, 'tmp', 'webassets-cache')
manifest_path = os.path.join(config.base_dir, 'tmp', 'webassets-manifest')
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
    filters='cssmin',
    output='css/compiled/free-%(version)s.css'
)

css_nonfree = webassets.Bundle(
    css_normalize,
    css_main_nonfree,
    filters='cssmin',
    output='css/compiled/nonfree-%(version)s.css'
)

env.register('css_free', css_free)
env.register('css_nonfree', css_nonfree)

js_core = webassets.Bundle(
    'js/easytabs.js',
    'js/nav.js',
    'js/sc_functions.js',
    'js/sc_init.js',
    'js/sc_formatter.js',
    filters='rjsmin',
    output='js/compiled/core-%(version)s.js'
)
env.register('js_core', js_core)

def build():
    log = logging.getLogger(__name__)
    cmd = CommandLineEnvironment(env, log)
    cmd.build()
