import json
import os
import re
import psutil
import math
import requests
from .ApiBase import ApiBase

class admin_index(ApiBase):

    def __init__(self, handler):
        super().__init__(handler)

    def wifi_name_list(self):
        try:
            data = os.popen("sudo iwlist wlan0 scan | grep ESSID").read()
            strs=r""
            result=[]
            for x in data:
                strs+=x
                #分类
                if x=="\n":
                    #去掉不识别的
                    if x.count("\\x00")>3:
                        continue
                    #去换行,多余字符,空格
                    result.append(strs[:-1].replace("ESSID:",'',1).strip().strip('","'))
                    strs=""
            return result
        except:
            return []

    def wifi_strength(self):
        try:
            data = int(os.popen("iw wlan0 link | grep signal").read().strip().replace("signal: -",'',1).strip().strip('dBm'))

            #wifi 5格子
            if data >=0:#满格
                key=5
            if data >56:#缺1格
                key=4
            if data >60:#缺2格
                key=3
            if data >65:#缺3格
                key=2
            if data >69:#缺4格
                key=1
            return key
        except:
            return 0 #0格子没有开启wifi
            
    def getRotate(self):
        ''' 屏幕旋转状态 '''
        config = '/boot/config.txt'
        f = open(config, "r")
        fstr = f.read()
        f.close()
        restr = r'^display_rotate\s*=\s*(\d)'
        rotate_val = 0
        rema = re.search(restr, fstr, re.M | re.I)
        if rema:
            rotate_val = rema.group(1)
        return rotate_val

    def getVolume(self):
        ''' 取得音量大小 '''
        info = os.popen("sudo amixer sget Speaker").read()
        patten = r'Front\sLeft:\sPlayback\s(\d+)\s\[(\d+)\%\]'
        varStr = re.search(patten, info, re.M | re.I)
        if varStr:
            realvol = int(varStr.group(2))
        else:
            realvol = 80
        vol = int(1.7972 * math.pow(2.718, 0.04 * realvol))
        return vol

    # 返回CPU温度信息
    def getCPUtemperature(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))
    
    # 返回内存使用情况 (单位=kb) 列表
    # Index 0: total RAM
    # Index 1: used RAM
    # Index 2: free RAM
    def getRAMinfo(self):
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return(line.split()[1:4])
    
    # 返回CPU使用百分比%
    def getCPUuse(self):
        #return(str(os.popen(r"top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))
        return str(psutil.cpu_percent(interval=1,percpu=False))

    # 返回磁盘使用情况表
    # Index 0: total disk space
    # Index 1: used disk space
    # Index 2: remaining disk space
    # Index 3: percentage of disk used
    def getDiskSpace(self):
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                return(line.split()[1:5])

    # 转换磁盘大小
    def diskToNum(self, disknum):
        intnum = float(re.sub(r'G|T|K|B', '', disknum))
        renum = 0
        if re.search(r'G', disknum, re.M|re.I):
            renum = intnum * 1024 * 1024
        elif re.search(r'K', disknum, re.M|re.I):
            renum = intnum * 1024
        return renum


    # 返回所有信息
    def get_allinfo(self):
        cpu_temp  = self.getCPUtemperature()    # CPU温度
        cpu_usage = self.getCPUuse()            # CPU使用率
        if len(cpu_usage)<=0:
            cpu_usage = 1

        # 内存使用率
        ram_stats = self.getRAMinfo()
        ram_total = round(int(ram_stats[0]) / 1000,1)
        ram_used  = round(int(ram_stats[1]) / 1000,1)
        ram_ues   = int((ram_used / ram_total) * 100)

        # 磁盘使用率
        disk_stats = self.getDiskSpace()
        disk_total = disk_stats[0]
        disk_used  = disk_stats[1]

        disk_total = self.diskToNum(disk_total)
        disk_used  = self.diskToNum(disk_used)
        # disk_perc = disk_stats[3]
        disk_ues = int((disk_used / disk_total) * 100)
        # disk_ues = str(int(disk_total))

        new_json = {
            'cpuTemp': cpu_temp,
            'cpuUse': cpu_usage,
            'ramUse': ram_ues,
            'diskUes': disk_ues,
            
        }
        ret_arr = {
            'code' : 20000,
            'message': '获取全部插件数据成功',
            'data': new_json
        }
        return json.dumps(ret_arr)

    def network_detection(self):
        try:
            response  = requests.post(self.config['httpapi'] + r'/raspberry/ping.html',timeout=10)
            if response.status_code==200:
                return 1
            else:
                return 0
        except:
            return 0

    def main(self):
        # 获取所有设备状态信息
        if self.query['op']=='getallinfo':
            return self.get_allinfo()

        if self.query['op'] == 'getRotate':
            ret_arr = {
            'code' : 20000,
            'message': '获取屏幕方向信息成功',
            'data': self.getRotate()
        }
            return json.dumps(ret_arr)
            
        if self.query['op'] == 'getVolume':
            ret_arr = {
            'code' : 20000,
            'message': '获取音量信息成功',
            'data': self.getVolume()
        }
            return json.dumps(ret_arr)

        if self.query['op'] == 'getwifiname':
   
            ret_arr = {
            'code' : 20000,
            'message': '获取wifi信息成功',
            'data':  os.popen("iw wlan0 link | grep SSID").read().strip()
        }
            return json.dumps(ret_arr)


        if self.query['op']=='wifi_name_list':
    

            ret_arr = {
                'code' : 20000,
                'message': '获取wifi列表数据成功',
                'data': self.wifi_name_list()
            }
            return json.dumps(ret_arr)


        if self.query['op']=='wifi_strength':
            ret_arr = {
                'code' : 20000,
                'message': '获取wifi强度数据成功',
                'data': self.wifi_strength()
            }
            return json.dumps(ret_arr)

        if self.query['op']=='network_detection':
            ret_arr = {
                'code' : 20000,
                'message': '获取网络状态成功',
                'data': self.network_detection()
            }
            return json.dumps(ret_arr)


            


'''
if __name__ == '__main__':
    adm = admin_index()
        # CPU informatiom
    CPU_temp = adm.getCPUtemperature()
    CPU_usage = adm.getCPUuse()
    
    # RAM information
    # Output is in kb, here I convert it in Mb for readability
    RAM_stats = adm.getRAMinfo()
    RAM_total = round(int(RAM_stats[0]) / 1000,1)
    RAM_used = round(int(RAM_stats[1]) / 1000,1)
    RAM_free = round(int(RAM_stats[2]) / 1000,1)
    
    # Disk information
    disk_stats = adm.getDiskSpace()
    DISK_total = disk_stats[0]
    DISK_used = disk_stats[1]
    DISK_perc = disk_stats[3]

    print('')
    print('CPU Temperature = '+CPU_temp)
    print('CPU Use = '+CPU_usage)
    print('')
    print('RAM Total = '+str(RAM_total)+' MB')
    print('RAM Used = '+str(RAM_used)+' MB')
    print('RAM Free = '+str(RAM_free)+' MB')
    print('') 
    print('DISK Total Space = '+str(DISK_total)+'B')
    print('DISK Used Space = '+str(DISK_used)+'B')
    print('DISK Used Percentage = '+str(DISK_perc))

'''