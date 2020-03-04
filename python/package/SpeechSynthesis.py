# -*- coding: utf-8 -*-
# @Autor: atlight
# @Date: 2019-12-29 13:34:16
# @LastEditTime: 2020-01-20 14:18:22
# @Description: 语音合成类，可以增加多家产品,暂实现百度语音识别

from MsgProcess import MsgProcess, MsgType
from package.BDaip import AipSpeech
from package.CacheFileManager import CacheFileManager
from hashlib import md5
import os
import logging


class SpeechSynthesis(MsgProcess):
    def Text(self, message):
        text = message['Data'] 
        if text and isinstance(text, str) and len(text) < 1024:
            logging.info('[%s] request Speech: %s' %(message['Sender'],text))           
            name = md5(text.encode('utf-8')).hexdigest() + r'.mp3'
            CachePath = r'runtime/soundCache'
            fileName = os.path.join(CachePath, name)
            if os.path.exists(fileName):
                self.playSound(fileName)
            else:
                self.BDSpeechSynthesis(text, fileName)
        # self.send(MsgType=MsgType.JobsDone, Receiver = message['Sender'])
  
    def BDSpeechSynthesis(self, text, fileName):
        APP_ID =  self.config['BDAip']['APP_ID']
        API_KEY =  self.config['BDAip']['API_KEY']
        SECRET_KEY =  self.config['BDAip']['SECRET_KEY']
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

        # 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
        # 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美
        # PER = 4
        # 语速，取值0-15，默认为5中语速     SPD = 5
        # 音调，取值0-15，默认为5中语调     PIT = 5
        # 音量，取值0-9，默认为5中音量      VOL = 5
        # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
        # AUE = 6
        #         
        try:
            auido = client.synthesis(text=text, options={'vol': 5, 'per': 4, 'aue': '3', 'cuid': self.CUID})
        except Exception as e:
            logging.error('语音合成失败,%s' % e)
        with open(fileName, 'wb') as f:
            f.write(auido)
        self.playSound(fileName)
              
    def playSound(self, fileName):
        '''播放音乐文件fileName 可能会实现一个player类 暂用mpg123 '''        
        CacheFileManager.add(fileName)        
        logging.debug('墦放音频')
        os.system(" mpg123  -q  {} ".format(fileName))
        # os.popen("sudo mpg123  -q  {}".format(fileName))
        # os.popen("sudo aplay -q {}".format(fileName))
