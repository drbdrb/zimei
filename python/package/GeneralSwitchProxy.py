import json
import logging
import os
import socket
from multiprocessing import Process
from MsgProcess import MsgProcess, MsgType
from bin.SocketServer import SocketServer


# 万能开关代理
class GeneralSwitchProxy(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.client = None
        p = Process(target=self.StartServer)
        p.start()

    # 万能开关收到消息回调
    def on_message(self, jsonobj, sock):
        logging.info('消息回调: %s' % (jsonobj) )
        if isinstance(jsonobj, dict):
            if jsonobj['type'] == 'online':
                self.say('万能开关设备已连接')
            elif jsonobj['type'] == 'offline':
                self.say('万能开关设备已断开')
            else:
                self.send(MsgType=MsgType.LoadPlugin,Receiver='ControlCenter',Data="Wnkg")
                self.send(MsgType=MsgType.Text,Receiver='Wnkg', Data=jsonobj)

    def publish(self, sendjson):
        '''
        系统发送消息给设备
        {
            "sender":"system",          // 发送者
            "receive":"kycx_45612",     // 接收者
            "type":"action",            // 操作类型
            "data":{
                //消息体
            }
        }
        '''
        if self.client is None:
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            connst = client.connect_ex(('127.0.0.1',8301))
            if connst==0:
                self.client = client

        if self.client:
            json_str = json.dumps(sendjson)
            self.client.send(json_str.encode("utf-8"))

    def StartServer(self):
        #dbpath = os.path.join(self.config['root_path'], 'data/device.db')
        dbpath = './data/device.db'
        serverinfo = ('0.0.0.0',8301)
        Sock = SocketServer(dbpath, serverinfo)
        Sock.run( self.on_message )
       
    def Text(self, message):
        '''
        回调函数,收到插件发来的文本消息 转发到万能开关服务器
        {
            "sender":Sender,
            "receive":receive,
            "data":data
        }
        参数中：data 必须为字典类型，格式如下：
        {
            'deviceid':'设备ID',
            'data': {
                'type':'switch',    开关类型，分为：switch-开关 / 
                'state':state       状态
            }
        }
        '''
        Sender = message['Sender']
        Data = message['Data']

        logging.info('万能开关收到控制中心消息: %s' % ( str(Data) ) )

        if isinstance(Data, dict):
            if 'deviceid' in Data and 'data' in Data:
                receive = Data['deviceid']
                data = Data['data']

                send_json = {"sender":Sender,"receive":receive,"data":data}
                self.publish( send_json )
