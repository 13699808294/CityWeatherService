import json

from tornado import web

from utils.baseAsync import BaseAsync


class BaseHanderView(web.RequestHandler,BaseAsync):
    def set_default_headers(self) -> None:
        # print('调用了set_default_headers')
        self.set_header('Content-Type','application/json;charset=UTF-8')

    def write_error(self, status_code: int, **kwargs) -> None:
        # print('调用write_error')
        self.write(u"<h1>出错了</h1>")
        self.write(u'<p>{}</p>'.format(kwargs.get('error_title','')))
        self.write(u'<p>{}</p>'.format(kwargs.get('error_message','')))

    def initialize(self,**kwargs) -> None:
        self.server = kwargs.get('server')
        # print('调用initialize')

    def prepare(self):
        if self.request.headers.get('Content-Type','').startswith('application/json'):
            self.json_dict = json.loads(self.request.body)
        else:
            self.json_dict = None

    def on_finish(self) -> None:
        pass

class WeatherCallback(BaseHanderView):

    def get(self,*args,**kwargs):
        print(self.request.body)
        self.write('')