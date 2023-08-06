from pascut.plugin import FileObserverPlugin
import os
import os.path
import fnmatch 
import thread
import time

class FileObserver(FileObserverPlugin):
    
    _ignore = ['*/.svn/*', '*/CVS/*', '*.pyc']
    running = False

    def __init__(self, **config):
        self.files = {}
        
        self._observe_ext = config['observe_ext'][1:-1].split(",")
        self.debug('observe_ext %s' % self._observe_ext)

        self._interval = int(config['interval'])
        self.debug('interval %s' % self._interval)
        
        self._ignore.extend(config.get('ignore', []))
        self.debug('ignore %s' % self._ignore)
        
        observe_file = config.get('observe_files')[1:-1].split(',')
        observe_file.append(config.get('swf_root'))
        self.debug('observe_files %s' % observe_file)
        self.observe(observe_file)
        
    def on_start(self, *args, **kwargs):
        thread.start_new_thread(self.run, ())

    def run(self):
        self.running = True
        while self.running:
            self.check()
            time.sleep(self._interval)

    def observe(self, files):
        for file in files:
            file = file.strip()
            if os.path.isdir(file):
                self.dir_observe(file)
            else:
                path = os.path.abspath(file)
                self.save_mtime(file)
        self.debug('find files %s' % self.files.keys())

    def dir_observe(self, dir):
        for root, dirs, files in os.walk(dir):
            for file in files:
                path = os.path.join(root, file)
                if not self.ignore_filter(path):
                    self.save_mtime(path)
            for dir in dirs:
                path = os.path.join(root, dir)
                if not self.ignore_filter(path):
                    self.save_mtime(path)
                
    def save_mtime(self, path, force=False):
        if os.path.exists(path):
            match = False
            for ext in self._observe_ext:
                if path.endswith(ext.strip()):
                    match = True
                    break
            if not match:
                return 
            if force or not path in self.files:
                self.files[path] = os.stat(path).st_mtime
    
    def check(self):
        modifies = []
        for path, mtime in self.files.items():
            if self.is_modify(path, mtime):
                modifies.append(path)
        if modifies:
            self.info('modify files %s' % modifies)
            self.compile()
    
    def is_modify(self, path, mtime):
        if not os.path.exists(path):
            del self.file[path]
            return True
        else:
            if os.stat(path).st_mtime > mtime:
                #print path
                self.save_mtime(path, True)
                if os.path.isdir(path):
                    self.dir_observe(path)
                return True
    
    def ignore_filter(self, path):
        return reduce(lambda x,y:x or y,
                [fnmatch.fnmatch(path, i) for i in self._ignore])
    
    def on_stop(self):
        pass

