# -*- coding: utf-8 -*-
# @Author: drbdrb
# @Date: 2019-12-31 15:57:55
# @LastEditTime: 2020-01-12 17:19:39
# @Description: 本插件语音播报本机IP。因功能简单可作其它插件的写作参模板。
import os
from MsgProcess import MsgProcess, MsgType

        
class SayIp(MsgProcess):
    def Text(self, message):  
        ipAddrs = os.popen("hostname -I").read()    # 取IP地址
        if ipAddrs:                                 # 如果有IP
            msgstr = '当前IP为：' + ipAddrs
        else:
            msgstr = "没有网络链接"
        self.say(msgstr)                             # 语音和屏显IP地址

        # 语音交互最简例子
        self.say('是要再播报一次吗？请说\"是的\"或者\"不是\"!')        
        words = self.listen()
        if '是的' in words:
            self.say(msgstr)
        
        self.Stop()  # 报完IP即退出。

