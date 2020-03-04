import json
import os

from .ApiBase import ApiBase
from package.mylib import mylib

class plugin_admin(ApiBase):
    '''
    插件管理
    '''

    pluginpath = r'./plugin'

    # 获取单个插件信息
    def uninstall_pugin(self, pluginNmae='' ):
        filedir = pluginNmae + '/'
        json_file = os.path.join(self.pluginpath, filedir)
        if os.path.isdir(json_file):
            os.system('sudo rm -rf '+ json_file)
            message = '卸载插件数据成功'
            data = {'error': '0000'}
        else:
            message = '卸载插件失败，【'+pluginNmae+'】插件不存在'
            data = {'error': '1001'}

        ret_arr = {
            'code' : 20000,
            'message':message,
            'data': data
        }

        return json.dumps(ret_arr)

    def main(self):
        # 卸载插件
        if self.query['op']=='uninstall':
            name = self.query['name']
            return self.uninstall_pugin( name )
