import os
import tornado
from tornado import httpserver
from tornado import web
from tornado.options import options

from apps.view import WeatherCallback
from setting.setting import DEBUG
from utils.baseAsync import BaseAsync

tornado.options.define('port', type=int, default=8017, help='服务器端口号')


class HttpService(BaseAsync):
    def __init__(self):
        self.urlpatterns = [
            (r'/weather/callback', WeatherCallback, {'server': self}),
        ]
        app = web.Application(self.urlpatterns,
                              debug=DEBUG,
                              # autoreload=True,
                              # compiled_template_cache=False,
                              # static_hash_cache=False,
                              # serve_traceback=True,
                              static_path = os.path.join(os.path.dirname(__file__),'static'),
                              template_path = os.path.join(os.path.dirname(__file__),'template'),
                              autoescape=None,  # 全局关闭模板转义功能
                                      )
        http_setver = httpserver.HTTPServer(app)
        http_setver.listen(options.port)