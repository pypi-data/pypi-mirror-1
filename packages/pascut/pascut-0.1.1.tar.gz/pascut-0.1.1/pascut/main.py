from plugpy import *
from pascut.commands import parse_args
from pascut.plugin import LoggerPlugin, FileObserverPlugin, CompilerPlugin, ServerPlugin
import sys
import signal
from os import path

default_plugin_path = path.join(path.dirname(path.abspath(__file__)), 'plugins')

def main():
    args = sys.argv
    args = args[1:]
    if not args:
        start(['-h'])
    else:
        start(args)

def start(argv):
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)

    config = parse_args(argv)
    #print config    
    
    plugin_path=[config.pop('plugin_path', None), default_plugin_path]
    plugin_class=[Plugin, LoggerPlugin, ServerPlugin, FileObserverPlugin, CompilerPlugin]
    ignore_class=[LoggerPlugin, CompilerPlugin, ServerPlugin, FileObserverPlugin]
    
    load_plugins(config, plugin_path=plugin_path, 
        plugin_class=plugin_class, ignore_class=ignore_class,
            debug=config['plugin_debug'])
    
    dispatch('debug', "paramter %s " % config, 'main', target=LoggerPlugin)
    dispatch('start', target=FileObserverPlugin)
    dispatch('start', target=CompilerPlugin)

    if config['server']:
        dispatch('start', target=ServerPlugin)

def stop(*args):
    dispatch('stop', target=FileObserverPlugin)
    dispatch('stop', target=ServerPlugin)
    dispatch('stop', target=CompilerPlugin)

    
