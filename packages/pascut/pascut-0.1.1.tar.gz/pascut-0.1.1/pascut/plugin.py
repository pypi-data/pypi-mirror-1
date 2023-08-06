from plugpy import Plugin, dispatch
from os import path
from BaseHTTPServer import BaseHTTPRequestHandler

def log_message(self, format, *args):
    msg = format%args
    dispatch('info', msg, self, target=LoggerPlugin)

BaseHTTPRequestHandler.log_message = log_message

def debug(msg, obj):
    dispatch('debug', msg, obj, target=LoggerPlugin)

def info(msg, obj):
    dispatch('info', msg, obj, target=LoggerPlugin)

class LoggerPlugin(Plugin):

    def on_info(self, msg):
        pass

    def on_debug(self, msg):
        pass

class CompilerPlugin(Plugin):
    
    def on_start(self):
        pass

    def on_stop(self):
        pass
    
    def compile(self):
        pass
    
    def on_compile(self):
        res = self.compile()
        if res:
            dispatch('reload', target=ServerPlugin)
        
    def debug(self, msg):
        debug(msg, self)

    def info(self, msg):
        info(msg, self)

class ServerPlugin(Plugin):

    def on_start(self):
        pass

    def on_stop(self):
        pass
    
    def on_reload(self):
        self.reload()

    def debug(self, msg):
        debug(msg, self)

    def info(self, msg):
        info(msg, self)

class FileObserverPlugin(Plugin):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def debug(self, msg):
        debug(msg, self)

    def info(self, msg):
        info(msg, self)

    def compile(self):
        dispatch('compile', target=CompilerPlugin)

    
