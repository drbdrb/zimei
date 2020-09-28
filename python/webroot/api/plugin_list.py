import json
import os
import copy

from .ApiBase import ApiBase
from package.mylib import mylib

class plugin_list(ApiBase):

    def __init__(self, handler):
        super().__init__(handler)

        self.pluginpath = r'./plugin'

        self.plugintemp = {}
        template_path = r'./data/conf/pluginconfig.json'
        with open(template_path) as f:
            self.plugintemp = json.load(f)


    # 加载本地插件列表
    def __load_local_pugin(self):
        pluginlist = []

        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':
                template_json = copy.deepcopy(self.plugintemp)          # 拷贝一个对象

                json_file = os.path.join(self.pluginpath, filedir, 'config.json')
                if not os.path.isfile(json_file):
                    continue
                with open(json_file, 'r') as f:
                    config_json = json.load(f)
                    template_json.update(config_json)
                    pluginlist.append(template_json)

        return pluginlist

    # 加载远程插件列表
    def __load_origin_plugin(self):
        url = self.config['httpapi'] + '/raspberry/pluginlist.html'
        ret = mylib.http_post(url)
        origin_plugin = json.loads(ret['data'])
        return origin_plugin

    # 获取远程单个插件信息
    def __load_origin_plugin_info(self, pluginName):
        url = self.config['httpapi'] + '/raspberry/plugininfo.html'
        ret = mylib.http_post(url,{'name':pluginName})
        plugininfo = json.loads(ret['data'])
        return plugininfo

    # 加载插件列表
    def load_plugin_list(self):
        plugin_list = self.__load_local_pugin()
        ret_arr = {
            'code' : 20000,
            'message':'获取数据成功',
            'data':plugin_list
        }
        return json.dumps(ret_arr)

    # 获取本地单个插件信息
    def load_plugin_info(self, pluginNmae='' ):
        filedir = pluginNmae + '/'
        config_json = copy.deepcopy(self.plugintemp)
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        file_json = {}
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                file_json = json.load(f)

        config_json.update(file_json)

        origin_info = self.__load_origin_plugin_info(pluginNmae)
        if len(origin_info)<=0:
            config_json['isRelease'] = 0
        else:
            config_json['isRelease'] = 1

        ret_arr = {
            'code' : 20000,
            'message':'获取[%s]插件数据成功' % pluginNmae,
            'data':config_json
        }

        return json.dumps(ret_arr)

    # 更新插件配置信息
    def set_plugin_config(self, pluginNmae, updata):
        filedir = pluginNmae + '/'
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)
        
        config_json.update( updata )

        fw = open(json_file,'w',encoding='utf-8')
        json.dump(config_json, fw, ensure_ascii=False, indent=4)
        fw.close()

        ret_arr = {
            'code' : 20000,
            'message': '更新插件配置成功',
            'data': {'error': '0000'}
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
            return self.load_plugin_list()

        # 官方全部插件列表
        if self.query['op']=='getalllist':
            return self.load_allpugin()
        
        # 单个插件信息
        if self.query['op']=='getinfo':
            name = self.query['name']
            return self.load_plugin_info( name )

        # 更新插件配置信息
        if self.query['op']=='setconfig':
            data = self.query['data']
            data_json = json.loads(data)
            ret_arr = {
                'code' : 20000,
                'message':'未知错误',
                'data':{'error': '9999'}
            }
            if 'name' in data_json:
                pluginName = data_json['name']
                if pluginName != '':
                    del data_json['name']
                    return self.set_plugin_config(pluginName, data_json)
            return json.dumps(ret_arr)

            
