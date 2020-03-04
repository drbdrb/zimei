import json
import os
from .ApiBase import ApiBase
from package.mylib import mylib

class set_config(ApiBase):

    def main(self):
        # 获取配置
        if self.query['op'] == 'getconfig':
            config_set = os.path.abspath('./config_set.yaml')
            conf_set = mylib.yamlLoad(config_set)
            ret_arr = {
                'code' : 20000,
                'message': '获取数据成功',
                'data': {
                    'config': self.config,
                    'setconfig': conf_set
                }
            }
            return json.dumps(ret_arr)

