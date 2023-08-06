import pascut
from optparse import IndentedHelpFormatter, OptionParser
import sys
from os import path

"""
Usage: $ pascut HelloWrold.as
    -b, --bind-address=VAL           server bind address(default 0.0.0.0)
    -c, --compile-config=VAL         mxmlc compile config ex:) --compile-config="-benchmark -strict=true"
        --fcsh-cmd=VAL               fcsh command path
    -I, --observe-files=VAL          observe files and directories path
    -h, --help                       show this message
    -i, --interval=VAL               interval time(min)
    -l, --log=VAL                    showing flashlog.txt
    -m, --mapping=VAL                server mapping path :example) -m "../assets=assets" -m "../images/=img"
        --no-file-observe            don't observing files
        --observe-ext=VAL            observe ext ex:) --observe-ext="as3,actionscript3,css,mxml"
    -s, --server                     start autoreload webserver
        --server-handler=val         set server hander :example) --server-handler=webrick
    -p, --port=val                   server port(default: 3001)
        --plugin-path=VAL            set load plugin(s) path
    -t, --template=VAL               server use template file
    -v, --verbose                    detail messages
        --version                    show version
"""

def parse_args(args):
    parser = OptionParser(formatter=IndentedHelpFormatter(
        max_help_position=60, width=200))
    parser.add_option('-b', '--bind-address', dest='addr',
            default='0.0.0.0', help='server bind address(default 0.0.0.0)')
    parser.add_option('-c', '--compile-config', dest='compile_config',
            default='', help='mxmlc compile config ex:) --compile-config="-benchmark -strict=true"')
    parser.add_option('', '--fcsh-cmd', dest='fcsh_cmd',
            default='fcsh', help='fcsh command path')
    parser.add_option('-I', '--observe-files', dest='observe_files',
            default='', help='observe files and directories path. ext:)\
            --observe-files="./lib/src/lib1, ./lib/src/lib2"')
    parser.add_option('-i', '--interval', dest='interval',
            type="int", default='5', help='interval time(min)')
    #parser.add_option('-l', '--log', dest='flashlog',
    #        default='', help='showing flashlog.txt')
    #parser.add_option('-m', '--mapping', dest='mapping',
    #        default='', help='server mapping path :example) -m "../assets=assets" -m "../images/=img"')
    #parser.add_option('--no-file-observe', dest='no_observe',
    #        action="store_false", default=False, help="don't observing files")
    parser.add_option('--observe-ext', dest='observe_ext',
            default='"as, mxml"', help='observe ext ex:) --observe-ext="as3,actionscript3,css,mxml"')
    parser.add_option('-s', '--server', dest='server',
            default=False, action="store_true", help='start autoreload webserver')
    parser.add_option('-p', '--port', dest='port',
            type="int", default=3001, help='server port(default: 3001)')
    #parser.add_option('--plugin-path', dest='plugin_path',
    #        default=None, help='set load plugin(s) path')
    #parser.add_option('-t', '--template', dest='template_file',
    #        help='server use template file')
    parser.add_option('-v', '--verbose', dest='verbose',
            action="store_true", default=False, help='detail messages')
    parser.add_option('--plugin-debug', dest='plugin_debug',
            action="store_true", default=False, help='detail plugin debug messages')
    parser.add_option('--version', dest='version',
            action="store_true", default=False, help='show version')

    config, args = parser.parse_args(args)
    if config.version:
        print pascut.version_info
        sys.exit(0)
    if not args:
        raise RuntimeError("require mxml or as files")
    target = args[0]
    config.swf_root = path.dirname(target)
    config.target = target
    return config.__dict__

