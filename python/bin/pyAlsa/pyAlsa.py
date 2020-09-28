# -*- coding: utf-8 -*-
# @Author: atlight
# @Date: 2019-12-29 01:23:51
# @LastEditTime: 2020-03-15 17:08:23
# @Description: 本程序调用 pyalsa.so录制音频 pyalsa是用c直接调用alsa


import ctypes
import os
import wave

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
        if showDebug:
            print("device= ", alsaout.device, "rate= ", alsaout.rate, "channels= ", alsaout.channels,
                  "frames= ", alsaout.frames, "buffersize= ", alsaout.buffersize)
        if alsaout.buffersize == 0 or rate != alsaout.rate or \
           alsaout.buffersize != alsaout.frames * alsaout.channels * 2:
            print("device= ", alsaout.device, "rate= ", alsaout.rate, "channels= ", alsaout.channels,
                  "frames= ", alsaout.frames, "buffersize= ", alsaout.buffersize)
            raise 'pyalsa.so init() failed !'
            return
        else:
            self.buffersize = alsaout.buffersize

    def read(self):
        self.libso.readsound.argtypes = [ctypes.c_char_p]
        self.libso.readsound.restype = ctypes.c_bool
        buffer = ctypes.create_string_buffer(self.buffersize)
        ret = self.libso.readsound(buffer)
        if not ret:
            print("Recording XRUN ERROR .")
        return buffer

    def close(self):
        self.libso.closesound()


if __name__ == "__main__":
    # 录音样例 5秒
    rec = pyAlsa(device="default", showDebug=True)             # 1 创建录音对像
    sounds = list()
    for i in range(30):
        data = rec.read()                                      # 2 直接读即可
        sounds.append(data)
        
    with wave.open('record.wav', 'wb') as wf: 	
        wf.setnchannels(1)                         
        wf.setsampwidth(2)                         
        wf.setframerate(16000)
        wf.writeframes(b''.join(sounds))
    rec.close()                                                    # 3 关闭音频对像

