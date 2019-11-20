# -*- coding: utf-8 -*-
import multiprocessing as mp  # 多进程
import os
import time

import package.include.visual as visual
import RPi.GPIO as GPIO
from package.base import Base, log
from plugin import Plugin


class Probe_people(Base,Plugin):

    channel = 16
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(channel,GPIO.IN)

    def __init__(self, public_obj ): 
       
        log.info("人体探测启动")
        self.public_obj  = public_obj 
        self.start({})

    def success(self,data):
        try:
            if data:
                self.public_obj.uid.value = int(data["body"]['uid'])        
                self.public_obj.master_conn.send({'optype': 'return','type': 'system','state': True,'msg': '人脸识别','data':data["data"],'stop':True} ) 
            else:
                self.public_obj.master_conn.send({'optype': 'return','type': 'system','state': True,'msg': '人脸识别','data':"你好",'stop':True} )       
        except:
            self.public_obj.master_conn.send({'optype': 'return','type': 'system','state': True,'msg': '人脸识别','data':"你好",'stop':True} ) 

    #进程
    def main(self):
        try:
            self.hello = 0#记录主人是否存在#设置为1 就不会一开始和你打招呼   
            self.on1 = time.time()
            self.key =0

            while 1:
                self.key += GPIO.input(self.channel)
                #print( self.key,time.time())
                #刷新率
                time.sleep(1)
                #周期秒#可以设置检测周期 几分钟都可以。自定义
                if time.time() - self.on1 >=120:
                    #刷新计时时间
                    self.on1 = time.time()
                                       
                    if self.key !=0:
                        #print('主人还在')
                        self.key =0                                       
                    else:
                        #记录是否存在有人
                        #print('主人不在')
                        self.key =0 
                        self.hello = 0
                #发现有人存在，记录里也没有人就再次欢迎
                if self.key ==1 and self.hello == 0:
                    self.hello = 1
                    
                    #os.system("sudo aplay  -q "+ os.path.join(self.config['root_path'], "data/yuyin/Probe_people.wav"))
                    self.visual =visual.Visual()
                    self.visual.success =self.success
                    self.visual.main()
        except:
            #防止树莓派系统莫名其妙的错误
            log.info("人体探测"*10)
            time.sleep(1)
            self.main()

    #开始        
    def start(self, enobj):
        m = mp.Process(target = self.main )
        m.start()
                       
if __name__ == "__main__":
    Human_body_detection().main()      
