import logging
import os
import re
import time
from threading import Thread
from urllib.request import Request, urlopen
import RPi.GPIO as GPIO
from MsgProcess import MsgProcess, MsgType
from bin.Device import Device
from bin.Setnet import Setnet
from package.data import data as db
from package.mylib import mylib


class Daemon(MsgProcess):
    ''' 守护进程初始化环境并监测网络连接CPU温度内存容量等内容'''
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.netStatus = False                                          # true为连网 false断网
        self.connectedTime = time.time()                                # 网络连网时间
        self.pin_fengshan_kg = self.config['GPIO']['fengshan_kg']       # 降温风扇开关 0 - 为关闭此功能
        self.pin_setnet = self.config['GPIO']['setnet_pin']             # 配网控制
        self.pin_detect_man = self.config['GPIO']['detect_man']         # 人体探测
        self.powersavetime = self.config['GPIO']['powersavetime']       # 节能时间
        self.detect_man_time = time.time()  # 探测到人的时间

        self.arr_setnet = []                                            # 配网按键控制
        Device.setSoundCard()
        self.u_list = db().user_list_get()                              # 用户列表
        self.showBind = True
        self.isSettingNet = False                                       # 是否正在配网中
        self.pin_fengshan_zt = 0
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_fengshan_kg, GPIO.OUT)
        GPIO.setup(self.pin_setnet, GPIO.IN)
        GPIO.setup(self.pin_detect_man, GPIO.IN)

    def showBindNav(self):
        ''' 显示用户绑定的二维码 '''
        if self.netStatus and self.showBind:
            self.config = mylib.getConfig()
            if self.u_list is False:
                clientid = self.config['httpapi']+'/xiaocx/dev/' + self.config['MQTT']['clientid']
                nav_json = {"event": "open", "size": {
                    "width": 380, "height": 380}, "url": "desktop/Public/bind_user.html?qr=" + clientid}
                data = {'type': 'nav', 'data': nav_json}
                self.send(MsgType.Text, Receiver='Screen', Data=data)
                self.showBind = False

    def detect_setnet(self):
        ''' 检测配网按键 '''
        # if not self.isSettingNet and self.netStatus is False:
        if not self.isSettingNet:
            st = GPIO.input(self.pin_setnet)
            if int(st) == 1:
                self.arr_setnet.append('1')
            else:
                self.arr_setnet.clear()

            if len(self.arr_setnet) >= 2:
                self.isSettingNet = True
                if self.config['initWifi'] == 'SoundWave':
                    self.send(MsgType.Stop, Receiver="Awake")                    
                    from bin.setWifi.soundSetNet import soundSetNet
                    soundSetNet()
                    return

                if self.config['initWifi'] == 'ApHot':
                    Setnet().main()
                    return
    
    def Start(self, message):
        ''' 起动守护线程 '''
        Thread(target=self.detectAll, args=(), daemon=True).start()

    def set_soundcard(self):
        ''' 检测驱动板 '''
        cardtext = os.popen("aplay -l").read()
        restr = r'card\s(\d)\:\swm8960soundcard'
        matc = re.search(restr, cardtext, re.M | re.I)
        cardnum = 0
        if matc:
            cardnum = matc.group(1)
        else:
            logging.warning('没有检测到驱动板')
            import tkinter
            import tkinter.messagebox
            root = tkinter.Tk()
            root.withdraw()
            tkinter.messagebox.showerror(title='警告', message='没有找到配套的驱动板,系统可能无法完整运行!!!')
            root.destroy()
            root.quit()
            return False
        
        # logging.debug('设置默认声卡')
        # alsa_conf = '/usr/share/alsa/alsa.conf'
        # f = open(alsa_conf, "r")
        # fstr = f.read()
        # f.close()

        # is_write = False
        # restr = r'^defaults.ctl.card\s+\d\s*$'
        # matc = re.search(restr, fstr, re.M | re.I)
        # if matc:
        #     fstr = re.sub(restr, "defaults.ctl.card " + str(cardnum), fstr, 1, re.M | re.I)
        #     is_write = True

        # restr = r'^defaults.pcm.card\s+\d\s*$'
        # matc = re.search(restr, fstr, re.M | re.I)
        # if matc:
        #     fstr = re.sub(restr, "defaults.pcm.card " + str(cardnum), fstr, 1, re.M | re.I)
        #     is_write = True

        # if is_write:
        #     fo = open(alsa_conf, "w")
        #     fo.write(fstr)
        #     fo.close()

    def detect_netstate(self):
        '''  监控网络状态 '''
        url = self.config['httpapi'] + r'/raspberry/ping.html'
        try:
            req = Request(url)
            f = urlopen(req, timeout=10)
            if f.getcode() == 200:
                # data = {'type': 'dev', 'data':  {"netstatus": 1}}
                # self.send(MsgType.Text, Receiver='Screen', Data=data)
                self.connectedTime = time.time()
                if not self.netStatus:
                    self.netStatus = True
                    data = {'type': 'dev', 'data':  {"netstatus": 1}}
                    self.send(MsgType.Text, Receiver='Screen', Data=data)
                    logging.info('网络已连接')
                    self.send(MsgType.Text, Receiver='Screen', Data='网络已连接')
                    if Device.online():                                 # 设备成功上线
                        self.showBindNav()                              # 显示绑定页
                        self.send(MsgType.Start, Receiver='MqttProxy')  # 启动mqtt
                return
        except Exception as e:
            logging.warning(e)
        if time.time() - self.connectedTime > 15:
            self.netStatus = False
            data = {'type': 'dev', 'data': {"netstatus": 0}}
            self.send(MsgType.Text, Receiver='Screen', Data=data)
            msg = '网络断开连接'
            logging.warning(msg)
            self.send(MsgType.Text, Receiver='Screen', Data=msg)

    def detect_cpuwd(self):
        ''' 监控CPU温度 '''
        # res = os.popen('vcgencmd measure_temp').readline()
        # wdg = re.match( r"temp=(.+)\'C", res, re.M|re.I)
        # if wdg.group(1):
        #    wd = float(wdg.group(1))
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
        wd = int(res) / 1000
        if wd >= 70:
            if self.pin_fengshan_zt == 0:
                self.pin_fengshan_zt = 1
                GPIO.output(self.pin_fengshan_kg, GPIO.HIGH)
                logging.info('起动CPU风扇')
        if wd < 50:
            if self.pin_fengshan_zt == 1:
                self.pin_fengshan_zt = 0
                GPIO.output(self.pin_fengshan_kg, GPIO.LOW)
                logging.info('关闭CPU风扇')
        return res
    
    def detect_man(self):
        ''' 人体探测 关闭屏幕节能 ''' 
        if GPIO.input(self.pin_detect_man):
            self.detect_man_time = time.time()
            os.system('sudo vcgencmd display_power 1 > /dev/null')
        else:
            if (self.powersavetime > 0) and (time.time() - self.detect_man_time >= self.powersavetime * 60):
                os.system('sudo vcgencmd display_power 0 > /dev/null')
                        
    def detectAll(self):
        time.sleep(5)       # 等待屏幕启动，以免丢失网络图标
        self.set_soundcard()
        ''' 无限循环依次执行allTasks中的任务。每个任务执行后睡眠一秒 '''
        allTasks = [
            'detect_netstate', 
            'detect_cpuwd',
            'detect_man',
            'detect_setnet']
        i = 0
        while True: 
            eval('self.'+allTasks[i]+'()')
            i += 1
            i %= len(allTasks)
            time.sleep(1)

