import hashlib
import json
import multiprocessing as mp  # 多进程
import os
import re
import time
import urllib
from urllib.parse import urlparse

import requests

import _thread
import psutil
import pygame
from package.base import Base, log
from plugin import Plugin

# 当前播放歌ID
this_play_id = 0

class Qqmusic(Base):
    '''QQ音乐基本类'''

    def __init__( self, nei_conn ):
        #print('QQ音乐基本类启用', nei_conn )
        self.nei_conn = nei_conn

        #当前插件进程ID
        self.music_pid = os.getpid()

        #音乐缓存根目录
        self.music_path  = '/music/'
        self.music_cache = '/music/cache'
        if os.path.exists(self.music_cache)==False:
            os.system('sudo mkdir -p '+ self.music_cache)

        self.this_play = ''     #当前播放的歌曲
        self.this_key  = 0      #当前播放的歌曲ID

    #缓存音乐
    def cache_music(self, play_list, key):
        
        this_play = play_list[key]
        url       = this_play['url']
        md5_fname = this_play['hashname']
        mp3_file  = os.path.join(self.music_cache, md5_fname +'.wav')

        if os.path.exists(mp3_file)==False:
            if key==0 and this_play_id ==0:
       
                front_end( {'obj':'mojing','msg':'正在缓冲歌曲，请稍候……'})    
                os.popen("sudo aplay "+ os.path.join(self.config['root_path'], "data/yuyin/Buffering.wav"))
        
        
            result    = urlparse( url )
            m4afile   = result.path
            m4afile   = re.sub(r'\/','',m4afile)
            file_ext  = os.path.splitext(m4afile)[1]
            save_file = os.path.join(self.music_cache, md5_fname + file_ext)       #os.path.join(self.music_cache, m4afile)

            headers = {
                'Connection': "keep-alive",
                'Pragma': "no-cache",
                'Cache-Control': "no-cache",
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/72.0.3626.119 Safari/537.36",
                'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                'Referer': "https://y.qq.com",
                'Accept-Encoding': "gzip, deflate, br",
                'Accept-Language': "zh-CN,zh;q=0.9",
                'cache-control': "no-cache",
            }

            music = requests.get(url,headers=headers).content
            with open(save_file,'wb') as f:
                f.write(music)

            cmd = "ffmpeg -y -i "+ save_file +" "+ mp3_file
            #print(cmd)
            os.system(cmd)
            time.sleep(1)
            os.system('rm -f '+ save_file)
            time.sleep(1)
        return mp3_file
        
    #前端显示歌曲名称和演唱者
    def music_name_list(self,play_list,hashname):
        try:
            name = {}      
            for key in play_list:
                name[key['hashname']]=key['name']+" 演唱者:"+key['author']
       
            front_end( {'obj':'mojing','msg':'正在播放:'+ name[hashname]})
        except:
            pass
        
    #播放音乐
    def play_music(self):
        global this_play_id

        #print('当前播放ID', this_play_id )

        play_list = self.read_play_list()

        if this_play_id < 0:
            this_play_id = len(play_list) - 1

        # =======  开始缓存下一曲  =========
        next_key = this_play_id + 1
        if next_key >= len(play_list):
            next_key = 0

        self.p1 = mp.Process(
            target = self.cache_music,
            args = (play_list,next_key)
        )
        self.p1.start()
        # ============  END  ==============

        this_play = self.cache_music(play_list, this_play_id)

        self.music_name_list(play_list,this_play[len(self.music_cache)+1:-4])
        
        pygame.mixer.music.load(this_play)
        pygame.mixer.music.play()
        this_play_id = next_key     
        while pygame.mixer.music.get_busy():
            pass

        self.play_music()


    # 分析列表
    # 如查缓冲目录有对应的音乐文件优先播放
    def analy_list(self, play_list):
        i = 0
        is_file = ''        #是否有缓冲文件
        for key in play_list:
            md5_fname = key['hashname']
            mp3_file  = os.path.join(self.music_cache, md5_fname +'.wav')
            if os.path.exists(mp3_file):
                is_file = mp3_file
                break
            i += 1

        if is_file:
            return is_file,i
        elif i > 0:
            return self.cache_music(play_list, 0), 0


    #读取播放列表
    def read_play_list(self):
        this_play_list = os.path.join(self.music_path,'this_play_list.json')
        fstr = ''
        play_list = []
        with open(this_play_list, mode='r', encoding='utf-8') as f:
            fstr = f.read()

        #得到播放列表
        play_list = json.loads(fstr)
        return play_list

    #音乐主体入口
    def main(self):
        global this_play_id

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1)        #调整音量最多1

        #线程控制函数
        def th_control( pygame, nei_conn, music_pid):
            global this_play_id
            while True:
                enjson = nei_conn.recv()
                log.info('音乐收到通知', enjson )

                if type(enjson) is dict:
                    if enjson['control'] == 'pause':
                        pygame.mixer.music.pause()
                    elif enjson['control'] == 'unpause':
                        if enjson['newlist'] == 1:
                            pygame.mixer.music.stop()
                            this_play_id = 0
                        else:
                            pygame.mixer.music.unpause()
                    elif enjson['control'] == 'stop':
                        pygame.mixer.music.pause()
                        pygame.mixer.quit()
                        pygame.quit()
                        os.system('sudo kill -9 '+ str(music_pid))

                    elif enjson['control'] == 'next':
                        pygame.mixer.music.stop()

                    elif enjson['control'] == 'previous':
                        this_play_id -= 2
                        pygame.mixer.music.stop()



        _thread.start_new_thread( th_control, (pygame, self.nei_conn, self.music_pid) )

        # 读取当前播放列表
        play_list = self.read_play_list()

        #返回的是歌曲列表 内部是多个字典 需要解析内部的authon  name

        # 分析歌典列表
        self.this_play, self.this_key = self.analy_list( play_list )
        this_play_id = self.this_key
        if self.this_play:
            self.play_music()





# ==================================================================================================

class Music(Plugin,Base):
    '''音乐插件'''

    def __init__( self, public_obj ):
        global front_end
        self.public_obj = public_obj
        front_end = self.public_obj.sw.send_info
        # 进程通信
        self.nei_conn, self.wai_conn = mp.Pipe(False)

        #当前插件进程ID
        self.this_pid = os.getpid()

        #当前播放歌曲列表名称
        self.this_list_name = ''

        self.p2 = mp.Process(
            target = Qqmusic(self.nei_conn).main
        )
        self.p2.start()
        


    #插件入口
    def start(self, enobj):

        #print('插件入口',enobj, enobj['data'] )
        self.this_list_name = enobj['data']
        self.wai_conn.send({"control":"play"})
     
    #插件等待（暂时停止）控制
    def pause(self):
        self.wai_conn.send({"control":"pause"})

    #插件继续
    def resume(self, enobj={}):


        if str(self.this_list_name) != str(enobj['data']) and enobj['name']=='Music':
            self.wai_conn.send({"control":"unpause","newlist":1})
            self.this_list_name = enobj['data']
           

        elif enobj["trigger"] in ["下一曲","下一个","下一首"]:

            self.wai_conn.send({"control":"next"})
     


        elif enobj["trigger"] in ["上一曲","上一个","上一首"]:

            self.wai_conn.send({"control":"previous"})
        

        else:
            #继续播放
            self.wai_conn.send({"control":"unpause","newlist":0})


    #插件结束
    def stop(self, *enobj):
        self.wai_conn.send({"control":"stop"})
        #print('当前进程', self.this_pid)

        pro = psutil.Process( int(self.this_pid) )
        if pro:       #进程存在
            #停止进程下所有子进程
            for x in pro.children():
                pid_arr = re.findall(r'pid\=(\d+)', str(x), re.M|re.I)
                if pid_arr:
                    os.system('sudo kill -9 '+ str(pid_arr[0]) )
        os.system('sudo kill -9 '+ str(self.this_pid) )
        return False


    #重写插件默认事件
    def __del__(self):
        pass

if __name__ == "__main__":
    send_dict = {'state': True, 'data': '播放歌曲。', 'trigger': '播放', 'action': '', 'ptype': 'stay', 'name': 'Music', 'optype': 'start'}
    Music({}).start(send_dict)
