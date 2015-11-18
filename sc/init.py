""" Module responsible for periodic updating """

import os
import sys
import time
import logging
import pathlib
import importlib
import threading
logger = logging.getLogger(__name__)

logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('plumbum').setLevel(logging.WARNING)

import sc

try:
    _reloading
except NameError:
    _reloading = False
else:
    _reloading = True

if not _reloading:
    init_lock = threading.Lock()
    reinit_lock = threading.Lock()
    search_lock = threading.Lock()
    should_reinit = False
    module_reloader = None
    auto_reloader = None


def update_search():
    import sc.search
    import sc.search.updater

    if search_lock.acquire(blocking=False):
        try:
            sc.search.updater.start()
            sc.search.update_indexes()
            print("Index Update Complete")
        finally:
            search_lock.release()

def init():
    # Import here to delay intialization code.
    global module_reloader
    
    if not init_lock.acquire(blocking=False):
        print('Init already in progress')
        return
    try:
        import sc
        import sc.scimm
        import sc.textdata
        import sc.text_image_index
        
        print("Building TIM")
        sc.textdata.build()
        print("Building IMM")
        sc.scimm.build()
        print("Building Text Image Index")
        sc.text_image_index.build()
        print("Components are now ready")
        
        if sc.config.app['update_search']:
            print("Initiating Index Update in Background")
            threading.Thread(target=update_search, daemon=True).run()
        
        if module_reloader is None:
            module_reloader = ModuleReloader()
            module_reloader.set_file_mtimes()
    finally:
        init_lock.release()
        if should_reinit:
            reinit()
    
def reinit():
    """Perform a live restart of the server"""
    global should_reinit
    should_reinit = False
    if reinit_lock.acquire(blocking=False):
        try:
            if module_reloader:
                module_reloader.reload()
            
            import sc.views
            import sc.assets
            if sc.config.app['compile_assets']:
                sc.assets.compile()
                sc.views.jinja2_environment(rebuild=True)
                # Compress static resources in background thread
                threading.Thread(target=sc.assets.compress_static, daemon=True).start()
            
            # Perform init
            init()
        finally:
            reinit_lock.release()
    else:
        should_reinit = True
        print('Reloading already in progress, queuing reload')
    
class ModuleReloader:
    _file_mtimes = None
    
    def set_file_mtimes(self):
        self._file_mtimes = self.get_file_mtimes()
    
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
        new_mtimes = self.get_file_mtimes()
        for key, (old_mtime, module) in self._file_mtimes.items():
            if new_mtimes[key][0] != old_mtime:
                print('RELOADER: Reloading {}'.format(key))
                try:
                    importlib.reload(module)
                except Exception as e:
                    logger.exception(e)
                    
        self._file_mtimes = new_mtimes



class AutoReloader(threading.Thread):
    """Auto Reloader which examines state of files and decides if the
    server should reload data.
    
    Don't use this in production!
    """
    
    def __init__(self):
        super().__init__(daemon=True)
        self.watchlist = []
        self.mtimes = {}
        self.last_mtime_sum = None
        self.i = 0
    
    def get_data_files(self):
        files = []
        for dir, _, filenames in os.walk(str(sc.data_dir)):
            for filename in filenames:
                parts = filename.split('.')
                if len(parts) > 1:
                    ext = parts[-1]
                    if ext in {'html', 'csv', 'json'}:
                        files.append(dir + '/' + filename)
        return sorted(files)
    
    def step(self):
        watchlist = self.watchlist
        mtimes = self.mtimes
        major = (self.i % 10 == 0)
        if major:
            files = self.get_data_files()
        else:
            files = self.watchlist
        
        if module_reloader:
            module_reloader.reload()
        
        mtime_sum = 0
        changed_files = []
        for file in files:
            mtime = os.stat(file).st_mtime_ns
            mtime_sum += mtime
            if mtime != mtimes.get(file):
                changed_files.append(file)
                if self.i != 0:
                    watchlist.append(file)
                mtimes[file] = mtime
        
        
        
        if len(watchlist) > 3:
            watchlist = watchlist[-3:]
        
        if self.i > 0: 
            if changed_files:
                print('Files have changed: {}'.format(', '.join(str(pathlib.Path(f).relative_to(sc.base_dir)) for f in changed_files)))
            if changed_files or (major and (mtime_sum != self.last_mtime_sum)):
                print('Performing reinit')
                reinit()

        if major:
            self.last_mtime_sum = mtime_sum
            
    def run(self):
        while True:
            try:
                self.step()
            except InitError as e:
                logger.exception(e)
            time.sleep(5)
            self.i += 1
            
def start():
    def inner():
        init()
        if sc.config.app['debug']:
            start_autoreloader()
    
    threading.Thread(target=inner, daemon=True).start()

if not _reloading:
    start()


def start_autoreloader():
    global auto_reloader
    if not auto_reloader:
        auto_reloader = AutoReloader().start()
        
    
    
    
    
    
    
