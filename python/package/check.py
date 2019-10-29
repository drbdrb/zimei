import multiprocessing as mp  # 多进程
import os
import re
import time
from urllib.request import Request, urlopen

import psutil  # 检测内存
import RPi.GPIO as GPIO
from package.base import Base, log  # 基本类
from package.setnet import Setnet


class Check(Base):
    """设备检测类"""

    def __init__(self):
        self.is_bind = True         #是否启动用户绑定提示窗口
        self.onnet_time = 0         #网络断开时间
        self.netstatus  = False     #网络状态，True -- 通，False -- 不通

        #设置不显示警告
        GPIO.setwarnings(False)

        #设置读取面板针脚模式
        GPIO.setmode(GPIO.BOARD)
        self.pin_pingmo_kg   = self.config['GPIO']['pingmo_kg']                 # 设置屏幕控制脚
        self.pin_pingmo_zt   = self.config['GPIO']['pingmo_zt']['pin']          # 获取屏幕开关状态脚
        self.pin_pingmo_open = self.config['GPIO']['pingmo_zt']['open']         # 获取屏幕开关状态 1 - 高电平，0 - 低电平
        self.pin_fengshan_kg = self.config['GPIO']['fengshan_kg']               # 降温风扇开关 0 - 为关闭此功能
        self.pin_setnet      = self.config['GPIO']['setnet_pin']                # 配网控制
        self.pin_fengshan_zt = 0

        # self.pin_renti_tc    = self.config['GPIO']['renti_tc']['pin']           # 人体探测
        # self.pin_renti_max_time = self.config['GPIO']['renti_tc']['max_time']

        GPIO.setup(self.pin_pingmo_kg,GPIO.OUT)                                 # 设置屏幕控制脚为输出
        GPIO.setup(self.pin_pingmo_zt,GPIO.IN)
        #GPIO.setup(self.pin_renti_tc, GPIO.IN)
        GPIO.setup(self.pin_fengshan_kg,GPIO.OUT)

        GPIO.setup(self.pin_setnet,GPIO.IN)                                     # 配网控制

        # self.ren_nk_time = 0            # 人体离开时间
        self.is_op_screen = True        # 是否操作屏幕

        #计数器
        self.jishuqi = {
            'onnet_time': 0,            # 网络断开时间
            'start_net': True,          # 开始配网 0 -- 不启动，1 - 启动 2- 已启动
            # 'ren_nk_time': 0,           # 人体离开时间
            'pin_setnet_st':0,          # 配网按键脚状态
        }

    #启用检测是否有用户
    def enable_bind(self):
        if self.is_bind == True and self.netstatus is True:
            u_list = self.data.user_list_get()
            if self.mylib.is_empty(u_list):
                if self.config['MQTT']['clientid']:
                    clientid = self.config['httpapi'] +'/'+ self.config['MQTT']['clientid']
                    nav_json = {"event":"open","size":{"width":380,"height":380},"url":"bind_user.html?qr="+ clientid }
                    self.public_obj.sw.send_nav( nav_json )
                    self.is_bind = False
            else:
                self.is_bind = False

    #人体探测
    def detect_ren(self):
        return

        # if self.pin_renti_max_time == 0: return False
        # is_face = os.path.join(self.config['root_path'],'data/is_face')
        # NOW_TIME = int(time.time())                     # 当前时间
        # ctime = NOW_TIME
        # if os.path.isfile(is_face):
        #     ctime = int(os.stat(is_face).st_ctime)      # 获取文件创建时间

        # if GPIO.input(self.pin_renti_tc) == True:
        #     '''高电平：有人'''
        #     self.ren_nk_time  = 0               # 第一次检测人离开时间，置0
        #     self.is_op_screen = True

        #     if (NOW_TIME - ctime) > self.pin_renti_max_time:
        #         #self.screens.openclose_screen(1)
        #         os.remove(is_face)

        # else:
        #     '''人离开'''
        #     if self.ren_nk_time == 0:
        #         self.is_op_screen = True
        #         self.ren_nk_time = NOW_TIME     # 第一次检测人离开时间
        #     else:
        #         if (NOW_TIME - self.ren_nk_time) > self.pin_renti_max_time and self.is_op_screen:
        #             self.is_op_screen = False
        #             #self.screens.openclose_screen(0)


    #检测声卡
    def detect_cards(self):
        if re.search("wm8960", os.popen("cat /proc/asound/cards").read()) == None:
            return False
        else:
            print('有声卡')
            return True

    #检测摄像头
    def detect_video(self):
        if re.search("video0", os.popen("ls -al /dev/ | grep video").read()) == None:
            pass

    #检测内存
    def detect_memory(self):
        if int((psutil.virtual_memory()[1]/1000)/1000) < 200:
            print('内存过低')

    #监控CPU温度
    def detect_cpuwd(self):
        res = os.popen('vcgencmd measure_temp').readline()
        wdg = re.match( r"temp=(.+)\'C", res, re.M|re.I)
        if wdg.group(1):
            wd = float(wdg.group(1))
            if wd >= 70:
                if self.pin_fengshan_zt == 0:
                    self.pin_fengshan_zt = 1
                    GPIO.output( self.pin_fengshan_kg, GPIO.HIGH )

            if wd < 50:
                if self.pin_fengshan_zt == 1:
                    self.pin_fengshan_zt = 0
                    GPIO.output( self.pin_fengshan_kg, GPIO.LOW )
        del res,wdg,wd

    # 监控网络状态
    def detect_netstate(self):
        url = self.config['httpapi'] +'/raspberry/ping.html'
        net_st = {'netstatus':0}
        try:
            req = Request(url)
            f = urlopen(req, timeout = 2)
            if f.getcode() == 200:
                #print('通')
                self.netstatus = True
                net_st = {'netstatus':1}
                self.jishuqi['onnet_time'] = 0
            else:
                #print('不通')
                self.netstatus = False
                self.jishuqi['onnet_time'] += 1
                net_st = {'netstatus':0}
            del req,f
        except:
            #print('不通')
            self.netstatus = False
            self.jishuqi['onnet_time'] += 1
            net_st = {'netstatus':0}

        self.public_obj.sw.send_devstate( net_st )


    #检测配网
    def detect_setnet(self):
        st = GPIO.input(self.pin_setnet)
        if int( st )==1:
            if self.jishuqi['pin_setnet_st'] >= 5:
                if self.jishuqi['start_net']==True and self.netstatus==False:
                    self.jishuqi['start_net'] = False
                    Setnet().main()
            else:
                self.jishuqi['pin_setnet_st'] +=1
        else:
            self.jishuqi['pin_setnet_st'] = 0



    # 初始化默认配置
    def default_config(self):
        pass
        #屏幕控制类
        #self.screens = screens.Screen(self.public_obj)
        #self.screens.openclose_screen(1)        # 初始化打开屏幕

    #开始启动
    def start(self):
        self.default_config()       #初始化默认配置

        while True:
            ss = time.strftime("%S", time.localtime())
            yu = int(ss) % 5
            if yu == 0:
                self.detect_ren()
            elif yu == 1:
                self.enable_bind()
            elif yu == 2:
                self.detect_cpuwd()
            elif yu == 3:
                self.detect_netstate()

            self.detect_setnet()

            time.sleep(1)


    def main(self, public_obj):
        log.info('启动监视进程')
        self.public_obj = public_obj
        #启动监视进程
        mp.Process(target=self.start).start()
