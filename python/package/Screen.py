# -*- coding: utf-8 -*-
# @Date: 2019-12-26 09:35:35
# @LastEditTime: 2020-01-22 14:32:04
# @Description: 屏幕显示的消息进程，只要实现Text消息响应即可。

import json
import logging
import re
import time
from threading import Thread

from bin.SocketScreen import SocketScreen
from MsgProcess import MsgProcess, MsgType

class Screen(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.StartServer()

    # 收到消息回调
    def on_message(self, ws):
        while True:
            try:
                response = ws.recv()
                mess = json.loads(response)
                if type(mess) is dict:
                    if 'MsgType' not in mess.keys():
                        mess['MsgType'] = 'Text'
                    mess['MsgType'] = re.sub(r'MsgType\.','', mess['MsgType'])
                    if str(mess['MsgType']) not in MsgType.__members__:
                        mess['MsgType'] = 'Text'
                    new_msgtype = MsgType[ mess['MsgType'] ]
                    self.send(MsgType = new_msgtype, Receiver = mess['Receiver'], Data = mess['Data'])
            except json.JSONDecodeError:
                continue
            except:
                self.re_connection()
                break
        exit()

    # 重连前端，如果连接成功则重启屏幕模块
    def re_connection(self):
        is_succ = self.sw.connection()
        if is_succ is True:
            self.send(MsgType.Start, Receiver='ControlCenter', Data='Screen')
            return True

        time.sleep(2)
        self.re_connection()

    # 启用屏幕通讯服务器
    def StartServer(self):
        self.sw = SocketScreen()
        self.sw.connection()
        self.openindex()
        p = Thread(target=self.on_message, args=(self.sw.sock,))
        p.start()

    # 打开默认首页
    def openindex(self):
        index_url = self.config['VIEW']['path'] + self.config['VIEW']['index']
        nav_json = {"event": "index", "url": index_url}
        self.sw.send_nav(nav_json)

    # 处理文本消息
    def Text(self, message):
        Data = message['Data']

        # 如果Data 是字符串
        if isinstance(Data, str):
            info = {
                'type': 'text',
                'init': 0,           # 是否为初始化唤醒
                'obj': 'mojing',     # 对象： zhuren / mojing  主人/魔镜
                'emot': '',          # 情感：
                'msg': Data          # 消息内容
            }

            if message['Sender'] == 'Record':  # 主人
                info['obj'] = 'zhuren'

            self.sw.on_send(info)
            return

        # 对Data词典解析
        if isinstance(Data, dict) and 'type' in Data.keys():
            if Data['type'] == 'text':
                self.Text(Data['msg'])
                return

            if Data['type'] == 'mic':
                self.sw.on_send(Data)
                return

            if Data['type'] == 'nav':       # 导航
                self.sw.send_nav(Data['data'])
                return

            if Data['type'] == 'dev':       # 网络状态图标
                self.sw.send_dev(Data['data'])
                return

            if Data['type'] == 'exejs':     # 执行前端JS代码
                self.sw.on_send(Data)
                return

            self.sw.on_send(Data)              # 用户自定义数据 直接发给前端
            logging.warning('未知格式，直接发送: %s ' % Data['data'])

    def Stop(self, message=None):
        super().Stop(message)  
