# -*- coding: utf-8 -*-
# @Date: 2019-12-29 13:34:16
# @LastEditTime: 2020-03-08 16:53:34
# @Description: 语音识别类，可以增加多家产品,暂实现百度语音识别
from MsgProcess import MsgProcess, MsgType


class VoiceRecognition(MsgProcess):
    ''' 语音识别转文字 '''

    def __init__(self, msgQueue):
        super().__init__(msgQueue)

        if self.config['ApiConfig']['VoiceRecognition'] == 'Baidu':
            from module.VoiceRecognition.baidu import baidu
            vr = baidu()
            self.Voicerecognition = vr.main
        
        if self.config['ApiConfig']['VoiceRecognition'] == 'Xunfei':
            from module.VoiceRecognition.xunfei import xunfei
            vr = xunfei()
            self.Voicerecognition = vr.main

    # 开始语音转文字识别过程
    def Voicerecognition(self, data):
        pass

    def Start(self, data):
        return self.Voicerecognition(data)