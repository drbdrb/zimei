import json
import os

from .ApiBase import ApiBase
from package.mylib import mylib

class plugin_list(ApiBase):

    pluginpath = r'./plugin'

    # 加载本地插件列表
    def __load_local_pugin(self):
        pluginpath = r'./plugin'

        plugin_list = []
        for filedir in os.listdir(pluginpath):
            if os.path.isdir(os.path.join(pluginpath, filedir)):
                json_file = os.path.join(pluginpath, filedir, 'config.json')
                with open(json_file, 'r') as f:
                    config_json = json.load(f)
                    icon = '0'
                    IsEnable = True
                    version = '0.0.1'
                    if 'icon' in config_json:
                        icon = config_json['icon']
                    if 'IsEnable' in config_json:
                        IsEnable = config_json['IsEnable']
                    if 'version' in config_json:
                        version = config_json['version']
                    item_dict = {
                        'name': config_json['name'],
                        'displayName': config_json['displayName'],
                        'description': config_json['description'],
                        'icon': icon,
                        'version': version,
                        'IsEnable': IsEnable
                    }
                    plugin_list.append(item_dict)
        return plugin_list

    # 加载远程插件列表
    def __load_origin_plugin(self):
        url = self.config['httpapi'] + '/raspberry/pluginlist.html'
        ret = mylib.http_post(url)
        origin_plugin = json.loads(ret['data'])
        return origin_plugin


    # 加载插件列表
    def load_pugin_list(self):
        plugin_list = self.__load_local_pugin()
        ret_arr = {
            'code' : 20000,
            'message':'获取数据成功',
            'data':plugin_list
        }
        return json.dumps(ret_arr)

    # 获取单个插件信息
    def load_pugin_info(self, pluginNmae='' ):
        filedir = pluginNmae + '/'
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)

        ret_arr = {
            'code' : 20000,
            'message':'获取[%s]插件数据成功' % pluginNmae,
            'data':config_json
        }

        return json.dumps(ret_arr)

    # 获取远程插件列表
    def load_allpugin(self):
        # 远程插件列表
        origin_plugin = self.__load_origin_plugin()

        # 本地已装插件
        local_plugin = self.__load_local_pugin()

        new_json = []
        for origin_item in origin_plugin:
            origin_item['state'] = '一键安装'
            for local_item in local_plugin:
                if origin_item['name']==local_item['name']:
                    origin_item['state'] = '已安装'
                    if mylib.versionCompare(local_item['version'], origin_item['version']) > 0:
                        origin_item['state'] = '一键升级'
            new_json.append( origin_item )

        ret_arr = {
            'code' : 20000,
            'message':'获取全部插件数据成功',
            'data':new_json
        }
        return json.dumps(ret_arr)


    def main(self):
        # 本地安装的插件列表
        if self.query['op']=='getlist':
            return self.load_pugin_list()

        # 官方全部插件列表
        if self.query['op']=='getalllist':
            return self.load_allpugin()
        
        # 单个插件信息
        if self.query['op']=='getinfo':
            name = self.query['name']
            return self.load_pugin_info( name )
