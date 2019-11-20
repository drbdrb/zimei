# -*- coding: utf-8 -*-
import os
import random
import re
import time

import package.include.baiduapi.hecheng as hecheng  # 百度语音合成（文字转语音）
import package.include.baiduapi.shibie as shibie  # 百度识别
import package.include.bofang as bofang  # 播放
import package.include.luyin as luyin  # 录音
from package.base import Base, log


'''
语音类
实现：录音 -> 保存本地 -> 上传百度语音识别 -> 返回识别后文字
'''
class Hecheng_bofang(Base):

    def __init__(self, is_snowboy, public_obj):
        self.yuyin_path = os.path.join(self.config['root_path'], 'data/yuyin')
        self.is_snowboy = is_snowboy

        self.hecheng = hecheng.Hecheng()
        self.hecheng.success = self.success
        self.hecheng.error = self.error

        self.bofang = bofang.Bofang()
        self.public_obj = public_obj

    def success(self,position):         #os.path.join(self.yuyin_path,"result.wav")
        is_snowboy_value = 0
        if self.reobj["state"]==False or ('stop' in self.reobj and self.reobj['stop'] is True):
            is_snowboy_value = 0
        else:
            is_snowboy_value = 2
            self.public_obj.master_conn.send({"optype":"snowboy"})
            
        chiproc = self.bofang.paly_wav( position )
        chiproc.wait()   #等待播放结束

        self.is_snowboy.value = is_snowboy_value

    def error(self, errtype = ''):
        if errtype == 'neterror':        #网络错误
            self.bofang.paly_wav( os.path.join(self.yuyin_path, "meiyou_wangluo.wav") )

    def main(self, reobj ):
        self.reobj = reobj
        if self.reobj["state"]==False:
            self.error( reobj )
        else:
            #合成语音并播放
            self.hecheng.main( reobj )


'''
录音+识别 类（实现：语音转文字）
'''
class Luyin_shibie(Base):

    def __init__(self):
        self.luyin = luyin.Luyin()
        self.luyin.success = self.luyin_success
        self.luyin.error = self.luyin_error
        self.timer = 5      #录音时长
     
    #全部转换成功执行（已在main函数中被重写）
    def success(self, json ):
        pass

    #录音成功 -> 进入百度识别
    def luyin_success(self,results):
        json = shibie.Shibie().main(results)
        self.success( json )

    #录音失败 -> 递归自己，继续调用自己工作
    def luyin_error(self,bug):
        log.info('出错继续录音',bug)
        self.luyin.main(self.timer, self.pyaudio_obj)

        #停止说话
    def stop_aplay(self):
        taskcmd = 'ps ax | grep aplay' 
        out = os.popen(taskcmd).read()               # 检测是否已经运行
        pat = re.compile(r'(\d+)\s+.+aplay.+\/python\/runtime\/hecheng\/',re.M|re.I)
        res = pat.findall(out)
        for x in res:
            cmd = 'sudo kill -9 '+ str(x)
            os.system(cmd)

    '''
    语音录音主函数
    参数：
        is_one      -- 是否为首次唤醒
        command_execution   --  语音全部操作成功
        pyaudio_obj --  录音对象
        public_obj  --  全局类对象
    '''
    def main(self, hx_chenggong, is_one, command_execution, pyaudio_obj, public_obj ):
        hx_chenggong.value = os.getpid()       #记录唤醒进程ID

        self.success = command_execution

        self.pyaudio_obj    = pyaudio_obj
        self.pyaudio_obj.sw = public_obj.sw

        self.yuyin_path = pyaudio_obj.yuyin_path

        #停止之前的播放声音
        self.stop_aplay()

        #如果是首次唤醒：执行魔镜应答声
        if is_one == 1:
            wozai = [
            {'text':'嗯','wav': 'zaina2.wav',"time":0.33},
            {'text':'我在','wav': 'zaina3.wav',"time":0.66}
            ]
            ints = random.randint(0,len(wozai)-1) 
            filearr = wozai[ ints ]

            #播放唤醒提示声
            play_cmd = 'aplay -q '+ self.yuyin_path +'/'+ filearr['wav']

            send_txt = {'init':1, 'obj':'mojing','msg': filearr['text']}
            self.pyaudio_obj.sw.send_info( send_txt )
            os.popen(play_cmd)

            time.sleep(filearr["time"])

            del send_txt,play_cmd,wozai,filearr,ints

        self.luyin.main(self.timer, self.pyaudio_obj)
