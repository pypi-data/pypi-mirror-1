from pascut.plugin import CompilerPlugin
from subprocess import Popen, PIPE
import os
import re
import thread

COMPILE_ERROR_RE = re.compile(" Error: (.*)")
COMPILE_ID_RE = re.compile("fcsh: Assigned (\d+) as the compile target id")
FCSH = re.compile("\(fcsh\) $")

class FlashCompiler(CompilerPlugin):

    def __init__(self, *args, **kwargs):
        self._fcsh_cmd = kwargs.get("fcsh_cmd", None)
        self.debug('fcsh %s' % self._fcsh_cmd)
        self._target = kwargs.get("target", '')
        self.debug('target %s' % self._target)
        compile_config = kwargs.get("compile_config", '').strip()
        if compile_config.startswith('"'):
            compile_config = compile_config[1:]
        if compile_config.endswith('"'):
            compile_config = compile_config[:-1]
        self._compile_config = compile_config
        self.debug('compile_config %s' % self._compile_config)
        #self._config = config
        self._process = None
        self._compile_id = None
        self._lock = None
        self._threaded = kwargs['server']
    
    def read_result(self, init=False):
        res = ''
        while True:
            buf = self._process.stdout.read(1)
            res = res + buf
            if FCSH.search(res):
                return res

    def init_process(self):
        if not self._process:
            org_lang = os.environ['LANG']
            os.environ['LANG'] = 'C'
            self._process = Popen(' '.join([self._fcsh_cmd,"2>&1"]),
                stdin=PIPE, stdout=PIPE,
                shell=True, close_fds=True)
            self.read_result()

            #self._in = self._process.stdin
            #self._out = self._process.stdout
            os.environ['LANG'] = org_lang
            self.debug('fcsh process open')
    
    def compile_cmd(self):
        cmd = ' '.join(['mxmlc', self._compile_config, self._target, '\n'])
        self.info('compile_cmd %s' % cmd)
        return cmd
    
    def on_start(self, *args, **kwargs):
        if self._threaded:
            thread.start_new_thread(self.compile, ())
        else:
            self.compile()
        #self.wait()
    
    def lock(self):
        return self._lock.acquire(0)

    def unlock(self):
        return self._lock.release()

    def compile(self):
        init = False
        res = True
        if not self._process:
            init = True
            self.init_process()
        
        if not self._lock:
            self._lock = thread.allocate_lock()

        if not self.lock():
            return False
        #self.debug('compiler lock %s' % self._lock)
        out = None
        self.info('start compile')
        try:
            if self._compile_id:
                self._process.stdin.write("compile %s\n" % self._compile_id)
                out = self.read_result()
                match = COMPILE_ERROR_RE.search(out)
                self.info(out)
                if match:
                    res = False
                else:
                    self.debug('compile ok compile id %s' % self._compile_id)
                    #raise RuntimeError("Can not compile %s" % match.group(1))
            else:
                self._process.stdin.write(self.compile_cmd())
                out = self.read_result()
                match = COMPILE_ERROR_RE.search(out)
                self.info(out)
                if match:
                    res = False
                    #raise RuntimeError("Can not compile %s" % match.group(1))
                else:
                    match = COMPILE_ID_RE.search(out)
                    if match:
                        self._compile_id = match.group(1)
                    self.debug('compile ok compile id %s' % self._compile_id)
                    #raise RuntimeError("Can not compile %s" % out)
            if init:
                self.unlock()
                self.wait()
            return res
        finally:
            if not init:
                self.unlock()
            #self.debug('compiler lock release %s' % self._lock)


    def on_stop(self):
        self.stop()

    def stop(self):
        self._process.stdin.close()
        self._process.stdout.close()
        self._process.wait()

    def wait(self):
        if self._process:
            try:
                self._process.wait()
            except:
                pass
            

