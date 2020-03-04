import json
import os
import sys
import crypt

from .ApiBase import ApiBase

class user_login(ApiBase):

    # 定义获取账号和加密密码字典
    def get_pw(self):
        user_pw = {}
        # 读取shadow文件
        f = open('/etc/shadow','r')
        userline = f.readlines()
        f.close()
        for l in userline:
            if len(l.split(":")[1]) > 3:
                user_pw[l.split(":")[0]] = l.split(":")[1]
        return user_pw

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

    def ret_admin(self, username):
        roles = []
        server = self.get_localhost()
        if username == 'root':
            roles = ['root','pi']
            introduction = '超级管理员'
            avatar = server +'/desktop/Public/img/roothead.png'
        else:
            roles = [username]
            introduction = '普通管理员'
            avatar = server +'/desktop/Public/img/pihead.png'

        ret_arr = {
            'code' : 20000,
            'data':{
                'roles' : roles, 
                'introduction' : introduction,
                'avatar' : avatar,
                'name' : introduction,
                'token' : username
            }
        }
        return ret_arr

    def main(self):
        if 'token' in self.query:
            ret_arr = self.ret_admin(self.query['token'])
            return json.dumps(ret_arr)

        if 'op' in self.query and self.query['op'] == 'logout':
            ret_arr = {
                'code' : 20000,
                'message': '退出用户登录成功'
            }
            return json.dumps(ret_arr)
        
        username = self.query['username']
        password = self.query['password']

        user_passwd = self.get_pw()
        user_pass = user_passwd[username]
        # 获得用户盐值
        user_salt = "$6$" + user_pass.split("$")[2]

        if user_pass == crypt.crypt(password.rstrip(),user_salt):
            ret_arr = self.ret_admin(username)
        else:
            ret_arr = {
                'code' : 50000,
                'message': '账号或密码错误，登录账号为系统账号密码root、pi'
            }

        return json.dumps(ret_arr)

