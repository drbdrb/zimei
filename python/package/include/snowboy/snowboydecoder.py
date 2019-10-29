#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import pyaudio
import package.include.snowboy.snowboydetect as snowboydetect
import time
import wave
import os,sys
'''
import logging
logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
'''

TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")


class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    pass
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    '''
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()
    '''


class HotwordDetector(object):
    """
    用于检测麦克风输入流中是否存在由“decoder_model”指定的关键字

    :param decoder_model: 解码器模型文件路径，字符串或字符串列表
    :param resource: 资源文件的路径。
    :param sensitivity: 解码器灵敏度，浮点数列表的浮点数。
                        价值越大，越有意义译码器。如果提供空列表，则
                        将使用模型中的默认灵敏度。
    :param audio_gain: 将输入体积乘以这个因子。
    """
    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1):

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect( resource_filename=resource.encode(), model_str=model_str.encode() )
        self.detector.SetAudioGain(audio_gain)
        #此代码用于测试通用模型
        self.detector.ApplyFrontend(True)#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity*self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "decoder_model中的关键词数量 (%d) 和敏感 (%d) 不匹配" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer( self.detector.NumChannels() * self.detector.SampleRate() * 5)

        self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True,
            output=False,
            format=self.audio.get_format_from_width(self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback
        )

    def start(self, detected_callback=play_audio_file,interrupt_check=lambda: False,sleep_time=0.03):
        """
        启动语音检测器。对于每'sleep_time'秒，它都会检查
        用于触发关键字的音频缓冲区。如果检测到，则调用
        在detected_callback中对应的函数，可以是单个函数
        函数(单个模型)或回调函数列表(多个模型)。如果它返回，
        它还会调用每个循环的interrupt_check True，然后从循环中断开并返回。

        :param detected_callback: 函数或函数列表。项目的数量必须与“decoder_model”中的模型数量匹配。
        :param interrupt_check: 如果主循环需要停止，返回True的函数。
        :param float sleep_time: 每个循环等待的秒数。
        :return: None
        """
        if interrupt_check():
            #logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "错误: 你的模型中的关键词 (%d) 不匹配的数字是多少 " \
            "回调 (%d)" % (self.num_hotwords, len(detected_callback))

        #logger.debug("detecting...")

        while True:
            if interrupt_check():
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            ans = self.detector.RunDetection(data)
            if ans == -1:
                return
                #logger.warning(u"错误：初始化流或读取音频数据")
            elif ans > 0:
                message = "唤醒词:" + str(ans) + " 被检测到，时间: "
                message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                #logger.info(message)
                callback = detected_callback[ans-1]
                if callback is not None:
                    callback()

        #logger.debug("finished.")

    def terminate(self):
        """
        终止音频流。用户不能再次调用start()来检测。
        :return: 无
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
