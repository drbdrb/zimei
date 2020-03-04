import json
import sys
import os

from .ApiBase import ApiBase
from package.mylib import mylib

class mojing(ApiBase):

    def main(self):
        # 获取配置
        
        if self.query['op'] == 'getconfig':
            return json.dumps(self.config)

        # 获取天气数据
        elif self.query['op'] == 'getweather':
            url = self.config['httpapi'] + '/raspberry/getweather.html'
            city_json = self.config['LOCATION']
            post_data = {'cnid': city_json['city_cnid'], 'city': city_json['city']}
            ret = mylib.http_post(url, post_data)
            return ret['data']

        # 获取老黄历
        elif self.query['op'] == 'laohuangli':
            url = self.config['httpapi'] + '/raspberry/laohuangli.html'
            ret = mylib.http_post(url)
            return ret['data']

        else:
            return '{"error":"lack of parameter"}'
