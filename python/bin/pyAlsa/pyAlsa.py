# -*- coding: utf-8 -*-
# @Author: GuanghuiSun
# @Date: 2019-12-29 01:23:51
# @LastEditTime: 2020-03-02 17:00:46
# @Description: 本程序调用 pyalsa.so录制音频 pyalsa是用c直接调用alsa


import ctypes
import os
import logging


class AlsaStruct(ctypes.Structure):
    _fields_ = [('device', ctypes.c_char_p),         # 设备名
                ('rate', ctypes.c_ulong),            # rate
                ('channels', ctypes.c_ulong),        # channels
                ('frames', ctypes.c_ulong),          # frames
                ('buffersize', ctypes.c_ulong)]      # buffer 返回值 为0 失败


class pyAlsa:
    ''' 本程序调用 pyalsa.so录制音频 '''
    def __init__(self, device="default", rate=16000, channels=1, frames=1600, showDebug=False):
        alsain = AlsaStruct(device=bytes(device, encoding="utf8"),
                            rate=rate,
                            channels=channels,
                            frames=frames,
                            buffersize=0)
        sopath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyalsa.so")
        self.libso = ctypes.cdll.LoadLibrary(sopath)
        init = self.libso.init
        init.argtypes = [AlsaStruct, ctypes.c_bool]
        init.restype = AlsaStruct        
        alsaout = init(alsain, showDebug)
        self.realArg = alsaout
        logging.debug("device=%s rate=%d channels=%d frames=%d buffersize=%d " 
                      % (alsaout.device, alsaout.rate, alsaout.channels, alsaout.frames, alsaout.buffersize))
        if alsaout.buffersize == 0 or rate != alsaout.rate or channels != alsaout.channels or \
           alsaout.buffersize != alsaout.frames * alsaout.channels * 2:
            logging.debug("\npyalsa.so init() failed !!! \ndevice=%s rate=%d channels=%d frames=%d buffersize=%d \n" 
                          % (alsaout.device, alsaout.rate, alsaout.channels, alsaout.frames, alsaout.buffersize))
            raise 'pyalsa.so init() failed !'
            return
        self.buffersize = alsaout.buffersize

    def read(self):
        self.libso.readsound.argtypes = [ctypes.c_char_p]
        self.libso.readsound.restype = ctypes.c_bool
        buffer = ctypes.create_string_buffer(b'\0', self.buffersize)
        ret = self.libso.readsound(buffer)
        # if not ret:
        # logging.error("Recording XRUN ERROR .")
        return buffer

    def close(self):
        self.libso.closesound()


if __name__ == "__main__":
    ''' 录音样例 3 秒   '''
    rec = pyAlsa()                           # 1 创建录音对像
    sounds = list()
    with open('record.pcm', 'wb') as f:
        for i in range(30):
            data = rec.read()                # 2 直接读即可
            sounds.append(data)
        f.write(b''.join(sounds))
    rec.close()                              # 3 关闭录音对像

