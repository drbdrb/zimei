# -*- coding: utf-8 -*-
import os
import re
import subprocess
import sys
import time
import wave

import pyaudio
from package.base import Base, log


class Bofang(Base):
    '''语音播放类'''

    # 命令行方式播放
    def __paly_linux_wav(self,name):
        child = subprocess.Popen('aplay -q {}'.format(name),shell=True)
        return child

    # Windows 环境下播放
    def __paly_windows_wav(self,name):
        ding_wav = wave.open(name, 'rb')
        ding_data = ding_wav.readframes(ding_wav.getnframes())
        audio = pyaudio.PyAudio()
        stream_out = audio.open(
            format=audio.get_format_from_width(ding_wav.getsampwidth()),
            channels=ding_wav.getnchannels(),
            rate=ding_wav.getframerate(), input=False, output=True)
        stream_out.start_stream()
        stream_out.write(ding_data)
        #time.sleep(0.2)
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()

        log.info('播放结束')

    def paly_wav(self,name):
        try:
            if self.mylib.typeof(name) !='str':
                return '参数1，设置播放录音的名字str类型'

            if name[-4:] != '.wav':
                return '参数1，播放录音格式.wav'

            return self.__paly_linux_wav(name)

        except Exception as bug:
            pass

    def play_mp3(self,nane):
        pass
