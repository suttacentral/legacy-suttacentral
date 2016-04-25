"""Asset (CSS, JavaScript) compilation using webassets.

See: http://webassets.readthedocs.org/
"""

import logging
import webassets
from webassets.script import CommandLineEnvironment

import sc
from sc import config

logger = logging.getLogger(__name__)


def clean(older=False):
    """Remove outdated compiled assets."""

    maximum_ctime = 86400
    try:
        maximum_ctime = sc.webassets_manifest_path.stat().st_mtime
        maximum_ctime -= 86400  # seconds
    except OSError:
        older = True

    cache_glob = sc.webassets_cache_dir.glob('*')
    css_glob = sc.compiled_css_dir.glob('*.css')
    js_glob = sc.compiled_js_dir.glob('*.js')
    paths = list(cache_glob) + list(css_glob) + list(js_glob)

    if not older:
        paths.append(sc.webassets_manifest_path)

    for path in paths:
        try:
            if not older or path.stat().st_ctime < maximum_ctime:
                path.unlink()
        except OSError:
            pass


def compile():
    """Compile assets."""

    log = logging.getLogger(__name__)
    cmd = CommandLineEnvironment(get_env(), log)
    cmd.build()

def build_sc_uid_expansion(env):
    from sc.csv_loader import table_reader
    import json, os.path
    filename = 'js/sc_uid_expansion_data.js'
    fullname = os.path.join(env.directory, filename)
    
    with open(fullname, 'w', encoding='UTF8') as outfile:
        data = {uid: [acro, name] for uid, acro, name in
            table_reader('uid_expansion')}
        
        outfile.write('sc.util.expand_uid_data = {}'.format(
            json.dumps(data, ensure_ascii=False)))
    
    return filename

def get_env():
    """Return the SuttaCentral webassets environment."""

    env = webassets.Environment(str(sc.static_dir), '/')
    env.auto_build = not config.compile_assets
    env.cache = str(sc.webassets_cache_dir)
    env.debug = not config.compile_assets
    env.manifest = 'json:{}'.format(sc.webassets_manifest_path)
    
    compile_fonts()

    css_normalize = webassets.Bundle(
        'css/vendor/normalize-2.1.3.css'
    )

    css_utf8 = webassets.Bundle(
        'css/utf8.css'
    )

    css_main = webassets.Bundle(
        'css/main.scss',
        depends=('css/*.scss', 'css/*/*.scss'),
        filters='pyscss',
        output='css/compiled/main-%(version)s.css'
    )

    css_core = webassets.Bundle(
        css_normalize,
        css_main,
        css_utf8,
        filters='cssmin',
        output='css/compiled/core-%(version)s.css'
    )

    env.register('css_core', css_core)
    
    sc_uid_expansion_data_file = build_sc_uid_expansion(env)

    sc_data_scripts_file = get_js_datascripts_filename()
    
    js_core = webassets.Bundle(
        'js/vendor/underscore-1.8.3.js',
        'js/sc_state.js',
        'js/vendor/clipboard.js',
        'js/vendor/jquery.hashchange-1.3.min.js',
        'js/vendor/jquery.easytabs-3.2.0.min.js',
        'js/vendor/jquery.dropdown.js',
        'js/vendor/polyglot.js',
        'js/vendor/jquery.mobile.custom.min.js',
        'js/lib/jquery.scrolllock.js',
        'js/lib/jquery.unveil.js',
        'js/lib/jquery.details.js',
        'js/exports.js',
        'js/intr.js',
        'js/sc_utility.js',
        sc_uid_expansion_data_file,
        'js/text.js',
        'js/text_selections.js',
        'js/search.js',
        'js/sidebar.js',
        'js/sc_functions.js',
        'js/sc_init.js',
        'js/header_menu.js',
        'js/sc_formatter.js',
        'js/sc_popupnotes.js',
        'js/sc_lzh2en_lookup.js',
        'js/text_image.js',
        'js/discourse.js',
        'js/fonts.js',
        sc_data_scripts_file,
        
        'js/tracking.js',
        filters=None if sc.config.debug else 'rjsmin',
        output='js/compiled/core-%(version)s.js'
    )
    env.register('js_core', js_core)

    # For some reason, webassets does not create these directories if
    # they do not exist...
    if not sc.webassets_cache_dir.exists():
        sc.webassets_cache_dir.mkdir(parents=True)

    return env


def sanitize_font_name(name):
    return name.rstrip('_-.0123456789')

fonts_dir = sc.static_dir / 'fonts'
fonts_json_file = fonts_dir / 'fonts.json'

font_header = '''
/* This file is generated automatically
 * DO NOT EDIT THIS FILE MANUALLY
 *
 * To add a font, edit {}
*/
'''.format(fonts_json_file)

font_face_template = '''
@font-face {{
    font-family: '{family}';
    font-weight: {weight};
    font-style: {style};
    src: url('{url}.woff') format('woff'),
         url('{url}.woff2') format('woff2');
}}
'''



def compile_fonts(flavors=['woff', 'woff2']):
    import json
    import hashlib
    from fontTools.ttLib import TTFont
    
    font_face_decls = []
    
    fonts_output_dir = fonts_dir / 'compiled'
    if not fonts_output_dir.exits():
        fonts_output_dir.mkdir()
    try:
        with fonts_json_file.open() as f:
            font_data = json.load(f)
    except json.decoder.JSONDecodeError:
        logging.error('Error while processing %s', str(fonts_json_file))
        raise
        
    fonts_seen = set()
    font_keys = set()
    
    def get_font_family_weight_and_style(font_name):
        result = {}
        for key, name in sorted(font_data["families"].items(), key=lambda t: len(t[0]), reverse=True):
            if font_name.startswith(key):
                result["family"] = name
                font_keys.add((key, name))
                leftovers = font_name[len(key): ]
                fonts_seen.add(key)
                break
        else:
            logger.error('Font file %s does not have a matching entry in fonts.json', font_name)
            return None
        
        for key, weight in sorted(font_data["weights"].items(), key=lambda t: len(t[0]), reverse=True):
            if key in leftovers:
                result["weight"] = weight
                break
        else:
            result["weight"] = "normal"
        
        for key, style in sorted(font_data["styles"].items(), key=lambda t: len(t[0]), reverse=True):
            if key in leftovers:
                result["style"] = style
                break
        else:
            result["style"] = "normal"
        return result            
    
    seen = {}
    
    compiled_fonts = set(fonts_output_dir.glob('**/*'))
    valid_compiled_fonts = set()
    
    for file in sorted(fonts_dir.glob('**/*')):
        
        nonfree = "nonfree" in file.parts
        if file in compiled_fonts:
            continue
        if file.suffix not in {'.tff', '.otf', '.woff', '.woff2'}:
            continue
        print('Now processing {!s}'.format(file.name))
        base_name = sanitize_font_name(file.stem)
        if base_name in seen:
            logger.error('Font file %s is too similiar to other file %s, skipping', file, seen[base_name])
        seen[base_name] = file
        
        with file.open('rb') as f:
            font_binary_data = f.read()
        md5sum = hashlib.md5(font_binary_data).hexdigest()[:12]
        
        outname = md5sum if (nonfree and not sc.config.app['debug']) else "{}_{}".format(base_name, md5sum)
        base_outfile = fonts_output_dir / outname
        
        font = None
        
        for flavor in flavors:
            suffix = '.{}'.format(flavor)
            outfile = base_outfile.with_suffix(suffix)
            valid_compiled_fonts.add(outfile)
            if not outfile.exists():
                if outfile.suffix == file.suffix:
                    with outfile.open('wb') as f:
                        f.write(font_binary_data)
                else:
                    if font is None:
                        font = TTFont(str(file))
                    font.flavor = flavor
                    font.save(file=str(outfile))
        
        font_details = get_font_family_weight_and_style(file.stem)
        if font_details:
            font_face_decls.append(font_face_template.format(url='/fonts/compiled/{}'.format(outname), **font_details))
    
    for file in compiled_fonts - valid_compiled_fonts:
        file.unlink()
    
    font_face_decls
    
    with (sc.static_dir / 'css' / 'fonts' / 'fonts-auto.scss').open('w') as f:
        f.write(font_header)
        f.writelines("${} = '{}';\n".format(key, name) for key, name in sorted(font_data["families"].items()))
        f.writelines(font_face_decls)
    
    for key in set(font_data["families"]) - fonts_seen:
        logger.error('Font family mapping matches no font file: {} ({})'.format(key, font_data["families"][key]))
        
        

def compress_static():
    """Pre-compress static data (for Nginx ngx_http_gzip_static_module)"""
    import plumbum
    try:
        compress_cmd = plumbum.local['zopfli']['--gzip']
    except plumbum.CommandNotFound:
        print('zopfli not available, falling back to gzip')
        compress_cmd = plumbum.local['gzip']['-9', '-k']
    
    extensions = {'.js', '.css', '.svg', '.ttf'}
    files = set(sc.static_dir.glob('fonts/**/*'))
    files.update(sc.static_dir.glob('js/data/*'))
    files.update(sc.static_dir.glob('js/compiled/*'))
    files.update(sc.static_dir.glob('css/compiled/*'))
    to_process = []
    for file in sorted(files):
        if file.suffix == '.gz':
            if file.with_name(file.stem) not in files:
                # Remove if original does not exist anymore
                file.unlink()
            continue
        if file.suffix not in extensions:
            continue
        if file.with_suffix(file.suffix + '.gz') in files:
            continue
        to_process.append(file)
    if to_process:
        print('Compressing {} files'.format(len(to_process)))
        compress_cmd[to_process]()
        
def get_js_datascripts_filename():
    import pathlib
    filepath = sc.static_dir / 'js/data/lzh2en-data-scripts-names.js'
    if not filepath.exists():        
        import tasks.jsdata
        tasks.jsdata.build(minify=True, quiet=True)
    return str(filepath)
