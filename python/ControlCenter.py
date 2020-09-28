#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: drbdrb
# @Date: 2020-01-03 09:09:04
# @LastEditTime: 2020-03-26 01:05:48
# @Description:  控制中心

import logging
import importlib
import os
import random
import json
import re
import sys
import time
from multiprocessing import Queue
from MsgProcess import MsgProcess, MsgType
from package.CacheFileManager import CacheFileManager
from package.mylib import mylib


class ControlCenter(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.msgQueue = msgQueue
        self.ProcessPool = list()     # 进程池
        self.plugTriggers = dict()    # 插件激活词
        self.lastSystemPlugin = None  # 最近,正在运行的系统插件    
        self.isGeekTalk = False       # 连续对话模式
        self.awakeresponse = list()
        self.AwakeInit()
        self.LoadAll()

    def LoadAll(self):
        '''控制中心启动各个模块和插件'''
        screen = logging.StreamHandler()
        logFile = logging.FileHandler(self.config['Logging']['File'], mode=self.config['Logging']['Mode'], encoding='utf-8')
        logging.basicConfig(level=self.config['Logging']['Level'],
                            format='%(asctime)s [%(module)s.%(funcName)s] %(levelname)s: %(message)s',
                            handlers=[screen, logFile])  
     
        # 加载各模块
        for (module, isEnable) in (self.config["LoadModular"]).items():
            if isEnable:
                package = r'package.' + module
                try:
                    package = importlib.import_module(package)
                except Exception as e:
                    logging.error("loading [%s] error %s " % (module, e))
                    continue
                try:
                    moduleClass = getattr(package, module)
                except Exception as e:
                    logging.error("loading [%s] error %s " % (module, e))
                    continue
                process = moduleClass(self.msgQueue)
                process.start()
                self.ProcessPool.append(process)  # 加入进程池
                if isEnable == 'Start':
                    logging.debug('send Start message to %s', module)
                    self.send(MsgType=MsgType.Start, Receiver=module)

        # 扫描并加载插件
        self.PluginScan()

        # 删除旧cache文件
        CacheFileManager.delfile()

        logging.info('所有进程创建完毕,数量: %d ' % len(self.ProcessPool))
        logging.info('向每个进程发送心跳消息,测试其回复。')
        for pro in self.ProcessPool:
            self.send(MsgType=MsgType.HeartBeat, Receiver=pro.name)

    def AwakeInit(self):
        '''唤醒初始化工作'''
        echofilePath = r'data/audio/echo'
        for root, dirs, files in os.walk(echofilePath):
            for f in files:
                fnames = os.path.splitext(f)
                if fnames[1] == '.wav':
                    echofile = os.path.join(root, f)
                    waittime = (os.path.getsize(echofile) / 32000) - 0.3
                    response = {'path': echofile, 'text': fnames[0], 'waittime': waittime}
                    self.awakeresponse.append(response)


    def Awake(self, message):
        '''被唤醒时自动执行'''
        logging.debug('唤醒')
        self.Silence()
        randarr = random.choice(self.awakeresponse)
        os.popen(r'aplay -q {}'.format(randarr['path']))
        time.sleep(randarr['waittime'])
        self.send(MsgType=MsgType.Start, Receiver='Record', Data=5)
        self.isGeekTalk = self.config["IsGeekMode"]
        if self.config['GPIO']['powersavetime'] > 0:
            os.system('sudo vcgencmd display_power 1 > /dev/null')

    def Start(self, message):
        '''处理用控制中心启动核心模块'''
        module = message['Data']
        if not module:
            return

        self.send(MsgType.Stop, Receiver=module)
        
        package = r'package.' + module
        try:
            package = importlib.import_module(package)
        except Exception as e:
            logging.error("loading [%s] error %s " % (module, e))
            return
        try:
            moduleClass = getattr(package, module)
        except Exception as e:
            logging.error("loading [%s] error %s " % (module, e))
            return
        process = moduleClass(self.msgQueue)
        process.start()
        self.ProcessPool.append(process)  # 加入进程池
        
    def Text(self, message):
        ''' 处理文本内容 调用相关插件 '''
        text = message['Data']
        if not text:
            return

        if text == '重启控制中心':
            self.ControlCenterQuit()
            return
        
        TriggerWords = [r'\b打开极客模式\b', r'\b开启极客模式\b', r'\b极客模式\b']
        if any(map(lambda trigger: re.search(trigger, text), TriggerWords)):
            self.config["IsGeekMode"] = True
            self.isGeekTalk = True
            msg = '极客模式已打开'
            self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=msg)
            self.send(MsgType.Text, Receiver='Screen', Data=msg)
            return

        TriggerWords = [r'\b关闭极客模式', r'\b退出极客模式', r'\b停止极客模式']
        if any(map(lambda trigger: re.search(trigger, text), TriggerWords)):
            self.config["IsGeekMode"] = False
            self.isGeekTalk = False
            msg = '极客模式已关闭'
            logging.info(msg)
            self.send(MsgType.Text, Receiver='SpeechSynthesis', Data=msg)
            self.send(MsgType.Text, Receiver='Screen', Data=msg)
            return

        TriggerWords = [r'\b关闭\b', r'\b退出\b', r'\b停止\b', r'\b停止录音']
        if self.isGeekTalk:
            if any(map(lambda trigger: re.search(trigger, text), TriggerWords)):
                self.isGeekTalk = False
                logging.info('停止连续对话')
                return

        # 系统关键词分析 暂停 继续 停止 发给运行中的系统插件
        sysTriggerDic = {r'\b停止\b': MsgType.Stop,
                         r'\b暂停\b': MsgType.Pause,
                         r'\b继续\b': MsgType.Resume}

        # print('系统关键词分析')
        for (word, action) in sysTriggerDic.items():
            if re.search(word, text) is not None:
                if self.lastSystemPlugin is not None:
                    self.send(action, Receiver=self.lastSystemPlugin)
                return

        # 普通关键词
        plugtext = mylib.ChineseNum2Arab(text)
        for trigger in self.plugTriggers.keys():
            if re.search('\\b' + trigger, plugtext) is not None:
                for plugin in self.plugTriggers[trigger]:
                    self.send(MsgType.Text, plugin, plugtext)
                    # notLoadTrigger = r'\b暂停\b|\b继续\b|\b停止\b|\b取消\b'
                    # if re.search(notLoadTrigger, plugtext) is None:
                    self.LoadPlugin(plugin)
                return
        
        # 没有任何激活词转最后一个插件处理
        last = self.config["LastDefaultPlugin"]
        self.send(MsgType.Text, Receiver=last, Data=text)

    def HeartBeat(self, message):
        """ 控制中心收到各模块心跳消息打印出来 """
        logging.info('Received [HeartBeat] message from [{}]'.format(message['Sender']))

    def JobsDone(self, message):
        if self.isGeekTalk:
            self.Silence()
            self.send(MsgType=MsgType.Start, Receiver='Record', Data=8)
            logging.debug('isGeekTalk so Record.')

    def QuitGeekTalk(self, message=None):
        ''' 退出连续对话模式 '''
        if self.config["IsGeekMode"]:
            self.config["IsGeekMode"] = False
            msg = '连续对话模式已关闭'
            logging.info(msg)

    def Silence(self, message=None):
        ''' 安静 停止一切音频活动 '''
        # soundPlugins = ['Music']
        # for plugin in soundPlugins:
        plugin = self.lastSystemPlugin
        if any(map(lambda p: p.name == plugin, self.ProcessPool)):
            self.send(MsgType=MsgType.Pause, Receiver=plugin)
        os.popen(r'sudo killall mpg123 > /dev/null 2>&1')

    def Stop(self, message):
        ''' 当控制中心收到各模块的退出消息 '''
        self.ProcessPool = list(filter(lambda p: p.name != message['Sender'], self.ProcessPool))        
        configfile = os.path.join("plugin", message['Sender'], 'config.json')
        if os.path.exists(configfile):
            with open(configfile) as f:
                pluginConfig = json.load(f)
                IsSystem = pluginConfig['IsSystem']
            if IsSystem:
                logging.debug('lastSystemPlugin set to None')
                self.lastSystemPlugin = None
        if self.lastSystemPlugin:
            logging.debug('Let lastSystemPlugin go on')
            self.send(MsgType=MsgType.Resume, Receiver=self.lastSystemPlugin)
        logging.info('[{}]已退出,当前进程池:{}'.format(message['Sender'], len(self.ProcessPool)))

    def ControlCenterQuit(self, message=None):
        ''' 退出控制中心 由于存在run.py会再次加载所以变相重启控制中心'''
        for pro in self.ProcessPool:
            self.send(MsgType=MsgType.Stop, Receiver=pro.name)
        time.sleep(2)
        super().Stop()
        os.system("sudo pkill -f awake")
        os.system("sudo pkill -f ControlCenter.py")

    def PluginScan(self, message=None):
        """ 扫描插件目录下所有的插件文件并提取其激活词到plugTriggers
        plugTriggers结构 {'激活词1': ['插件名'],'激活词2': ['插件名1,'插件名2'] , ...}
        如果插件配置为AutoLoader=true 即开机加载类型，就立即加载插件 """

        self.plugTriggers.clear()
        pluginpath = r'./plugin'
        dirs = os.listdir(pluginpath)
        configs = map(lambda d: os.path.join(pluginpath, d, 'config.json'), dirs)
        configs = filter(lambda f: os.path.exists(f), configs)
        for file in configs:
            with open(file) as fd:
                try:
                    pluginConfig = json.load(fd)
                except Exception as e:
                    logging.error("json file %s load error: %s " % (fd, e))
                    continue
                pluginName = pluginConfig['name']
                IsEnable = pluginConfig['IsEnable']
                TriggerWords = pluginConfig['triggerwords']
                # IsSystem = pluginConfig['IsSystem']
                AutoLoader = pluginConfig['AutoLoader']
                if IsEnable:
                    if AutoLoader:
                        self.LoadPlugin(pluginName)  # 如是插件是开机加载类型,现在加载
                    for trigger in TriggerWords:
                        self.plugTriggers.setdefault(trigger, list())
                        self.plugTriggers[trigger].append(pluginName)

        # 从长到短排列激活词，长激活词优先
        self.plugTriggers = dict(sorted(self.plugTriggers.items(), key=lambda x: len(x[0]), reverse=True))
        logging.info('所有插件激活词列表:')
        for (trigger, plugins) in self.plugTriggers.items():
            logging.info('%s -> %s' % (trigger, plugins))

    def LoadPlugin(self, message):
        """根据名称加载插件,接受两种方法，如果message是str 则直接加载此插件
        如果message是dict 则加载 message['Data'] """

        if isinstance(message, dict):
            pluginName = message['Data']
        else:
            pluginName = message
        if pluginName == 'ControlCenter':  # 控制中心无需加载.
            return

        # 根据插件名运行插件
        if all(map(lambda p: p.name != pluginName, self.ProcessPool)):  # 如果插件没有运行
            pluginDir = os.path.join(r'plugin', pluginName)
            configfile = os.path.join(pluginDir, 'config.json')
            if not os.path.exists(configfile):
                logging.error('插件[%s]没有config.json配置文件,加法加载!' % pluginName)
                return
            with open(configfile) as fd:
                pluginConfig = json.load(fd)
                IsEnable = pluginConfig['IsEnable']
                IsSystem = pluginConfig['IsSystem']
                AutoLoader = pluginConfig['AutoLoader']
                if not IsEnable:
                    logging.info('插件[%s]配置为不启用!' % pluginName)
                    return
                if AutoLoader == "Start":
                    self.send(MsgType=MsgType.Start, Receiver=pluginName)
                package = r'plugin.' + pluginName + '.' + pluginName
                try:
                    module = importlib.import_module(package)
                except Exception as e:
                    logging.error('插件[%s]加载失败! %s' % (pluginName, e))
                    return
                try:
                    pluginClass = getattr(module, pluginName)
                except Exception as e:
                    logging.error('插件[%s]加载失败! %s' % (pluginName, e))
                    return
                process = pluginClass(self.msgQueue)
                process.start()
                self.ProcessPool.append(process)  # 加入进程池
                if IsSystem:
                    self.lastSystemPlugin = pluginName
                logging.info('加载插件: [%s] ' % pluginName)


if __name__ == "__main__":
    cwd = os.getcwd()
    sys.path.append(cwd)
    sys.path.append(os.path.join(cwd, 'api'))
    sys.path.append(os.path.join(cwd, 'bin'))
    sys.path.append(os.path.join(cwd, 'package'))
    sys.path.append(os.path.join(cwd, 'include'))
    sys.path.append(os.path.join(cwd, 'module'))
    del cwd
    Center = ControlCenter(Queue())
    Center.start()
