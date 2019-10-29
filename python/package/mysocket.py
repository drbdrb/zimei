from websocket import create_connection
import json

class Mysocket():
    """内部通信模块"""

    def __init__(self ):
        self.connection()

    def connection(self):
        try:
            self.ws = create_connection("ws://127.0.0.1:8103")
        except Exception as e:
            self.ws = False

    #重新连接
    def reconnect(self):
        try:
            self.ws = self.ws.connect("ws://127.0.0.1:8103")
        except Exception as e:
            self.ws = False


    #发送屏幕文字
    def send_info(self, txt= {}):
        if self.ws:
            info = {
                't':'info',
                'init':0,           # 是否为初始化唤醒
                'obj':'mojing',     # 对象： zhuren / mojing  主人/魔镜
                'emot':'',          # 情感：
                'msg': txt['msg'],  # 消息体
                'timer':3           # 停留时长（秒）
            }
            if type(txt['obj']) is str:
                info['obj'] = txt['obj']

            if 'emot' in txt.keys():
                info['emot'] = txt['emot']

            if 'init' in txt.keys():
                info['init'] = txt['init']

            info['timer'] = round(len(txt['msg']) * 0.21, 2)

            jsonstr = json.dumps(info)
            self.ws.send(jsonstr)

    #发送麦的状态
    def sendmic(self, sendstr= ''):
        if self.ws:
            self.ws.send('{"t":"m","m":"'+str(sendstr)+'"}')

    #发送设备状态
    def send_devstate(self, sendjson ):
        if self.ws:
            info = sendjson
            info['t'] = 'dev'
            jsonstr = json.dumps(info)
            self.ws.send(jsonstr)

    #发送导航消息
    def send_nav(self, navjson ):
        if self.ws:
            info = {
                't':'nav',
                'event':'',
                'size':{
                    "width":380,
                    "height":380
                },
                'url':''          # 情感：
            }
            if 'event' in navjson.keys():
                info['event'] = navjson['event']
            else:
                info['event'] = 'close'

            if 'size' in navjson.keys():
                info['size'] = navjson['size']
            else:
                info['size'] = {"width":500,"height":300}

            if 'url' in navjson.keys():
                info['url'] = navjson['url']

            if info['event']=='open':
                if info['url'] =='':
                    return

            jsonstr = json.dumps(info)
            self.ws.send(jsonstr)

    #发送其他消息体
    def send(self, sendjson ):
        jsonstr = json.dumps(sendjson)
        self.ws.send(jsonstr)

    #接收消息
    def recv(self):
        result =self.ws.recv()
        return result

    #连接初始化
    def init(self):
        self.connection()

    def close(self):
        self.ws.close()