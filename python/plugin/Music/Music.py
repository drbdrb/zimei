# -*- coding: utf-8 -*-
# @Author: GuanghuiSun
# @Date: 2020-01-08 09:05:25
# @LastEditTime: 2020-01-20 10:14:11
# @Description:  音乐播放器 主要是从聊天机器处得到一串dict 解析下载播放

import random
import logging
import os
import re
import time
import urllib
from enum import Enum
from threading import Thread
import requests
import package.mplayer as mplayer
from MsgProcess import MsgProcess, MsgType
from package.CacheFileManager import CacheFileManager


class PlayState(Enum):
    Play = 1       # 播放
    Pause = 2      # 暂停
    Stop = 4       # 停止
    Buffering = 8  # 缓冲
    

class Music(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.playState = PlayState.Stop
        self.playlist = list()
        self.playindex = 0  
        self.player = None
        self.autoNextSongThread = None
        self.music_cache_path = "/music/cache"
        if not os.path.exists(self.music_cache_path):
            os.makedirs(self.music_cache_path)

    def Text(self, message):        
        data = message['Data']
        # 歌单格式: songList =[{'songname':name,'songurl':url},{...}...]

        if type(data) is list:  # 换歌单
            self.playlist = data
            self.playindex = 0
            self.Start()
            return

        if type(data) is str:  # 激活词分析
            Triggers = ['播放本地歌曲', '播放本机歌曲']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                self.playlist.clear()                
                for file in os.listdir(self.music_cache_path):
                    url = os.path.abspath(os.path.join(self.music_cache_path, file))
                    if os.path.isfile(url):
                        ext = os.path.splitext(file)[1]
                        name = os.path.splitext(file)[0]
                        if ext == '.mp3' or ext == '.m4a':
                            if 0.01 <= os.path.getsize(url) / 10 ** 6 <= 200:  # 大小在10kB~100MB
                                self.playlist.append({'songname': name, 'songurl': url})
                            else:
                                os.remove(url)
                random.shuffle(self.playlist)
                self.playlist = self.playlist[:15]
                self.Start()
                return
                       
            Triggers = ['暂停歌曲', '暂停播放']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                self.Pause()
                return

            Triggers = ['继续播放', '歌曲继续']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                self.Resume()
                return

            Triggers = ['停止播放', '停止歌曲', '歌曲停止']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                self.Stop()
                return

            Triggers = ['下一曲', '下一首', '下1曲', '下1首']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                self.playindex = (self.playindex + 1) % len(self.playlist)
                self.Start()
                return

            Triggers = ['上一曲', '上一首', '上1曲', '上1首']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                last = self.playindex - 1
                self.playindex = (last if (last >= 0) else (len(self.playlist) - 1))
                self.Start()
                return

            Triggers = ['播放', '切换']
            if any(map(lambda w: data.__contains__(w), Triggers)):
                pattern = r"(\d?\d)"
                index = re.findall(pattern, data)
                if index:
                    self.playindex = int(index[0]) % len(self.playlist)
                    self.Start()
                return

        elif type(data) is dict:
            if data['initstate'] == 'onLoad':
                self.sendMQTT()

    def Start(self, message=None):
        if self.player is None:
            self.player = mplayer.Player(args=("-slave -quiet -nolirc -vo null -ao alsa "))
            self.player.cmd_prefix = ' '

        if self.autoNextSongThread is None:
            self.autoNextSongThread = Thread(target=self.autoNextSong, args=())
            self.autoNextSongThread.start()
        
        if len(self.playlist) >= 1:
            file = self.cacheMusic(self.playindex, showinfo=True)
            CacheFileManager.add(file)
            self.player.loadfile(file)
            self.playState = PlayState.Play
            time.sleep(1)

            # 缓存歌曲列表的下三曲,如果有的话.
            for n in range(1, 4):
                nextPlayIndex = (self.playindex + n) % len(self.playlist)
                Thread(target=self.cacheMusic, args=(nextPlayIndex,)).start()
          
            self.sendMQTT()               
            self.consoleShow()

        else:
            text = '歌曲列表是空的'
            self.say(text)

    def Pause(self, message=None):
        if self.playState == PlayState.Play:
            os.system('clear')
            logging.info('Pause')            
            self.player.pause()
            self.playState = PlayState.Pause
                        
    def Resume(self, message=None):
        if self.playState == PlayState.Pause:
            self.player.pause()
            self.playState = PlayState.Play
            self.sendMQTT()
            self.consoleShow()
          
    def Stop(self, message=None):
        if self.playState != PlayState.Stop:
            os.system('clear')
            self.playState = PlayState.Stop
            self.player.stop()
            self.player.quit()                           
            super().Stop()

    def cacheMusic(self, index, showinfo=False):
        ''' 从指定的url下载歌曲返回完整的带有路径的歌名str  '''       
  
        url = self.playlist[index]['songurl']
        songname = self.playlist[index]['songname']

        if self.music_cache_path in url:    # 本地歌曲无需下载
            return url

        songFileM4a = os.path.join(self.music_cache_path, songname + '.m4a')
        if os.path.exists(songFileM4a):  # 检测音乐是否存在大小是否正常。
            if 0.01 <= os.path.getsize(songFileM4a) / 10 ** 6 <= 200:  # 大小在10kB~100MB
                return songFileM4a

        songFileMp3 = os.path.join(self.music_cache_path, songname + '.mp3')
        if os.path.exists(songFileMp3):  # 检测音乐是否存在大小是否正常。
            if 0.01 <= os.path.getsize(songFileMp3) / 10 ** 6 <= 200:  # 大小在10kB~100MB
                return songFileMp3

        # 从url下载
        if showinfo:          
            text = '缓冲歌曲: {}...'.format(songname)
            self.playState = PlayState.Buffering
            self.say(text, onlyForward=True, Receiver='Screen')
        result = urllib.parse.urlparse(url)
        m4afile = result.path
        m4afile = re.sub(r'\/', '', m4afile)
        file_ext = os.path.splitext(m4afile)[1]
        down_file = os.path.join(self.music_cache_path, songname + file_ext)
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
        content = requests.get(url, headers=headers).content
        with open(down_file, 'wb') as f:
            f.write(content)
            f.close()
        CacheFileManager.add(down_file)
        return down_file

    def autoNextSong(self):
        while True:
            time.sleep(0.5)      
            if self.playState == PlayState.Stop:
                logging.debug('Quit')
                return
            if self.playState == PlayState.Play and self.player.filename is None:
                self.playindex = (self.playindex + 1) % len(self.playlist)
                self.Start()
    
    def consoleShow(self):
        ''' 在控制台屏幕上模拟一个音乐播放器 '''
        os.system('clear')
        print('\033[2J \033[25A \033[78D')
        print('歌曲列表:')
        for (index, song) in enumerate(self.playlist):
            if self.playindex == index:
                print("\033[5;32;40m[*{}]:{} \033[0m".format(index, song['songname']))                      
            else:
                print("[{}]:{}".format(index, song['songname']))
    
    def sendMQTT(self):
        ''' 将当前播放状态和歌单发送到MQTT '''
        songnames = [song['songname'] for song in self.playlist]
        data = {"playindex": self.playindex, "PlayState": self.playState.name,
                'sound': self.getVolume(), 'playlist': songnames}                 
        self.send(MsgType.Text, Receiver='MqttProxy', Data=data)        
                
    def getVolume(self):        
        ''' 取得音量大小 ''' 
        info = os.popen("sudo amixer sget Speaker").read()
        patten = r'Front\sLeft:\sPlayback\s(\d+)\s\[(\d+)\%\]'
        varStr = re.search(patten, info, re.M | re.I)
        if varStr:
            realvol = int(varStr.group(2))
        else:
            realvol = 80
        import math
        vol = int(1.7972 * math.pow(2.718, 0.04 * realvol))
        return vol
