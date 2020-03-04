# -*- coding: utf-8 -*-
# @Author: GuanghuiSun
# @Date: 2019-12-31 15:00:28
# @LastEditTime: 2020-03-02 18:03:36
# @Description:  唤醒服务。换醒程序一般没有需要接收的消息，向控制中心发唤醒消息即可。
import os
import socket
from MsgProcess import MsgProcess, MsgType
from threading import Thread
import logging
import time
import subprocess
import re


class Awake(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.awakeThread = None
 
    def Start(self, message):
        if self.awakeThread is None:
            if self.config['AwakeEngine'] == 'XFAwake':                
                self.awakeThread = Thread(target=self.XFMonitorThread, args=())         
            elif self.config['AwakeEngine'] == 'snowboy':
                self.awakeThread = Thread(target=self.snowboyThread, args=())
            self.awakeThread.start()
            logging.debug(self.awakeThread)
          
    def snowboyThread(self):            
        path = os.path.join(os.getcwd(), r'bin/snowboy')
        os.path.join(path)
        from bin.pyAlsa import pyAlsa
        from bin.snowboy import snowboydetect
        resource = (os.path.join(path, 'common.res')).encode()
        model = (os.path.join(path, 'xiaoduxiaodu.umdl')).encode()
        sensitivity = 0.5
        detector = snowboydetect.SnowboyDetect(resource, model)
        detector.ApplyFrontend(True)
        sensitivity = (str(sensitivity) + ',') * detector.NumHotwords()
        detector.SetSensitivity(sensitivity.encode())
        stream = pyAlsa.pyAlsa()
        logging.info('snowboy唤醒已加载,提供socket录音:%s' % self.config['snowboy']['supplyRecord'])
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        while True:
            data = stream.read()
            status = detector.RunDetection(b''.join(data))
            if self.config['snowboy']['supplyRecord']:
                try:          
                    client.sendto(data, self.config['snowboy']['BindFile'])
                except Exception:
                    pass                # 没有接收方，直接放弃
            if status == -1:
                logging.error("Error initializing streams or reading audio data")
                return
            elif status == -2:
                # logging.debug('silence found')
                time.sleep(0.05)
                continue
            elif status == 0:
                # logging.debug('voice found')
                continue
            elif status >= 1:
                logging.debug('Hotword Detected!')      
                self.send(MsgType=MsgType.Awake, Receiver='ControlCenter')

    def XFMonitorThread(self): 
        allRunProg = str((os.popen('ps -aux ')).read())
        pattern = r"bin/XFawake/awake\b"
        result = re.search(pattern, allRunProg)   
        while not result:
            exefile = os.path.join(os.getcwd(), "bin/XFawake/awake")
            subprocess.Popen(args=exefile, cwd=os.path.dirname(exefile), shell=True, stdout=subprocess.DEVNULL)
            logging.debug("subprocess.popen bin/XFawake/awake")
            time.sleep(3)     
            allRunProg = str((os.popen('ps -aux ')).read())
            pattern = r"bin/XFawake/awake\b"    
            result = re.search(pattern, allRunProg)
    
        self.socketFile = "/tmp/awake.zimei"
        server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        if os.path.exists(self.socketFile):
            os.unlink(self.socketFile)
        server.bind(self.socketFile)
        logging.info('迅飞唤醒已加载')
        while True:
            data, address = server.recvfrom(256)
            data = data.decode('utf-8') + str(address)
            self.send(MsgType=MsgType.Awake, Receiver='ControlCenter')

    def Stop(self, message=None):
        os.system("sudo killall awake ")
        self.socketFile = "/tmp/awake.zimei"   
        if os.path.exists(self.socketFile):
            os.unlink(self.socketFile)          # 释放命名管道
        super().Stop(message)     
