# -*- coding: utf-8 -*-
# @Author: GuanghuiSun
# @Date: 2020-02-22 10:37:52
# @LastEditTime: 2020-03-01 23:06:37
# @Description:  录音服务

import webrtcvad
import os
import time
import logging
from threading import Thread
from MsgProcess import MsgProcess, MsgType
import package.VoiceRecognition as VoiceRecognition
import socket
from bin.pyAlsa import pyAlsa


class SocketRec:
    """ 直接通过在后台运行的awake唤醒程序发来的录音包来录音 """
    def __init__(self, buffSize=3200):        
        self.BindFilePath = '/tmp/Record.zimei'
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        if os.path.exists(self.BindFilePath):
            os.unlink(self.BindFilePath)
        self.server.bind(self.BindFilePath)
        # 根据后台awake录音参数调节 buffSize = frame*loop*2
        self.buffSize = buffSize  # 取决于 awake.ini中的 frames
        logging.debug("BindFilePath=%s buffSize=%d" % (self.BindFilePath, buffSize))

    def read(self):   
        data, address = self. server.recvfrom(self.buffSize)
        return data
    
    def close(self):
        os.unlink(self.BindFilePath)       


class Pyaudio:
    ''' 调用Pyaudio录音 '''
    def __init__(self, buffSize=3200):
        import pyaudio
        self.CHUNK = buffSize / 2
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000  # 16k采样率      
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(rate=RATE, channels=CHANNELS, format=FORMAT, input=True, frames_per_buffer=self.CHUNK)

    def read(self):
        return self.stream.read(self.CHUNK)
     
    def close(self):
        self.stream.close()
        self.pa.terminate()
      

class Record(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue=msgQueue)
        self.vad = webrtcvad.Vad(1)  # 语音检测库
        self.isReset = False
        self.currentRecThread = None  # 当前录音线程
        self.VoiceRecognition = VoiceRecognition.VoiceRecognition()

    def Start(self, message):
        logging.info('[%s] request Record' % message['Sender'])
        if self.currentRecThread and self.currentRecThread.is_alive():
            self.isReset = True
            self.send(MsgType.Text, Receiver='Screen', Data='请说，我正在聆听...')
            return
        os.popen('aplay -q data/audio/ding.wav')
        time.sleep(0.4) 
        self.currentRecThread = Thread(target=self.RecordThread, args=(message,))
        self.currentRecThread.start()         # 启动录音线程

    def is_speech(self, buffer):
        '''
        检测长度为size字节的buffer是否是语音
        webrtcvad 要求你的总CHUNK用时只能有三种 10ms 20ms 30ms
        在16000hz采样下，一个frame用时为 0.0625ms 所以只能选160 320 480
        对应字节数分别为:320,640,960
        '''
        size = len(buffer)
        RATE = 16000
        assert size >= 320  # 长度不能小于10ms
        # if size < 640:
        #    return self.vad.is_speech(buffer[0:320], RATE)
        setp = 320
        score = 0
        blocks = size // setp  # 将音频分割
        for i in range(blocks):
            score += self.vad.is_speech(buffer[i*setp:(i+1)*setp], RATE)
        # logging.debug("语音概率 {}/{} = {:.2f} buffer size = {}".format(score, blocks, score / blocks,size))
        return score / blocks

    def RecordThread(self, message):
        if self.config['RecSeclet'] == 'ScoketRec':
            stream = SocketRec(buffSize=4000)                                                    # 使用unix socket录音
        elif self.config['RecSeclet'] == 'pyAlsa':            
            stream = pyAlsa.pyAlsa()                                                             # 使用pyalsa.so录音       
        elif self.config['RecSeclet'] == 'Pyaudio':
            stream = Pyaudio(buffSize=4000)
        else:
            logging.error('未知录音配置 config.yaml')
            return
     
        NoSpeechCheck = 4           # 常量,参考frames大小而定
        MinSpeechCHUNK = 4          # 常量,参考frames大小而定
        MAXRECLAN = 5               # 最长录音时间,秒
        if message['Data']:
            MAXRECLAN = message['Data']
        NoSpeechCHUNK = 0
        Speech_CHUNK_Counter = 0
        lastData = None             # 前导音
        frames = list()
        record_T = time.time()

        # info = {'type':'mic',      类型：dev 设备
        #        'state': 'start'}  状态：start / stop / 1 / 0

        info = {'type': 'mic', 'state': 'start'} 
        self.send(MsgType=MsgType.Text, Receiver='Screen', Data=info)       # 显示mic
        info = {'type': 'mic', 'state': 1}
        # logging.info('开始录音...')
        while (time.time() - record_T < MAXRECLAN):
            info['state'] = ('1' if info['state'] == '0' else '0')            
            self.send(MsgType=MsgType.Text, Receiver='Screen', Data=info)   # 前端mic动画            
            if (self.isReset):
                logging.info('录音重置')
                frames.clear()                
                record_T = time.time()
                Speech_CHUNK_Counter = 0
                NoSpeechCHUNK = 0
                self.isReset = False                
            data = stream.read()
            frames.append(data)
            if self.is_speech(data) >= 0.6:
                if NoSpeechCHUNK >= NoSpeechCheck:
                    frames.insert(0, lastData)
                Speech_CHUNK_Counter += 1
                NoSpeechCHUNK = 0
            else:
                NoSpeechCHUNK += 1
            lastData = data
            if NoSpeechCHUNK >= NoSpeechCheck:
                if Speech_CHUNK_Counter > MinSpeechCHUNK:
                    break
                else:
                    Speech_CHUNK_Counter = 0
                    frames.clear()

        info = {'type': 'mic', 'state': 'stop'} 
        self.send(MsgType=MsgType.Text, Receiver='Screen', Data=info)  # 不显示mic
        stream.close()
        logging.info('录音结束')

        if Speech_CHUNK_Counter > MinSpeechCHUNK:
            os.popen('aplay -q data/audio/dong.wav')
            frames = frames[0: 1 - NoSpeechCheck]
            frames = b"".join(frames)
            text = self.VoiceRecognition.Start(frames)
            if text:
                self.send(MsgType.Text, Receiver='Screen', Data=text)
                self.send(MsgType=MsgType.Text, Receiver=message['Sender'], Data=text)
                return
        logging.info('无语音数据')
        self.send(MsgType=MsgType.JobFailed, Receiver=message['Sender'])
        self.send(MsgType.Text, Receiver='Screen', Data='无语音数据')
        self.send(MsgType.QuitGeekTalk, Receiver='ControlCenter')
