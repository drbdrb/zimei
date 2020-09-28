import json
import os
import copy

from .ApiBase import ApiBase
from package.mylib import mylib

class admin(ApiBase):
    '''
    后台管理相关
    '''

    def __init__(self, handler):
        super().__init__(handler)

        self.pluginpath = r'./plugin'
        self.default_admin = []
        admin_path = self.config['ADMIN']['config']
        with open(admin_path) as f:
            self.default_admin = json.load(f)
        del admin_path

    # 加载插件配置插件，所有插件只能有一个插件可以配置后台管理
    def __load_plugin_menu(self):
        admin_mneu = []

        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':
                json_path = os.path.join(self.pluginpath, filedir, 'adminconfig.json')
                if os.path.isfile(json_path):
                    with open(json_path, 'r') as f:
                        admin_mneu = json.load(f)
                        return admin_mneu
        return admin_mneu

    # 加载后台管理菜单
    def __load_admin_menu(self):
        # admin_mneu = self.__load_plugin_menu()
        # if len(admin_mneu)>0:
        #     self.default_admin = admin_mneu

        return json.dumps(self.default_admin)

    def main(self):
        # 获取后台管理菜单
        if self.query['get']=='menu':
            return self.__load_admin_menu()     
