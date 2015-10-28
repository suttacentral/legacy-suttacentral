import sys
import threading
from pathlib import Path

from sc.configuration import Config

def check_python_version(min_version):
    actual_version = sys.version_info[:3]
    if actual_version < min_version:
        raise SystemExit('SuttaCentral requires Python >= {min[0]}.{min[1]}.{min[2]}, actual python version is {act[0]}.{act[1]}.{act[2]}'.format(min=min_version, act=actual_version))
    

def reload_constants():
    """Reload runtime constants."""
    config.reload()
    set_contants()


def set_constants():
    """Set runtime constants."""
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = config.data_dir
    db_dir = base_dir / 'db'
    static_dir = base_dir / 'static'

    compiled_css_dir = static_dir / 'css' / 'compiled'
    compiled_js_dir = static_dir / 'js' / 'compiled'
    dict_db_path = db_dir / 'dictionaries.sqlite'
    dict_sources_dir = base_dir / 'dicts'
    exports_dir = static_dir / 'exports'
    global_config_path = config.global_config_path
    local_config_path = config.local_config_path
    table_dir = data_dir / 'table'
    templates_dir = base_dir / 'templates'
    text_dir = data_dir / 'text'
    tmp_dir = base_dir / 'tmp'
    webassets_manifest_path = db_dir / 'webassets' / 'manifest'
    webassets_cache_dir = db_dir / 'webassets' / 'cache'
    indexer_dir = base_dir / 'elasticsearch' / 'indexers'
    
    text_image_source_dir = base_dir / 'text_images'
    text_image_symlink_dir = static_dir / 'text_images'

    # Assign all constants to the module.
    globals().update(locals())

check_python_version(min_version=(3, 5, 0))

config = Config()

set_constants()
