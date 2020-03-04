import package.paho.mqtt.client as mclient
from MsgProcess import MsgProcess, MsgType
import json
import os
import logging


class MqttProxy(MsgProcess):
    '''
    MQTT代理，接受从微信或网页发来MQTT消息，再转发给相关的服务插件。
    对插件或其它模块来说是透明的
    '''

    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.isconnect = False

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

        # 2.0方法 mqtt协议新字典,只要传送激活词就可以激活任意插件
        # {sender:'发送方', 'receive':'equipm', 'plugin':插件名, data='激活词'}
        jsonText = {
            "sender": "equipm",     # 设备
            "receive": "xiaocx",    # 接收者
            "plugin": plugin,       # 插件名
            "data": Data            # 数据
        }

        topic = '/' + self.__clientid + '/xiaocx/admin'
        self.publish(topic, json.dumps(jsonText))
        logging.debug('MQTT 2.0 SEND :%s %s' % (topic, jsonText))

    # 加载插件列表
    def load_pugin_list(self, data):
        pluginpath = r'./plugin'

        send_json = {}
        if data['type'] == 'getlist':
            plugin_list = []
            for filedir in os.listdir(pluginpath):
                if os.path.isdir(os.path.join(pluginpath, filedir)) and filedir != '__pycache__':
                    json_file = os.path.join(pluginpath, filedir, 'config.json')
                    with open(json_file, 'r') as f:
                        config_json = json.load(f)
                        # print( config_json )
                        item_dict = {
                            'name': config_json['name'],
                            'displayName': config_json['displayName'],
                            'icon': config_json['icon'],
                            'IsEnable': config_json['IsEnable']
                        }
                        plugin_list.append(item_dict)

            send_json = {
                "Sender": "equipm",
                "Data": {
                    "action": "PLUGIN_LIST",
                    "list": plugin_list
                }
            }
        elif data['type'] == 'getinfo':
            filedir = data['pugin'] + '/'
            json_file = os.path.join(pluginpath, filedir, 'config.json')
            plugin_info = {}
            with open(json_file, 'r') as f:
                config_json = json.load(f)
                plugin_info = {
                    'name': config_json['name'],
                    'displayName': config_json['displayName'],
                    'description': config_json['description'],
                    'icon': config_json['icon'],
                    'IsEnable': config_json['IsEnable'],
                    'control': '',
                    'initControl': 0,
                }
                if 'control' in config_json.keys():
                    plugin_info['control'] = config_json['control']
                if 'initControl' in config_json.keys():
                    plugin_info['initControl'] = config_json['initControl']

            if len(plugin_info) > 0:
                send_json = {
                    "Sender": "equipm",
                    "Data": {
                        "action": "PLUGIN_INFO",
                        "info": plugin_info
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
        topic = '/public/sys/admin'
        self.client.subscribe(topic)        # 订阅主题
        topic = '/'+self.__clientid+'/equipm/admin'
        self.client.subscribe(topic)        # 订阅主题
        logging.info('mqtt完成主题订阅.')
           
    # 收到消息回调
    def on_message(self, client, userdata, msg):
        """收到mqtt消息，转发到插件 根据消息类型分析"""
        magstr = msg.payload.decode("utf-8")
        json_obj = json.loads(magstr)
        logging.debug('MQTT RECEIVE: %s' % json_obj)

        if type(json_obj) is dict and 'receive' in dict(json_obj).keys():
            if str(json_obj['receive']) == 'equipm':  # 接收端是设备
                # 2.0方法 mqtt协议新字典,只要传送激活词就可以激活任意插件
                # {sender:'发送方', 'receive':'equipm', 'plugin':插件名, data='激活词'}
                Data = json_obj['data']
                if 'plugin' in dict(json_obj).keys():
                    pluginReceiver = json_obj['plugin']
                    self.send(MsgType=MsgType.Text, Receiver=pluginReceiver, Data=Data)                    
                    self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data=pluginReceiver)
                    return
                elif type(Data) is dict:
                    if 'action' in dict(Data).keys() and Data['action'] == 'PLUGIN_LIST':
                        self.load_pugin_list(Data)
                        return

    # 发布消息
    def publish(self, topic, msgbody):
        self.client.publish(topic, msgbody, qos=2)
