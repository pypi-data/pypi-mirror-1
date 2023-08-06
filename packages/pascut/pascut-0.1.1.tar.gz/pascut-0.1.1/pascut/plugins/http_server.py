from pascut.plugin import ServerPlugin
from werkzeug import run_simple, Request, Response, ClosingIterator
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
import os
from os import path
from threading import Event

INDEX = """
<html>
    <head>
      <title>Pascut</title>
      <style>
      * {
          margin:0;
          padding:0;
      }
      #content {
          text-align:center;
      }
      </style>
      <script type="text/javascript" src="/js/swfobject.js"></script>
      <!--__RELOAD__-->
    </head>
    <body>
      <div id="content"></div>

      <script type="text/javascript">
       var so = __SWFOBJECT__;
       window.onload = function() {
         __SWF_VARS__
         so.addVariable('pascut', 'true');
         so.write("content");
       }
      </script>
    </body>
</html>
"""

RELOAD_SCRIPT = """
    <script type="text/javascript">
    var Pascut = new Object;

    Pascut.xhr = (function() {
      if (typeof XMLHttpRequest != 'undefined') {
        return new XMLHttpRequest();
      } else {
        try {
          return new ActiveXObject("Msxml2.XMLHTTP");
        } catch(e) {
          return new ActiveXObject("Microsoft.XMLHTTP");
        }
      }
    })();

    Pascut.reloadObserver = function() {
        var x = Pascut.xhr;
        x.open('GET', '/reload?' + (new Date()).getTime(), true);
        x.onreadystatechange = function() {
          try {
            if (x.readyState == 4) {
              if (x.status == 200 && Number(x.responseText) == 1) {
                // thanks os0x!
                so.attributes.swf = so.attributes.swf + '+';
                so.write('content');
                Pascut.reloadObserver();
              } else {
                setTimeout(Pascut.reloadObserver, 5000);
              }
            }
          } catch(e) {
            setTimeout(Pascut.reloadObserver, 5000);
          }
        } 
        x.send(null);
    }

    Pascut.swf = function() {
       return document.getElementById('idswf');
    }

    Pascut.reloadObserver();
    </script>
"""

js_path = path.join(path.dirname(path.abspath(__file__)), 'js')

url_map = Map()
def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate


class Application(object):
    
    def __init__(self, target="", template=None, height='100%', width='100%', bgcol=0):
        self._template = template
        self._target = target
        self._height = height
        self._width = width
        self._bgcol = bgcol
        self._event = Event()
        self.running = True

    @expose('/')
    def index(self, request):
        self._event.clear()
        self._event.set()
        if self._template and path.isfile(self._template):
            res = '\n'.join(open(self._template).readlines())
        else:
            res = INDEX.replace('__SWFOBJECT__', self.create_swftag()).replace('<!--__RELOAD__-->', RELOAD_SCRIPT)

        res = res.replace('__SWF_VARS__', self.create_vars(request.args))        

        return Response(res, mimetype='text/html')

    @expose('/reload')
    def reload(self, request):
        if self.running:
            self._event.clear()
            self._event.wait()
        return Response("1", mimetype='text/html')
    
    def create_vars(self, dict):
        res = []
        for k, v in dict.items():
            res.append("so.addVariable('%s', '%s');" % (k, v))
        res = '\n'.join(res)
        return res

    def create_swftag(self):
        name = self._target
        name = path.basename(name)
        name = path.splitext(name)[0]
        swf = "/swf/%s.swf" % name
        height = self._height
        width = self._width
        bgcol = self._bgcol
        return 'new SWFObject("%(swf)s?" + (new Date()).getTime(), "idswf",\
        "%(width)s", "%(height)s", "9", "%(bgcol)s");' % locals()
    
    def stop(self):
        self.running = False
        self._event.set()
        
    def unlock(self):
        self._event.set()

    def __call__(self, environ, start_response):
        request = Request(environ)
        adapter = url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        return ClosingIterator(response(environ, start_response))

class HttpServer(ServerPlugin):

    def __init__(self, *args, **kwargs):
        self._addr = kwargs['addr']
        self._port = kwargs['port']
        self._swf_root = kwargs['swf_root']
        target = kwargs['target'] 
        self._app = Application(target=target)

    def on_start(self):
        self.start()

    def start(self):
        self.run()
    
    def run(self):
        static = {
            '/swf': self._swf_root,
            '/js': js_path
        }
        self.info('start web server')
        run_simple(self._addr, self._port, self._app, 
                static_files=static, threaded=True) 
    
    def reload(self):
        self.debug('reload swf')
        self._app.unlock()

    def on_stop(self):
        self.stop()

    def stop(self):
        self._app.stop()

if __name__ == '__main__':
    HttpServer().on_start()
