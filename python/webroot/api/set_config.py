import json
import os
from .ApiBase import ApiBase
from package.mylib import mylib

# 设置所有配置
class set_config(ApiBase):

    def main(self):
        # 获取配置
        if self.query['op'] == 'getconfig':
            config_set = os.path.abspath('./data/conf/config_set.yaml')
            conf_set = mylib.yamlLoad(config_set)
            ret_arr = {
                'code' : 20000,
                'message': '获取配置数据成功',
                'data': {
                    'config': self.config,
                    'setconfig': conf_set
                }
            }
            return json.dumps(ret_arr)

        elif self.query['op'] == 'setconfig':
            data = self.query['data']
            data = json.loads(data)

            conf_set = mylib.getConfig()
            conf_set.update(data)
            mylib.saveConfig(conf_set)
            ret_arr = {
                'code' : 20000,
                'message': '保存配置成功，您需要重启后生效！',
                'data': {
                    'error': '0000'
                }
            }

            return json.dumps(ret_arr)


