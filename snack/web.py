import os
import redis
import tornado.options

from tornado import ioloop
from tornado import web
from tornado import httpserver
from tornado.options import define, options

from snack import handler
from snack import settings
from snack.session import RedisSessionStore

define("port", default=80, help="run on the given port", type=int)

class Application(web.Application):
    def __init__(self):
        
        handlers = [(r"/", handler.monitor.Instance),
                    (r"/ajax/(.*)", handler.ajax.AjaxHandler),]
        
        redis_connection = redis.Redis(host='localhost', port=6379, db=0)
        self.session_store = RedisSessionStore(redis_connection)
        
        application_settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            
            #These three parameters are used for session settings.
            permanent_session_lifetime = 1,
            redis_server = True,
            cookie_secret = 'You would never know this.',
            
            debug=settings.DEBUG)
        
        web.Application.__init__(self, handlers, **application_settings)

def main():
    tornado.options.parse_command_line()
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
