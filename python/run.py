#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# @Date: 2020-01-03 09:09:04
# @LastEditTime: 2020-03-26 10:05:48
# @Description:  启动和停止 ./run.py debug  ./run.py stop
import os
import subprocess
import sys
import time


def stop(pname):
    if processExist(pname):
        print('[\033[31m停止任务 {} 成功！\033[0m]'.format(pname))
        cmd = "sudo pkill -fe {}".format(pname)
        os.system(cmd)


def processExist(pname):
    ''' 查询pname进程是否存在 是则返回true '''
    query = 'sudo ps ax | grep {} | grep -v grep '.format(pname)
    out = os.popen(query).read()
    return out != ''


def init():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system("sudo alsactl --file data/conf/asound.state restore")  # 加载音量设置
    os.system("sudo amixer set Capture 70%")  # 设置话筒
    os.system("alsactl --file data/conf/asound.state restore")  # 加载音量设置
    os.system("amixer set Capture 70%")  # 设置话筒
    
    # 设定目录权限 特别是pi
    os.system("sudo chmod -R 0777 data")
    os.system("sudo chmod -R 0777 runtime")
    os.system("sudo chmod -R 0777 /music/")

    bak = "data/conf/configBAK.yaml"
    cfg = "config.yaml"
    if not os.path.exists(cfg) or os.path.getsize(cfg) < 10:       
        os.system('sudo cp -f %s %s ' % (bak, cfg))
        os.system('sudo chown pi.pi %s' % cfg)
        os.system('sudo chmod 0666 %s' % cfg)
        print("修复配置文件 %s ,以前配置丢失。 " % cfg)

    # 如果屏幕配置为不启动 则也不启动前端app
    from package.mylib import mylib
    mojing = mylib.getConfig()["LoadModular"]["Screen"]
    if mojing is False:
        global tasks
        tasks = tasks[1:]
        

tasks = [
    {"pname": "moJing",                     "cmd": "export DISPLAY=:0.0 & ../app/moJing", "sleep": 3},    # 前端必须在第一位
    {"pname": "WebServer.py",               "cmd": "sudo python3 WebServer.py", "sleep": 1},    
    {"pname": "ControlCenter.py",           "cmd": "python3 ControlCenter.py", "sleep": 1},
    {"pname": os.path.basename(__file__),   "cmd": __file__, "sleep": 1}]           # 自已必须在最后一位
  
if __name__ == '__main__':
    args = str(sys.argv[1:]).lower()
    if 'stop' in args:
        stop('awake')     # 语音唤醒
        stop('mplayer')
        for task in tasks:
            stop(task['pname'])

    if 'debug' in args:
        tasks[0]['cmd'] += " debug"
        tasks[1]['cmd'] += " debug"
        
    # {"pname": "mosquitto",                  "cmd": "mosquitto -d"},
    os.system("mosquitto -d")
    # 检测自己是否已运行
    isroot = 0
    if int(os.popen("id -u").read()) == 0:
        isroot = 1
    thisfile = os.path.basename(__file__)
    cmd = "sudo ps ax | grep {} | grep -v grep | wc -l".format(thisfile) 
    n = int(os.popen(cmd).read()) - isroot
    if n >= 2:
        print("\033[31m{}已经运行!  \033[0m结束任务用: ./{} stop".format(thisfile, thisfile))
        exit()

    init()  # 运行前初始化工作

    while True:
        for task in tasks:
            if not processExist(task['pname']):     
                print("\033[32mRun Task: %s\033[0m" % task['pname'])
                subprocess.Popen(args=task['cmd'], shell=True)
            time.sleep(task['sleep'])
