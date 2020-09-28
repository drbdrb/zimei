import json
import os
import sys

from .ApiBase import ApiBase
from package.mylib import mylib

class develop_user(ApiBase):
    '''开发者账号登录'''

    # 获取本机IP地址
    def get_localhost(self):
        ipAddrs = os.popen("hostname -I").read()
        ipAddrs = ipAddrs.strip()
        ipAddrs = ipAddrs.split(' ')

        server_address = self.handler.server.server_address
        server_host = str(server_address[0])
        server_port = str(server_address[1])

        if server_host == '0.0.0.0':
            server_host = ipAddrs[0]

        return 'http://'+server_host+':'+ str(server_port)

    def main(self):
        op = self.query['op']

        # 登录开发者账号
        if op == 'login':
            username = self.query['username']
            userpass = self.query['userpass']

            post_data = {
                'username': username,
                'userpass': userpass
            }
            message = '登录开发者账号失败，请检查账号和密码是否输入正确'
            data = {'error': '9999'}

            url = self.config['httpapi'] + '/user/raspilogin.html'
            ret = mylib.http_urllib(url, post_data)
            info = json.loads(ret['data'])
            if info['code'] == '0000':
                message = '登录开发者账号成功'
                data = {
                    'error': '0000',
                    'username': info['data']['username'],
                    'webuid': info['data']['webuid']
                }

        # 注册开发者账号
        elif op == 'regist':
            username = self.query['username']
            userpass = self.query['userpass']

            post_data = {
                'username': username,
                'userpass': userpass
            }
            message = '注册开发者账号失败，请检测注册信息是否输入正确'
            data = {'error': '9999'}

            url = self.config['httpapi'] + '/user/raspiregist.html'
            ret = mylib.http_urllib(url, post_data)
            info = json.loads(ret['data'])
            if info['code'] == '0000':
                message = '登录开发者账号注册成功'
                data = {
                    'error': '0000',
                    'username': info['data']['username'],
                    'webuid': info['data']['webuid']
                }
            else:
                message = info['msg']

        ret_arr = {'code' : 20000, 'message': message, 'data': data}
        return json.dumps(ret_arr)

