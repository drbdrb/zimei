import json
import os
import re
import time

from .ApiBase import ApiBase
from package.mylib import mylib

class PlugUpdate():
    '''插件更新程序'''

    def __init__(self):
        # 临时下载目录
        self.TEMPDOWN_DIR = r'/tmp/zmplugin'

        # 插件目录
        self.PLUGIN_DIR = os.path.abspath(r'./plugin')

    # 运行git命令
    def run_gitcmd(self, getcwd, cmd, osrun='popen' ):
        """
        运行git命令:
        getcwd -- 工作目录
        cmd    -- 运行指令
        osrun  -- 运行模式 system / popen(默认)
        """
        cmd = 'cd '+ getcwd +' && '+ cmd
        if osrun == 'system':
            cmd += ' > /dev/null 2>&1'
            os.system( cmd )
        else:
            out = os.popen(cmd).read()
            return out

    # 获取远程版本号
    def get_new_ver(self,pluginName):
        json_file = os.path.join(self.plugin_down, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)
        return config_json['version']

    # 移动插件名称
    def move_plugin(self, optype='升级插件'):
        mv_cmd = 'sudo rsync -aq --exclude=.git --delete '+ self.plugin_down +'/ '+ self.plugin_path+'/'
        os.system( mv_cmd )
        os.system('sudo chown -R pi.pi '+ self.plugin_path)
        os.system('sudo chmod -R 755 '+ self.plugin_path)

        json_file = os.path.join(self.plugin_path, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)
        message = optype +'成功'
        data = {
            'error': '0000',
            'version': config_json['version']
        }
        ret_arr = {'code': 20000, 'message': message, 'data':data}
        return json.dumps(ret_arr)

    # 下载新的文件
    def down_newfile(self, pluginName, giturl):
        git_cmd = ''
        if os.path.exists( os.path.join(self.plugin_down, '.git') ):
            git_cmd = 'sudo git pull'        #拉取
            self.run_gitcmd(self.plugin_down, git_cmd, 'system')
        else:
            git_cmd = 'sudo git clone --recursive '+ giturl +' '+ self.plugin_down
            cmd = git_cmd +' > /dev/null 2>&1'
            os.system( cmd )

    # 开始升级
    def update(self, config):
        plugin_name = config['name']
        plugin_ver  = config['version']
        update_url = config['repository']['url']

        self.plugin_down = os.path.join(self.TEMPDOWN_DIR, plugin_name)
        self.plugin_path = os.path.join(self.PLUGIN_DIR,plugin_name)

        # 下载最新文件
        self.down_newfile(plugin_name, update_url)
        time.sleep(1)
        new_ver = self.get_new_ver(plugin_name)

        if mylib.versionCompare(plugin_ver,new_ver) > 0:
            return self.move_plugin('升级插件')
        else:
            ret_arr = {
                'code': 20000, 
                'message': '当前插件已经是最新版了', 
                'data':{
                    'error': '0000',
                    'version': plugin_ver
                }
            }
            return json.dumps(ret_arr)

    # 开始安装
    def install(self, config):
        plugin_name = config['name']
        update_url = config['repository_url']

        self.plugin_down = os.path.join(self.TEMPDOWN_DIR, plugin_name)
        self.plugin_path = os.path.join(self.PLUGIN_DIR,plugin_name)

        # 下载最新文件
        self.down_newfile(plugin_name, update_url)
        time.sleep(1)
        return self.move_plugin('安装插件')

class plugin_update(ApiBase):

    pluginpath = r'./plugin'

    # 获取单个插件信息
    def load_pugin_info(self, pluginNmae='' ):
        filedir = pluginNmae + '/'
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)

        return config_json

    # 升级插件
    def update_pugin(self, pluginNmae):
        config_json = self.load_pugin_info( pluginNmae )

        is_update = False
        message = '当前插件不支持在线更新'
        data = {
            'error': '9999',
            'version': config_json['version']
        }

        if 'repository' in config_json:
            if 'type' in config_json['repository'] and 'url' in config_json['repository']:
                if config_json['repository']['type']=='git' and config_json['repository']['url']!='':
                    is_update = True

        if is_update:
            PlugUp = PlugUpdate()
            return PlugUp.update(config_json)
        else:
            ret_arr = {'code': 20000,'message': message, 'data':data}
            return json.dumps(ret_arr)

    # 安装新插件
    def install_pugin(self, pluginName):
        # 获取远程插件列表
        url = self.config['httpapi'] + '/raspberry/plugininfo.html'
        ret = mylib.http_post(url,{'name':pluginName})
        plugininfo = json.loads(ret['data'])

        is_install = False
        message = '当前插件暂不支持在线安装'
        data = {
            'error': '9999',
            'version': plugininfo['version']
        }
        if plugininfo['repository_type']=='git' and plugininfo['repository_url']!='':
            is_install = True

        if is_install is True:
            PlugUp = PlugUpdate()
            return PlugUp.install(plugininfo)
        else:
            ret_arr = {'code' : 20000,'message': message,'data':data}
            return json.dumps(ret_arr)

    def main(self):
        op   = self.query['op']
        name = self.query['name']

        if op=='update':
            return self.update_pugin( name )
        
        if op=='install':
            return self.install_pugin( name )
