#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from multiprocessing import Process  # 多进程
import os
import re
import sys
import time
from WebServer import WebServer


this_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(this_path+'/python/')

task_webser = 'WebServer.py'            # Web服务
task_webser_cmd = os.path.join(this_path, 'python/' + task_webser)
task_webser_cmd = 'sudo ' + task_webser_cmd

task_main = 'ControlCenter.py'           # 后端任务
task_main_cmd = os.path.join(this_path, 'python/' + task_main)
task_main_cmd = 'sudo ' + task_main_cmd

task_mojing = 'moJing'                     # 前端任务
task_mojing_cmd = os.path.join(this_path, 'app/' + task_mojing)         # 前端任务
task_run = os.path.basename(__file__)  # 监控任务


# 停止任务
def stop(task_name):
    taskcmd = 'ps ax | grep ' + task_name
    out = os.popen(taskcmd).read()               # 检测是否已经运行
    pat = re.compile(r'(\d+).+('+task_name+')')
    res = pat.findall(out)
    for x in res:
        pid = x[0]
        cmd = 'sudo kill -9 ' + pid
        out = os.popen(cmd).read()
    print('[\033[31m停止\033[0m] 任务成功！')


# 查询任务
def ps_ax(task_name):
    taskcmd = 'ps ax | grep ' + task_name
    out = os.popen(taskcmd).read()               # 检测是否已经运行
    pat = re.compile(r'(\d+).+('+task_name+')')
    res = pat.findall(out)
    if len(res) > 2:
        return True
    else:
        return False


# 开始启动
def start(run_file):      # 启动函数
    def run_fund(run_file):
        os.system('export DISPLAY=:0 && ' + run_file)
    Process(target=run_fund,args=(run_file,)).start()


# 启动Mojing前端
def start_mojing_app(is_debug=""): 
    os.system("sudo alsactl --file data/asound.state restore")  # 加载音量设置
  
    while True:
        is_task_mojing = ps_ax(task_mojing)
        if is_task_mojing is False:
            start(task_webser_cmd + is_debug)
            time.sleep(1)
            start(task_mojing_cmd + is_debug)     # 启动前端
            stop(task_main)
            time.sleep(3)
            start(task_main_cmd)                  # 启动后端
        time.sleep(3)


if __name__ == '__main__':
    is_debug = ''
    argv = ''
    if len(sys.argv) > 1:
        argv = sys.argv[1]

    if argv == 'stop':
        stop('awake')           # 语音唤醒
        stop('awakeRec')        # 提供socket录音的语音唤醒
        stop(task_webser)
        stop(task_main)
        stop(task_mojing)
        stop(task_run)

    elif argv == 'restart':
        stop(task_main)
        stop(task_mojing)

    if argv.lower() == 'debug':
        is_debug = " Debug"
        print("runing on debug mode..")

    # 检测自己有没有运行
    runcmd = 'ps ax | grep ' + task_run
    out = os.popen(runcmd).read()               # 检测是否已经运行
    pat = re.compile(r'(\d+).+(\/python\d?\s+\S+'+task_run+')')
    runres = pat.findall(out)
    if len(runres) > 1:
        exit()
    start_mojing_app(is_debug)
