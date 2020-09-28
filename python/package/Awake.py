import logging
import os
from threading import Thread

from MsgProcess import MsgProcess, MsgType


class Awake(MsgProcess):
    '''语音唤醒类'''
    
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.awakeThread = None
        self.socketFile  = "/tmp/zimei-awake.sock"
        self.awakeconfig = self.config['ApiConfig']['AwakeEngine']
 
    def Start(self, message):
        if self.awakeThread is None:
            if self.awakeconfig == 'XFAwake':            
                self.awakeThread = Thread(target=self.XFMonitorThread, args=())         
            elif self.awakeconfig == 'snowboy':
                self.awakeThread = Thread(target=self.snowboyThread, args=())

            self.awakeThread.start()
            logging.debug(self.awakeThread)

    def awakeSuccess(self):
        '''唤醒成功 - 回调使用'''
        self.send(MsgType=MsgType.Awake, Receiver='ControlCenter')


    def snowboyThread(self):
        '''snowboy唤醒模块'''
        from module.awake.snowboy import snowboy
        awak = snowboy()
        awak.awakeSuccess = self.awakeSuccess
        awak.main()

    def XFMonitorThread(self):
        '''讯飞唤醒模块'''
        from module.awake.xunfei import xunfei
        awak = xunfei()
        awak.awakeSuccess = self.awakeSuccess
        awak.main()
        
    def Stop(self, message=None):
        os.system("sudo killall awake ")
        if os.path.exists(self.socketFile):
            os.unlink(self.socketFile)          # 释放命名管道
        super().Stop(message)     
