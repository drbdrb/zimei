# -*- coding: utf-8 -*-
# @Autor: atlight
# @Date: 2019-12-26 09:35:35
# @LastEditTime: 2020-01-22 14:32:04
# @Description: 屏幕显示的消息进程，只要实现Text消息响应即可。

from MsgProcess import MsgProcess, MsgType
from bin.SocketScreen import SocketClient
import logging

class Screen(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.sw = SocketClient()
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

            self.sw.send_info(info)
            return
                
        # 对Data词典解析
        if isinstance(Data, dict) and 'type' in Data.keys():
            if Data['type'] == 'text':
                self.Text(Data['msg'])
                return

            '''
            info = {
                'type':'mic',       // 类型：dev 设备
                'state': 'start'   // 状态：start / stop / 1 / 0
            }
            '''
            if Data['type'] == 'mic':
                self.sw.send(Data)
                return

            if Data['type'] == 'nav':       # 导航
                self.sw.send_nav(Data['data'])
                return

            if Data['type'] == 'dev':       # 网络状态图标
                self.sw.send_dev(Data['data'])
                return

            self.sw.send(Data)              # 用户自定义数据 直接发给前端
            logging.warning('未知格式，直接发送: %s ' % Data['data'])
          
