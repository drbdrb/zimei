import json
import logging
import time
import sqlite3
import include.mqtt.client as mclient
from MsgProcess import MsgProcess, MsgType


# 万能开关代理
class GeneralSwitchProxy(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.client = None
        self.isconnect = False

        # 本地MQTT服务器信息
        self.__host = '127.0.0.1'                   # severIP
        self.__port = 1883                          # 1883
        self.__clientid  = 'GeneralSwitchProxy'     # 设备id
        self.__mqtt_name = 'GeneralSwitchProxy'     # 用户名
        self.__mqtt_pass = 'GeneralSwitchProxy'     # 密码
        self.topic = '/public/almight/admin'        # 公共话题

        self.dbfile = "./data/device.db"            # 管理数据库
    

    def Start(self, message):
        if not self.isconnect:
            self.isconnect = True
            self.client = mclient.Client(client_id=self.__clientid)
            self.client.username_pw_set(self.__mqtt_name, self.__mqtt_pass)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client_connect()

    # 连接成功回调
    def on_connect(self, client, userdata, flags, rc):
        logging.info('万能开关mqtt开始订阅主题.')
        self.client.subscribe(self.topic)           # 订阅主题
        logging.info('万能开关mqtt完成主题订阅.')

    # 连接MQTT服务器
    def client_connect(self):
        self.client.connect_async(self.__host, self.__port, 60)     # 非阻塞模式
        self.client.loop_start()                                    # 非阻塞模式

    # 万能开关收到消息回调
    def on_message(self, client, userdata, msg):
        """收到mqtt消息，转发到插件 根据消息类型分析"""
        magstr = msg.payload.decode("utf-8")
        json_obj = json.loads(magstr)
        logging.debug('MQTT RECEIVE: %s' % json_obj)

        if type(json_obj) is dict and 'receive' in dict(json_obj).keys():
            if str(json_obj['receive']) == 'equipm':                # 接收端是设备
                if json_obj['type'] == 'online':
                    logging.info(json_obj)
                    self.write2db(json_obj)
                    self.say('万能开关设备已连接')

                elif json_obj['type'] == 'offline':
                    self.say('万能开关设备已断开')
                else:
                    self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data="GeneralSwith")
                    self.send(MsgType=MsgType.Text, Receiver='GeneralSwith', Data=json_obj)

    def publish(self, topic, msgbody):
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
        self.client.publish(topic, msgbody, qos=2)
       
    def Text(self, message):
        '''
        回调函数,收到插件发来的文本消息 转发到万能开关服务器
        {
            "Sender": Sender,
            "Receive": receive,
            "Data": {
                'deviceid':'设备ID',
                'data': {
                    'type':'switch',    开关类型，分为：switch-开关 / 
                    'pin': 14,          控制引脚
                    'state':state       状态
                }
            }
        }
        '''
        Sender = message['Sender']
        Data = message['Data']
        logging.info('万能开关收到控制中心消息: %s' % (str(Data)))

        if isinstance(Data, dict):
            if 'deviceid' in Data and 'data' in Data:
                receive = Data['deviceid']
                data = Data['data']
                send_json = {"sender":Sender, "receive":receive, "data": data}
                self.publish(self.topic, send_json)
                
    def write2db(self, jsontext):
        deviceid = jsontext['data']['deviceid']
        timestamp = time.time()
        db = sqlite3.connect(database=self.dbfile)
        create_tb_cmd = '''
        CREATE TABLE if not exists "list" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "devid" TEXT,
        "name" TEXT,
        "regtime" TEXT,
        "lasttime" TEXT,
        "offtime" TEXT
        );'''
        cursor = db.cursor()
        cursor.execute(create_tb_cmd)        
        cursor.execute("SELECT * FROM LIST WHERE devid='" + deviceid + "'")  
        intable = len(cursor.fetchall()) >= 1        
        if intable:
            cursor.execute("UPDATE LIST SET lasttime=? WHERE devid=?", (timestamp, deviceid))   
        else:
            cursor.execute("INSERT INTO LIST (devid,name,regtime,lasttime) VALUES (?,?,?,?)", (deviceid, deviceid, timestamp, timestamp))    
        cursor.close()
        db.commit()
