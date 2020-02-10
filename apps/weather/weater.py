from tornado import gen

from setting.setting import TEST_SERVER_HOST
from utils.asyncRequest import asyncTornadoRequest
from utils.baseAsync import BaseAsync


class Weather(BaseAsync):
    def __init__(self,username,appsecret,appid,base_url):
        super().__init__()
        self.username = username
        self.appsecret = appsecret
        self.appid = appid
        self.baseUrl = base_url

    @gen.coroutine
    def getWeather(self,city_id,city_name):
        url = self.baseUrl+'/api/'
        data = {
            'appid':self.appid,
            'appsecret':self.appsecret,
            'version':'v6',
            'cityid':city_id,
            'city':city_name,
            'ip':'',
            # 'callback':'http://{}:8016/inkScreenToken/get_token'.format(TEST_SERVER_HOST),
            'vue':0,
        }
        result = yield asyncTornadoRequest(url=url,method='GET',params=data)
        return result

