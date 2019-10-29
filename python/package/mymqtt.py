#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import sys
import time

import package.include.paho.mqtt.client as mqtt
import package.include.paho.mqtt.publish as publish


class Mymqtt():
    """MQTT操作类"""

    __clientid = ''
    __mqtt_name = ''
    __mqtt_pass = ''

    def __init__(self, config ):
        self.bao = config['MQTT']
        self.__host = self.bao["server"]            # mqtt.16302.com
        self.__port = self.bao["port"]              # 1883
        self.__clientid = self.bao["clientid"]      # 设备id
        self.__mqtt_name = self.bao["mqttname"]     # 用户名
        self.__mqtt_pass = self.bao["mqttpass"]     # 密码

    def client_connect(self):
        client = mqtt.Client(self.__clientid)    # ClientId不能重复，所以使用当前时间
        client.username_pw_set(self.__mqtt_name, self.__mqtt_pass)  # 必须设置，否则会返回「Connected with result code 4」
        client.on_connect = self.on_connect             #连接成功回调
        client.on_message = self.on_message             #收到消息回调
        client.connect(self.__host, self.__port, 60)
        client.loop_forever()

    #连接成功回调
    def on_connect(self,client, userdata, flags, rc):
        topic = '/'+self.__clientid+'/sys/nav'
        client.subscribe(topic)        #订阅主题
        topic = '/'+self.__clientid+'/sys/admin'
        client.subscribe(topic)        #订阅主题
        del topic

    #收到消息回调
    def on_message(self,client, userdata, msg):
        topic = msg.topic
        magstr = msg.payload.decode("utf-8")
        json_obj = json.loads( magstr )
        if type(json_obj) is dict:
            '''是字典'''
            if str(json_obj['receive'])=="equipm":
                '''接收端是设备'''
                msgbody = json_obj['body']
                self.message_check(topic, msgbody)

        del topic,magstr,json_obj,msgbody


    #发布消息
    def on_publish(self, topic, neirong=''):
        publish.single(topic, neirong,
            qos = 2,
            hostname = self.__host,
            port = self.__port,
            client_id = self.__clientid +'_py',
            auth = {'username':self.__mqtt_name,'password':self.__mqtt_pass}
        )

    #发送导航消息
    def send_nav(self, txtjson ):
        if type(txtjson) is dict:
            topic = '/'+ self.__clientid +'/sys/nav'
            jsonstr = json.dumps(txtjson)
            self.on_publish( topic, jsonstr )


    '''
    * 发送管理状态反馈
    * receive   --      接收者： xiaocx / equipm 小程序 / 设备
    * action    --      管理事件：USER_REG: 用户注册
    * data      --      消息体
    '''
    def send_admin(self, receive, event, data):
        topic = '/'+ self.__clientid +'/sys/admin'
        info = {
            'sender': 'equipm',     #设备
            'receive': receive,     #接收者
            'body':{
                'action': event,
                'data': data  # 消息体
            }
        }
        jsonstr = json.dumps(info)

        self.on_publish( topic, str(jsonstr) )


    # 订阅消息回调处理
    def message_check(self, topic, msgbody ):
        if type(msgbody) is dict:
            sbobj ={
                'state': True,
                'enter': 'mqtt',
                'type': 'system',
                'optype': 'action',
                'msg': '获取成功',
                'data': msgbody
            }
            self.command_execution( sbobj )

    #入口函数
    def main(self, command_execution, public_obj ):
        self.command_execution = command_execution
        self.client_connect()
