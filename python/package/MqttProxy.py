import include.mqtt.client as mclient
import sqlite3
from MsgProcess import MsgProcess, MsgType
import json
import os
import logging
import re
import copy
import time


class MqttProxy(MsgProcess):
    '''
    MQTT代理，接受从微信或网页发来MQTT消息，再转发给相关的服务插件。
    对插件或其它模块来说是透明的
    '''

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.isconnect = False
        self.dbfile = "./data/device.db"            # 管理数据库

        self.wnkg_default_plugin = 'GeneralSwith'   # 万能开关默认插件

        warp_path = self.config["MQTT"]["warp"]

        # Mqtt和微信小程序通讯主题
        file = os.path.join(warp_path,"topic.json")
        f = open(file)
        topic = json.load(f)
        f.close()
        self.subscribe = topic["subscribe"]
        self.pubscribe = topic["pubscribe"]

        # 发送消息体模板
        file = os.path.join(warp_path,"send.json")
        f = open(file)
        self.sendwarp = f.read()
        f.close()

        # 接收消息体模板
        file = os.path.join(warp_path,"receive.json")
        f = open(file)
        self.receivewarp = f.read()
        f.close()

        self.plugintemp = {}
        template_path = r'./data/conf/pluginconfig.json'
        f = open(template_path)
        self.plugintemp = json.load(f)
        f.close()

    def Start(self, message):
        if not self.isconnect:         
            self.isconnect = True
            self.getConfig()
            mqtt_conf = self.config['MQTT']
            self.__host = mqtt_conf["server"]            # mqtt.16302.com
            self.__port = int(mqtt_conf["port"])         # 1883
            self.__clientid = mqtt_conf["clientid"]      # 设备id
            self.__mqtt_name = mqtt_conf["mqttname"]     # 用户名
            self.__mqtt_pass = mqtt_conf["mqttpass"]      # 密码
            self.client = mclient.Client(client_id=self.__clientid)
            self.client.username_pw_set(self.__mqtt_name, self.__mqtt_pass)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client_connect()

    def Text(self, message):
        ''' 回调函数,收到插件发来的文本消息 转发到mqtt服务器 '''
        plugin = message['Sender']
        Data = message['Data']

        # 如果有'type'字段则为通知万能开关设备
        if 'type' in dict(Data).keys():
            jsonText = self.sendwarp.replace(r'%plugin%', plugin)
            jsonText = jsonText.replace(r'%receive%', 'wnkg')
            jsonText = jsonText.replace(r'%data%', json.dumps(Data))
            jsonText = json.loads(jsonText)

            devidTab = self.getDeviceId(plugin)
            for devid in devidTab:
                topic = '/'+ devid + '/wnkg/admin'

                self.publish(topic, json.dumps(jsonText, ensure_ascii=False))
                logging.debug('MQTT SEND topic:%s %s' % (topic, jsonText))
            return

        # 如果有‘action’字段则为通知小程序
        if 'action' in dict(Data).keys():
            jsonText = self.sendwarp.replace(r'%plugin%', plugin)
            jsonText = jsonText.replace(r'%receive%', 'xiaocx')
            jsonText = jsonText.replace(r'%data%', json.dumps(Data))
            jsonText = json.loads(jsonText)

            for pub in self.pubscribe:
                topic = pub.replace(r'%clientid%', self.__clientid)

                self.publish(topic, json.dumps(jsonText, ensure_ascii=False))
                logging.debug('MQTT SEND topic:%s %s' % (topic, jsonText))

    # 加载万能开关列表
    def load_generalswitch_list(self, data):

        # 获取扩展设备列表
        if data['type'] == 'getlist':
            SwitchTab = self.getDeviceList()
            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "GENERALSWITCH_LIST",
                    "list": SwitchTab
                }
            }
        
        # 获取单个扩展设备信息
        elif data['type'] == 'getinfo':
            deviceid = data['devid']
            line_arr = self.getDeviceInfo(deviceid)

            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "GENERALSWITCH_INFO",
                    "info": line_arr
                }
            }

        # 设置信息
        elif data['type'] == 'setvalue':
            set_data = data['setdata']
            self.setDeviceInfo(set_data)

        elif data['type'] == 'delete':
            devid = data['devid']
            self.delDevice(devid)
            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "GENERALSWITCH_LIST",
                    "info": {
                        'type': 'delete',
                        'staust': 1
                    }
                }
            }

        if len(send_json) > 0:
            self.Text(send_json)


    # 加载插件列表
    def load_pugin_list(self, data):
        pluginpath = r'./plugin'

        send_json = {}

        # 获取插件列表
        if data['type'] == 'getlist':
            plugin_list = []
            for filedir in os.listdir(pluginpath):
                if os.path.isdir(os.path.join(pluginpath, filedir)) and filedir != '__pycache__':
                    template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象

                    json_file = os.path.join(pluginpath, filedir, 'config.json')
                    if os.path.isfile(json_file) is False:
                        continue
                    config_json = {}
                    f = open(json_file, 'r')
                    config_json = json.load(f)
                    f.close()
                    if type(config_json) is dict and len(config_json)>0 and 'name' in dict(config_json).keys():
                        template_json.update(config_json)
                        append_json = {
                            "name": template_json['name'],
                            "IsEnable": template_json['IsEnable'],
                            "displayName": template_json['displayName'],
                            "icon": template_json['icon'],
                            "version": template_json['version']
                        }
                        plugin_list.append(append_json)

            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "PLUGIN_LIST",
                    "list": plugin_list
                }
            }
        elif data['type'] == 'getinfo':
            filedir = data['pugin'] + '/'
            template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象
            json_file = os.path.join(pluginpath, filedir, 'config.json')
            config_json = {}
            f = open(json_file, 'r')
            config_json = json.load(f)
            f.close()

            if len(config_json) > 0:
                template_json.update(config_json)
                send_json = {
                    "Sender": "equipm",
                    "Data": {
                        "action": "PLUGIN_INFO",
                        "info": template_json
                    }
                }
        if len(send_json) > 0:
            self.Text(send_json)

    def client_connect(self):
        self.client.connect_async(self.__host, self.__port, 60)  # 非阻塞模式
        self.client.loop_start()  # 非阻塞模式

    # 连接成功回调
    def on_connect(self, client, userdata, flags, rc):
        logging.info('mqtt开始订阅主题.')

        for sub in self.subscribe:
            topic = sub.replace(r'%clientid%', self.__clientid)

            logging.info("subscribe topic: %s" % topic)
            self.client.subscribe(topic)

        logging.info('mqtt完成主题订阅.')

    # 收到消息回调
    def on_message(self, client, userdata, msg):
        """收到mqtt消息，转发到插件 根据消息类型分析"""
        magstr = msg.payload.decode("utf-8")
        logging.debug('MQTT RECEIVE: %s' % magstr)

        json_obj = self.receivewarp.replace(r'%data%', magstr)
        json_obj = json.loads(json_obj)

        if type(json_obj) is dict:
            json_Data = json_obj['Data']
            json_Sender = json_obj['Sender']
            json_Receive = json_obj['Receive']

            # 万能开关代理处理
            if json_Receive == 'WnkgProxy':
                if json_Data['type'] == 'online':
                    self.write2db(json_Data)
                    self.say('万能开关设备已连接')
                    return
                if json_Data['type'] == 'offline':
                    self.say('万能开关设备已断开')
                    return
                
                Receive = self.getPluginName(json_Sender)
                if len(Receive) <= 0:
                    Receive = self.wnkg_default_plugin
                    self.send(MsgType=MsgType.Text, Receiver=Receive, Data=json_Data)
                    self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data=Receive)
                    return
                else:
                    for Receive_item in Receive:
                        self.send(MsgType=MsgType.Text, Receiver=Receive_item, Data=json_Data)
                        self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data=Receive_item)
                    return

                return

            # 小程序代理处理
            elif json_Receive == 'XiaocxProxy':
                if 'action' in dict(json_Data).keys():
                    if json_Data['action'] == 'PLUGIN_LIST':                # 加载插件列表
                        self.load_pugin_list(json_Data)
                        return
                    if json_Data['action'] == 'GENERALSWITCH_LIST':          # 加载万能开关列表
                        self.load_generalswitch_list(json_Data)
                        return

            self.send(MsgType=MsgType.Text, Receiver=json_Receive, Data=json_Data)
            self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data=json_Receive)
            return


    # 发布消息
    def publish(self, topic, msgbody):
        self.client.publish(topic, msgbody, qos=2)


    # ======================== 数据库操作 =============================

    # 记录到数据库
    def write2db(self, jsontext):
        deviceid = jsontext['deviceid']
        timestamp = time.time()

        create_tb_cmd = '''
        CREATE TABLE if not exists "list" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "devid" TEXT,
        "name" TEXT,
        "plugin" TEXT,
        "regtime" TEXT,
        "lasttime" TEXT,
        "offtime" TEXT
        );'''
        try:
            db = sqlite3.connect(database=self.dbfile)
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
            db.close()
        except:
            pass

    # 根据万能开关设备ID查找对应的插件名
    # 返回：插件名数组列表
    def getPluginName(self, deviceid):
        rs = []
        try:
            db = sqlite3.connect(database=self.dbfile)
            cursor = db.cursor()
            cursor.execute("SELECT devid,plugin FROM LIST WHERE devid='" + deviceid + "'")
            rs = cursor.fetchall()
            cursor.close()
            db.commit()
            db.close()
        except:
            rs = []

        PluginTab = []
        for row in rs:
            if row[1] != None and row[1] != '':
                PluginTab.append(row[1])

        return PluginTab

    # 根据插件名查找指定的万能开关设备ID
    # 返回：设备ID数组列表
    def getDeviceId(self, plugin):
        if plugin == self.wnkg_default_plugin:
            where = "plugin is null or plugin='"+ self.wnkg_default_plugin +"'"
        else:
            where = "plugin='"+ plugin +"'"
        rs = []
        try:
            db = sqlite3.connect(database=self.dbfile)
            cursor = db.cursor()
            cursor.execute("SELECT devid,plugin FROM LIST WHERE "+ where)
            rs = cursor.fetchall()
            cursor.close()
            db.commit()
            db.close()
        except:
            rs = []

        PluginTab = []
        for row in rs:
            if row[0] != None and row[0] != '':
                PluginTab.append(row[0])

        return PluginTab

    # 获取扩展设备列表
    def getDeviceList(self):
        rs = []
        try:
            db = sqlite3.connect(database=self.dbfile)
            cursor = db.cursor()
            cursor.execute("SELECT id,devid,name,plugin,lasttime FROM LIST")
            rs = cursor.fetchall()
            cursor.close()
            db.commit()
            db.close()
        except:
            rs = []
        
        SwitchTab = []
        for row in rs:
            plugin = row[3]
            if row[3] is None or str(row[3])=='None':
                plugin = self.wnkg_default_plugin
            item = {
                'id': row[0],
                'devid': str(row[1]),
                'name': str(row[2]),
                'plugin': str(plugin)
            }
            SwitchTab.append(item)
        
        return SwitchTab

    # 获取单个设备信息
    def getDeviceInfo(self, deviceid):
        rs = []
        try:
            db = sqlite3.connect(database=self.dbfile)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM LIST WHERE devid='" + deviceid + "' LIMIT 1")
            col_list = [tuple[0] for tuple in cursor.description]  #得到域的名字
            rs = cursor.fetchall()
            cursor.close()
            db.commit()
            db.close()
        except:
            rs = []

        line_arr = {}
        if len(rs) > 0:
            for i in range(len(col_list)):
                line_arr[col_list[i]] = rs[0][i]                     #添加到字典

        if line_arr['plugin'] is None or str(line_arr['plugin']) == 'None':
            line_arr['plugin'] = self.wnkg_default_plugin
        
        return line_arr

    # 设置设备信息
    def setDeviceInfo(self, setdata):
        try:
            db = sqlite3.connect(database=self.dbfile)
            dev_id = setdata['devid']
            set_info = setdata['info']
            cursor = db.cursor()
            for key,val in set_info.items():
                up_sql = "UPDATE LIST SET {}='{}' WHERE devid='{}'".format(key, val, dev_id)
                cursor.execute(up_sql)
            cursor.close()
            db.commit()
            db.close()
        except:
            pass

    # 删除设备
    def delDevice(self, devid):
        try:
            db = sqlite3.connect(database=self.dbfile)
            cursor = db.cursor()
            cursor.execute("DELETE FROM LIST WHERE devid='{}'".format(devid))
            cursor.close()
            db.commit()
            db.close()
        except:
            pass
