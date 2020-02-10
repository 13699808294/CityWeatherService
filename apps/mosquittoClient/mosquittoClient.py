import json

from tornado import gen

from apps.weather.cityWeather import CityWeather
from apps.weather.weater import Weather
from setting.setting import QOS_LOCAL, DATABASES
from utils.bMosquittoClient import BMosquittoClient

from utils.MysqlClient import  mysqlClient
from utils.logClient import logClient
from utils.my_json import json_dumps

class MosquittoClient(BMosquittoClient):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.heartTopic = '/aaiot/cityWeater/send/controlbus/system/heartbeat'
        self.cityDict = {}

        self.ioloop.add_timeout(self.ioloop.time(), self.updateAllCity)
    @gen.coroutine
    def updateAllCity(self):
        for DATABASE in DATABASES:
            db = DATABASE['name']
            data = {
                'database': db,
                'fields': ['guid','name','city_id'],
                'eq': {
                    'is_delete': False,
                },
                'neq':{
                    'upper_story_id': None,
                    'city_id':'',
                }
            }
            msg = yield mysqlClient.tornadoSelectAll('d_city', data)
            if msg['ret'] == '0':
                city_list = msg['msg']
            else:
                yield logClient.tornadoErrorLog('数据库:{},查询错误:({})'.format(db, 'd_city'))
                continue
            for city_info in city_list:
                city_id = city_info.get('city_id')
                guid = city_info.get('guid')
                if not city_id or city_id in self.cityDict.keys():
                    continue

                city_ = CityWeather(**city_info,publish_func=self.myPublish,username='377031516',appsecret='JRt7az1y',appid='37394325',base_url='https://www.tianqiapi.com')
                self.cityDict[guid] = city_
        else:
            pass
    @gen.coroutine
    def handleOnMessage(self,mReceiveMessageObject):
        yield logClient.tornadoDebugLog(mReceiveMessageObject.topic)
        if mReceiveMessageObject.topicList[6] == 'city_weather':
            data = mReceiveMessageObject.data
            try:
                data = json.loads(data)
            except:
                return
            city_guid = data.get('city_guid')
            connection_token = data.get('connection_token')
            city = self.cityDict.get(city_guid)
            if city == None:
                return
            yield city.askSelfInfo(connection_token)

    @gen.coroutine
    def handle_on_connect(self):
        topic = '/aaiot/mqttService/receive/controlbus/system/heartbeat'
        self.connectObject.subscribe(topic, qos=QOS_LOCAL)
        yield logClient.tornadoDebugLog('订阅主题:({}),qos=({})'.format(topic, QOS_LOCAL))

        topic = '/aaiot/+/receive/controlbus/event/websocket/city_weather/0'
        self.connectObject.subscribe(topic, qos=QOS_LOCAL)
        yield logClient.tornadoDebugLog('订阅主题:({}),qos=({})'.format(topic, QOS_LOCAL))

