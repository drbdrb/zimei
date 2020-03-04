import json
import sys,os
from .ApiBase import ApiBase
from bin.Setnet import Wificore

class setwifi(ApiBase):

    def main(self):
        sys.stderr = open(os.devnull, 'w')
        if len(self.query) > 1:
            set_json = self.query

            set_json['wifiname'] = set_json['wifiname']
            set_json['wifipass'] = set_json['wifipass']
            set_json['scanssid'] = set_json['scanssid']

            #初始化网络状态
            Wificore().config_wifi(set_json)

            ret_str = {"code":"0000","msg":"正在验证网络"}
        else:
            ret_str = {"code":"9999","msg":"数据格式错误"}

        return json.dumps(ret_str)
