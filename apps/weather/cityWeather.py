import datetime

from tornado import gen

from apps.weather.weater import Weather
from setting.setting import QOS_LOCAL
from utils.baseAsync import BaseAsync
from utils.logClient import logClient
from utils.my_json import json_dumps


class CityWeather(Weather,BaseAsync):
    def __init__(self,guid,name,city_id,publish_func,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.myPublish = publish_func
        self.guid = guid
        self.name = name
        self.city_id = city_id
        self.updateInvertal = 3*60*60
        self.ioloop.add_timeout(self.ioloop.time(),self.getSelfWeather)

    @gen.coroutine
    def getSelfWeather(self):
        result = yield self.getWeather(self.city_id,self.name)
        # print(result)
        status = result.get('status')
        if status == 1:
            yield logClient.tornadoErrorLog(result.get('errmsg'))
            return
        city_id = result.get('cityid')          #当前城市ID
        if city_id != self.city_id:
            yield logClient.tornadoErrorLog('{}:获取的天气信息城市不一至:{},{}'.format(self.name,self.city_id,city_id))
            return
        date = result.get('date')               #日期
        # week = result.get('week')               #星期
        update_time = result.get('update_time') #气象台更新时间
        # city = result.get('city')               #天气情况
        # cityEn = result.get('cityEn')           #
        # country = result.get('country')         #
        # countryEn = result.get('countryEn')
        self.wea = result.get('wea')                 #天气情况
        self.wea_img = result.get('wea_img')         #天气对应图标(xue, lei, shachen, wu, bingbao, yun, yu, yin, qing)
        self.tem = result.get('tem')                 #当前温度
        self.tem1 = result.get('tem1')            #最小温度
        self.tem2 = result.get('tem2')            #最大温度
        self.win = result.get('win')                 #风向
        self.win_speed = result.get('win_speed')     #风速等级
        self.win_meter = result.get('win_meter')     #风速 如: 12km/h
        self.humidity = result.get('humidity')       #湿度
        self.visibility = result.get('visibility')   #能见度
        self.pressure = result.get('pressure')       #气压hPa
        self.air = result.get('air')                 #空气质量
        self.air_pm25 = result.get('air_pm25')       #PM2.5
        self.air_level = result.get('air_level')     #空气质量等级
        # air_tips = result.get('air_tips')       #空气质量描述
        # alarm = result.get('alarm')
        now_time = datetime.datetime.now()
        updateTime = datetime.datetime.strptime(date +' '+update_time,'%Y-%m-%d %H:%M')
        last_update_time = updateTime + datetime.timedelta(seconds=self.updateInvertal)
        invertal = (last_update_time - now_time).seconds+30

        yield self.publishSelfInfo()
        self.ioloop.add_timeout(self.ioloop.time()+invertal, self.getSelfWeather)
        yield logClient.tornadoInfoLog('城市:{},天气情况:{}'.format(self.name,self.wea))
        yield logClient.tornadoInfoLog('城市:{},天气对应图标:{}'.format(self.name,self.wea_img))
        yield logClient.tornadoInfoLog('城市:{},当前温度:{}'.format(self.name,self.tem))
        yield logClient.tornadoInfoLog('城市:{},最大温度:{}'.format(self.name, self.tem1))
        yield logClient.tornadoInfoLog('城市:{},最小温度:{}'.format(self.name, self.tem2))
        yield logClient.tornadoInfoLog('城市:{},风向:{}'.format(self.name,self.win))
        yield logClient.tornadoInfoLog('城市:{},风速等级:{}'.format(self.name,self.win_speed))
        yield logClient.tornadoInfoLog('城市:{},风速:{}'.format(self.name,self.win_meter))
        yield logClient.tornadoInfoLog('城市:{},湿度:{}'.format(self.name,self.humidity))
        yield logClient.tornadoInfoLog('城市:{},能见度:{}'.format(self.name,self.visibility))
        yield logClient.tornadoInfoLog('城市:{},气压hPa:{}'.format(self.name,self.pressure))
        yield logClient.tornadoInfoLog('城市:{},空气质量:{}'.format(self.name,self.air))
        yield logClient.tornadoInfoLog('城市:{},PM2.5:{}'.format(self.name,self.air_pm25))
        yield logClient.tornadoInfoLog('城市:{},空气质量等级:{}'.format(self.name,self.air_level))

    @gen.coroutine
    def publishSelfInfo(self):
        info = yield self.getSelfInfo()
        topic = '/aaiot/{}/send/controlbus/event/websocket/city_weather/0'.format(self.guid)
        data = json_dumps(info)
        yield self.myPublish(topic=topic,payload=data,qos=QOS_LOCAL)

    @gen.coroutine
    def askSelfInfo(self,connection_token):
        info = yield self.getSelfInfo()
        info['connection_token'] = connection_token
        topic = '/aaiot/{}/send/controlbus/event/websocket/city_weather/0'.format(self.guid)
        data = json_dumps(info)
        yield self.myPublish(topic=topic, payload=data, qos=QOS_LOCAL)

    @gen.coroutine
    def getSelfInfo(self):
        info = {
            'type':'city_weather',
            'guid':self.guid,
            'name':self.name,
            'tem':self.tem,
            'tem1': self.tem1,
            'tem2': self.tem2,
            'win':self.win,
            'win_speed': self.win_speed,
            'win_meter': self.win_meter,
            'humidity': self.humidity,
            'visibility': self.visibility,
            'air': self.air,
            'air_pm25': self.air_pm25,
            'air_level': self.air_level,
            'pressure': self.pressure,
            'wea': self.wea,
            'wea_img': self.wea_img,
        }
        return info
