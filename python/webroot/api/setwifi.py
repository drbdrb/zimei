import json
import sys,os,re
import math
from .ApiBase import ApiBase
from bin.Setnet import Wificore

class setwifi(ApiBase):

    # 设置WiFi配网信息
    def set_wifi_info(self, data):
        set_json = {}
        if len(data) > 1:
            set_json['wifiname'] = data['wifiname']
            set_json['wifipass'] = data['wifipass']
            set_json['scanssid'] = data['scanssid']

            #初始化网络状态
            Wificore().config_wifi(set_json)

            ret_str = {"code":"0000","msg":"正在验证网络"}
        else:
            ret_str = {"code":"9999","msg":"数据格式错误"}

        return json.dumps(ret_str)

    # 获取设备ID信息
    def get_equipm_id(self):
        ret_str = {"code":"0000", "data": self.config['MQTT']['clientid'], "msg":"获取设备ID信息成功"}
        return json.dumps(ret_str)

    def get_wifi_list(self):
        def takeSecond(elem):
            return int(elem['wifi_qual'])

        iwlist = 'sudo iwlist wlan0 scan | grep -E "ESSID|Quality|IEEE"'
        cmd_str = os.popen(iwlist).read()
        cmd_str = cmd_str.strip()
        cmd_str = re.sub(r'\\x00','',cmd_str)

        res = cmd_str.split("Quality")

        re_name = r'ESSID:"(.+)"'
        re_pass = r'IE:\s+IEEE\s+(.+)\s+Version'
        re_qual = r'\=(\d+)\/(\d+)'

        wifi_list = []
        for x in res:
            item_obj = {}
            o_n = re.search( re_name, x, re.M|re.I)
            if o_n:
                wifi_name = o_n.group(1)
                rem = re.search(r'\\x', wifi_name, re.M|re.I)
                try:
                    if rem != None:
                        wifi_name = wifi_name.encode('raw_unicode_escape').decode()

                    if wifi_name:
                        cn_byte   = wifi_name.replace('%', r'\x')
                        cn_byte   = eval("b"+"\'"+cn_byte+"\'")
                        wifi_name = wifi_name.replace(wifi_name, cn_byte.decode())
                        item_obj['wifi_name'] = wifi_name
                    else:
                        continue
                except:
                    continue
            else:
                continue

            o_p = re.search( re_pass, x, re.M|re.I)
            if o_p:
                #print('pass:', o_p.group(1))
                item_obj['wifi_pass'] = o_p.group(1)

            o_l = re.search( re_qual, x, re.M|re.I)
            if o_l:
                #print('pass:', o_l.group(1))
                item_obj['wifi_qual'] = math.floor( (int(o_l.group(1)) / int(o_l.group(2)))*100 )
            if len(item_obj)>0:
                wifi_list.append( item_obj )

        wifi_list.sort(key=takeSecond,reverse=True)

        return json.dumps(wifi_list)

    def main(self):
        sys.stderr = open(os.devnull, 'w')
        ret_str = {"code":"9999","msg":"数据格式错误"}
        if 'op' in dict(self.query).keys():
            op = self.query['op']
            if op == 'setinfo':
                return self.set_wifi_info(self.query)

            if op == 'getinfo':
                return self.get_equipm_id()

            if op == 'getlist':
                return self.get_wifi_list()

        return json.dumps(ret_str)
