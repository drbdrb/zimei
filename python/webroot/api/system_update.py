import json
import os
import sys
import re
import time

from .ApiBase import ApiBase
from package.mylib import mylib

class system_update(ApiBase):

    def main(self):
        self.SYSTEM_DIR = os.path.abspath(os.path.dirname('../'))
        self.zmprogress = '/tmp/zmprogress'
        if 'op' in self.query:
            op = self.query['op']
            # 检查升级
            if op == 'isupdate':
                os.system('sudo python3 '+ self.SYSTEM_DIR + '/update.py isupdate &')
                ret_arr = {'code': 20000,'message': '提交获取最新版本号操作成功', 'data':{'error':'0000'}}
                return json.dumps(ret_arr)

            # 获取远程版本号
            elif op == 'remotever':
                file_str = ''
                data_ver = ''
                message = '未能获取到'
                data = {'error':'1001','remotever':''}
                if os.path.isfile(self.zmprogress):
                    with open(self.zmprogress, 'r') as f:
                        file_str = f.read()

                    try:
                        file_json = json.loads(file_str)
                        if 'remotever' in file_json:
                            data_ver = file_json['remotever']

                        local_ver = self.config['version']
                        if mylib.versionCompare(local_ver, data_ver)>0:
                            data = {
                                 'error':'0000',
                                 'upgrade': 1,
                                 'remotever':data_ver
                            }
                            message = '系统版本已经更新，可以升级'
                        else:
                            data = {
                                 'error':'0000',
                                 'upgrade': 0,
                                 'remotever':data_ver
                            }
                            message = '当前系统版本已经是最新的了，不需要升级'
                    except:
                        pass

                ret_arr = {'code': 20000,'message': message, 'data':data}
                return json.dumps(ret_arr)

            # 开始升级
            elif op == 'startupdate':
                os.system('sudo python3 '+ self.SYSTEM_DIR + '/update.py startupdate &')
                ret_arr = {'code': 20000,'message': '提交获取最新版本号操作成功', 'data':{'error':'0000'}}
                return json.dumps(ret_arr)

            # 升级状态
            elif op == 'updatestate':
                data_state = ''
                message = '未能获取到'
                data = {'error': '9999'}
                if os.path.isfile(self.zmprogress):
                    with open(self.zmprogress, 'r') as f:
                        file_str = f.read()
                    try:
                        file_json = json.loads(file_str)
                        if 'progress' in file_json:
                            data_state = file_json['progress']
                    except:
                        pass
                    
                if data_state != '':
                    data = {
                        'error': '0000',
                        'progress': data_state
                    }
                    message = '获取升级操作状态成功'

                ret_arr = {'code': 20000, 'message': message, 'data':data}
                return json.dumps(ret_arr)

        

        ret_arr = {'code': 20000,'message': '提交获取最新版本号操作成功', 'data':''}
        return json.dumps(ret_arr)
