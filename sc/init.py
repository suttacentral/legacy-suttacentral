""" Module responsible for periodic updating """

import os
import time
import logging
import importlib
import threading
import scandir
logger = logging.getLogger(__name__)

import sc

try:
    _reloading
except NameError:
    _reloading = False
else:
    _reloading = True

if not _reloading:
    init_lock = threading.Lock()
    
def init():
    # Import here to delay intialization code.
    with init_lock:
        import sc
        import sc.scimm
        import sc.textdata
        import sc.text_image
        
        sc.textdata.build()
        sc.scimm.build()
        sc.text_image.update_symlinks()
        
        import sc.search
        import sc.search.updater
        
        sc.search.update_indexes()
        
        sc.search.updater.start()
        
        if module_reloader is None:
            module_reloader = ModuleReloader()
            module_reloader.set_file_mtimes()


if not _reloading:
    reinit_lock = threading.Lock()
    
def reinit():
    """Perform a live restart of the server"""
    with reinit_lock:
        if module_reloader:
            module_reloader.reload()
        
        import sc.views
        import sc.assets
        if sc.config.app['compile_assets']:
            sc.assets.compile()
            sc.views.jinja2_environment(rebuild=True)
            # Compress static resources in background thread
            threading.Thread(target=sc.assets.compress_static, dameon=True).start()
        
        # Perform init
        init()
    
class ModuleReloader:
    _file_mtimes = None
    
    def set_file_mtimes(self):
        self._file_mtimes = get_file_mtimes()
    
    @staticmethod
    def get_file_mtimes():
        mtimes = {}
        for k in sys.modules:
            if k.startswith('sc.'):
                module = sys.modules[k]
                mtimes[k] = (os.stat(module.__file__).st_mtime, module)
        return mtimes

    def reload(self):
        if self._file_mtimes is None:
            return
        new_mtimes = get_module_times()
        for key, (old_mtime, module) in self._file_mtimes:
            if new_mtimes[key][0] != old_mtime:
                print('RELOADER: Reloading {}'.format(key))
                importlib.reload(module)

module_reloader = None

class AutoReloader(threading.Thread):
    """Auto Reloader which examines state of files and decides if the
    server should reload data.
    
    Don't use this in production!
    """
    
    def __init__(self):
        super().__init__(daemon=True)
    
    def get_data_files(self):
        files = []
        for dir, _, filenames in scandir.walk(str(sc.data_dir)):
            for filename in filenames:
                parts = filename.split('.')
                if len(parts) > 1:
                    ext = parts[-1]
                    if ext in {'html', 'csv', 'json'}:
                        files.append(dir + '/' + filename)
        return files
        
    def run(self):
        
        watchlist = [] # If a file is changed it's added to watchlist
        mtimes = {}
        last_mtime_sum = None # We sum mtimes to catch deleted files
        i = 0
        while True:
            major = (i % 30 == 0)
            if major:
                files = self.get_data_files()
            else:
                files = watchlist
            
            if module_reloader:
                module_reloader.reload()
            
            changed = False
            mtime_sum = 0
            for file in files:
                mtime = os.stat(file).st_mtime_ns
                mtime_sum += mtime
                if mtime != mtimes.get(file):
                    changed = True
                    if i != 0:
                        watchlist.append(file)
                    mtimes[file] = mtime
            
            if len(watchlist) > 3:
                watchlist = watchlist[-3:]
            
            if i > 0: 
                if changed or (major and (mtime_sum != last_mtime_sum)):
                    reinit()
            if major:
                last_mtime_sum = mtime_sum
            time.sleep(2)
            i += 1
        
def start():
    threading.Thread(target=init, daemon=True).start()

if not _reloading:
    start()
    if sc.config.app['debug']:
        auto_reloader = AutoReloader().start()
        
    
    
    
    
    
    
