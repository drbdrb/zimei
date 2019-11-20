import math
import os
import re
import time

import package.mymqtt as mymqtt  # mqtt服务（网络神经）
from package.base import Base  # 基本类
from plugin import Plugin


class Yinliang():
    '''设置系统音量'''

    # 整数的四舍五入
    def l_45(self,ints):
        ints , new= int(ints),10
        #取最后一个值
        have = int(str(ints)[-1:])
        if have >=5:
            ints -= have
            ints += 10
        else: ints -= have
        del new
        return ints

    '''
    判断声卡是否有声音
    返回:
        1   -- 有声音
        0   -- 没声音
    '''
    def is_voice(self):
        cmd = 'lsmod | grep -i snd_soc_wm8960_soundcard'
        cmd_ret = os.popen(cmd).read()

        restr = r'snd_soc_wm8960_soundcard\s+\d+\s+(\d)'
        math  = re.search(restr, cmd_ret,  re.M|re.I)
        if math != None:
            if int( math.group(1) ) <= 6:
                return 0
            else:
                return 1
        return 0

    # 获取音量
    def get_volume(self):
        huoqu_os = os.popen("sudo amixer sget 'Speaker'").read()
        restr = r'Front\sLeft:\sPlayback\s(\d+)\s\[(\d+)\%\]'
        rema = re.search(restr, huoqu_os, re.M|re.I)
        jieguo = 80
        if rema:
            jieguo = rema.group(2)
        #通过y = 1.7972 * e^(0.04 * x) x为填入的音量，y为实际音量 这个公式计算出实际音量。
        return int(1.7972 * math.pow(2.718, 0.04 * int(jieguo)))

    # 设置音量
    def set_volume(self,val = 60):
        y = 24.979 * math.log(val) - 14.581
        os.system("sudo amixer set Speaker {}%".format(y))

    # 设置音量入口
    # size_text -- 音量大小
    def main(self, size_txt = 60):
        try:
            #自定义声音时size_txt为字符串类型
            if type(size_txt) is str : size_txt = int(size_txt)

            if size_txt <20:
                self.set_volume(20)
                return {'state':True,'data': "音量已经最小了",'msg':'音量已经最小了','stop':True}

            elif size_txt >=20 and size_txt <100:
                self.set_volume(size_txt)
                data_val = ''
                if self.is_voice() <= 0:
                    data_val = '音量已设置为{}'.format(size_txt)
                return {'state':True,'data':data_val,'msg':data_val,'stop':True}

            elif size_txt >=100:
                self.set_volume(100)
                return {'state':True,'data': "音量已经最大了",'msg':'音量已经最大了','stop':True}

        except:return {'state':True,'data': "没听清你说音量设置多少呢",'msg':'无知音量值','stop':True}

class Screens():
    '''屏幕控制类'''

    #设置开关屏幕
    def set_screen(self, val = 1 ):
        os.system('sudo vcgencmd display_power ' + str(val))

    #获取屏幕开关状态
    def get_screen(self):
        st = os.popen('sudo vcgencmd display_power').read()
        starr = st.strip().split('=')
        if str(starr[1])=='1':
            return '1'
        else:
            return '0'

        #旋转屏幕
    def get_rotate(self):
        config = '/boot/config.txt'
        f = open(config,"r")
        fstr = f.read()
        f.close()

        restr = r'^display_rotate\s*=\s*(\d)'
        rotate_val = 0
        rema = re.search(restr, fstr, re.M|re.I)
        if rema:
            rotate_val = rema.group(1)
        
        return rotate_val

    #旋转屏幕
    def rotate_screen(self,val = 0):
        config = '/boot/config.txt'
        f = open(config,"r")
        fstr = f.read()
        f.close()

        restr = r'^display_rotate\s*=\s*(\d)'
        rema = re.search(restr, fstr, re.M|re.I)
        if rema:
            new_api = 'display_rotate='+ str(val)
            fstr = re.sub(restr, new_api, fstr, 1, re.M|re.I )
        else:
            new_api = 'display_rotate='+ str(val)
            fstr += "\n"+ str(new_api) +"\n"
        
        fo = open(config, "w")
        line = fo.write( fstr )
        fo.close()
        del line,config,fo,rema,restr

        os.system('sudo reboot')

class Device(Base,Plugin):
    """设备管理类"""

    def __init__(self, public_obj):
        self.public_obj = public_obj
        self.Mqtt = mymqtt.Mymqtt(self.config)
        self.Yinliang = Yinliang()
        self.Screens  = Screens()

    # 获取设备IP
    def get_ip_address(self):
        re_json = []

        restr = r'inet\s+([\d+\.]+)\s+'

        eth0ip = os.popen('ifconfig eth0').read()
        matc = re.search( restr, eth0ip, re.M|re.I )
        if matc!=None:
            ethjson = {
                'devname':'eth0',
                'name':'有线网卡',
                'ip': str(matc.group(1))
            }
            re_json.append( ethjson )

        wlanip = os.popen('ifconfig wlan0').read()
        matc = re.search( restr, wlanip, re.M|re.I )
        if matc!=None:
            ethjson = {
                'devname':'wlan0',
                'name':'无线网卡',
                'ip': str(matc.group(1))
            }
            re_json.append( ethjson )

        return re_json

    #设备信息
    def device_s(self, data):
        body_json = {
            "code":"9999",
            "info":{
                "screen":"屏幕初始化状态失败" ,
                "screenrotate":0,
                "sound": "获取当前设备音量失败",
                "devip": {},
                "weathcity": {}
            }
        }

        try:
            have_volume = self.Yinliang.get_volume()

            #返回单个声音状态
            if data["data"]["state"] == "volume":
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"sound": str(int(have_volume))}})
                return {'state':True,'data': "",'msg':'','type':'system','stop':True}
            
            #获取屏幕状态
            have_screen = self.Screens.get_screen()

            #获取屏幕方向值
            screen_rotate = self.Screens.get_rotate()

            #返回单个屏幕状态
            if data["data"]["state"] == "screen":
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', { "code":"0000","info":{"screen":have_screen }})
                return {'state':True,'data': "",'msg':'','type':'system','stop':True}

            #获取全部状态
            if have_volume and have_screen and data["data"]["state"] == "all":
                # 设备IP信息
                dev_ip = self.get_ip_address()

                #天气预报默认城市信息
                data_config = self.data.getconfig()
                location = data_config['LOCATION']
                weathcity = {
                    'city': str(location['city']),
                    'city_cnid': str(location['city_cnid'])
                }

                body_json = {
                    "code":"0000",
                    "info":{
                        "screen":have_screen ,
                        "screenrotate": screen_rotate,
                        "sound": str(int(have_volume)),
                        "devip": dev_ip,
                        "weathcity": weathcity
                    }
                }
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', body_json )

                return {'state':True,'data': "微信小程序已连接",'msg':'','type':'system','stop':True}
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', body_json)
                return {'state':True,'data': "微信小程序获取设备信息失败。",'msg':'获取全部状态失败','type':'system','stop':True}
        except OSError as err:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_STATE', body_json)
            return {'state':True,'data': "微信小程序获取设备信息失败。",'msg':'系统级别错误'+str(err),'type':'system','stop':True}

    # ===============================【设置音量】Start ===================================

    #设置音量
    def device_volume(self,name):
        try:
            set_value = int(name['data']['value'])
            have = self.Yinliang.main(set_value)
            if have:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"0000","msg":set_value })
                have['state'] = True
                have['stop'] = True
                return have
            else:
                self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})
                return {'state':True,'data': "设置声音失败",'msg':'','type':'system','stop':True}
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_VOLUME',{"code":"9999","msg":"设置声音失败"})
            return {'state':True,'data': "设置声音失败",'msg':'','type':'system','stop':True}

    # ===============================【设置音量】End ===================================

    # ===============================【屏幕设置】Start ===================================
    # 旋转屏幕
    def device_rturn(self,name):
        try:
            set_value = int(name['data']['value'])
            self.Mqtt.send_admin('xiaocx', 'DEVICE_RTURN', { "code":"0000"})
            self.Screens.rotate_screen(set_value)
        except:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_RTURN', { "code":"9999","msg":"设置屏幕方向失败"})

    #打开和关闭屏幕
    def device_screen(self,name):
        have = name['data']["value"]
        if have == "0" or have == 0:
            self.Screens.set_screen(0)
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕关闭"})
            return {'state':True,'data': "屏幕已经关闭",'msg':'屏幕已经关闭','stop':True}

        elif have == "1" or have == 1:
            self.Screens.set_screen(1)
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"0000","msg":"屏幕打开"})
            return {'state':True,'data': "屏幕已经打开",'msg':'屏幕已经打开','stop':True}

        else:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_SCREEN',{"code":"9999","msg":"操作屏幕失败"})
            return {'state':True,'data': "屏幕操作失败",'msg':'','type':'system','stop':True}

    # ===============================【屏幕设置】End ===================================
            
    #修改天气预报默认城市
    def device_city(self,name):
        data = name['data']
        if type(data) is dict:
            self.data.up_config({"key":"city_cnid",'value':data['cnid']})
            self.data.up_config({"key":"city",'value':data['name']})
            self.Mqtt.send_admin('xiaocx', 'DEVICE_CITY',{"code":"0000","msg":"修改天气预报默认城市成功"})
            self.public_obj.sw.send_nav({"event" : "close"})
            time.sleep(1)
            self.public_obj.sw.send_nav({"event" : "close"})
            time.sleep(1)
            return {'state':True,'data': "修改天气预报默认城市为"+ str(data['name']) ,'msg':'','type':'system','stop':True}
        else:
            self.Mqtt.send_admin('xiaocx', 'DEVICE_CITY',{"code":"1001","msg":"修改天气预报默认城市失败"})
            return {'state':True,'data': "修改天气预报默认城市失败",'msg':'','type':'system','stop':True}


    #入口
    def start(self,name):

        #设置音量
        if name["action"] == "DEVICE_VOLUME":
            # 如果有触发词，即是语音控制
            if 'trigger' in name.keys():
                shuru = name['trigger']
                if shuru.count("最大")>=1:
                    name['data'] = {'value':100}

                elif shuru.count("最小")>=1:
                    name['data'] = {'value':20}

                elif shuru.count("小点")>=1 or shuru.count("小一点")>=1 or shuru.count("小一些")>=1 or shuru.count("好大")>=1 :
                    set_val = self.Yinliang.get_volume() - 10
                    set_val = self.Yinliang.l_45(set_val)
                    name['data'] = {'value':set_val}

                elif shuru.count("大点")>=1 or shuru.count("大一点")>=1 or shuru.count("大一些")>=1 or shuru.count("好小")>=1:
                    set_val = self.Yinliang.get_volume() + 10
                    set_val = self.Yinliang.l_45(set_val)
                    name['data'] = {'value':set_val}

                else:
                    ints = '60'
                    matchObj = re.findall( r'(\d+)', shuru, re.M|re.I)
                    if len(matchObj)>0:
                        ints = matchObj[0]
                        name['data'] = {'value': int(ints)}
                    else:
                        return {'state':True,'data': "太难理解啦！",'msg':'','type':'system','stop':True}

            return self.device_volume(name)

        #屏幕控制
        elif name["action"] == "DEVICE_SCREEN":
            if 'trigger' in name.keys():
                shuru = name['trigger']
                if shuru in ["屏幕点亮","打开屏幕","打开显示"]:
                    name['data'] = {'value': 1}
                elif shuru in ["关闭屏幕","屏幕关闭","关闭显示"]:
                    name['data'] = {'value': 0}
                else:
                    name['data'] = {'value': 1}

            return self.device_screen(name)

        #旋转屏幕
        elif name["action"] == "DEVICE_RTURN":
            return self.device_rturn(name)

        #获取设备信息
        elif name["action"] == "DEVICE_STATE":
            return self.device_s(name)

        #修改天气预报默认城市
        elif name["action"] == "DEVICE_CITY":
            return self.device_city(name)



if __name__ == '__main__':
    pass
