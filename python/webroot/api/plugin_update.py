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
    def get_new_ver(self, config):
        upurl = config['repository']['url']
        if 'gitee.com' in upurl:
            new_upurl = upurl[:-4]
            new_upurl += '/raw/master/config.json'
        elif 'github.com' in upurl:
            new_upurl = upurl[:-4]
            new_upurl = new_upurl.replace('github.com', 'raw.githubusercontent.com' , 1)
            new_upurl += '/master/config.json'

        version = '0.0.1'
        ret = mylib.http_post(new_upurl, timeout=60)
        if ret['data'] != '':
            ret_json = json.loads(ret['data'])
            version  = ret_json['version']
        return version

    # 移动插件文件
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
    def startUpdate(self, config):
        plugin_name = config['name']
        plugin_ver  = config['version']
        update_url  = config['repository']['url']

        self.plugin_down = os.path.join(self.TEMPDOWN_DIR, plugin_name)
        self.plugin_path = os.path.join(self.PLUGIN_DIR,plugin_name)

        new_ver = self.get_new_ver(config)

        if mylib.versionCompare(plugin_ver,new_ver) > 0:
            # 下载最新文件
            self.down_newfile(plugin_name, update_url)
            time.sleep(1)
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
    def __load_pugin_info(self, pluginNmae='' ):
        filedir = pluginNmae + '/'
        json_file = os.path.join(self.pluginpath, filedir, 'config.json')
        config_json = {}
        with open(json_file, 'r') as f:
            config_json = json.load(f)

        return config_json

    # 检测远程插件版本
    def checkver_pugin(self, pluginName):
        config_json = self.__load_pugin_info( pluginName )
        local_ver = config_json['version']      # 本地版本号

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
            message = '获取远程最新版本号失败'
            data = {
                'error': '9999',
                'newversion': ''
            }

            # 获取远程最新版本号
            origin_ver = PlugUpdate().get_new_ver(config_json)
            if origin_ver != '':
                if mylib.versionCompare(local_ver,origin_ver) > 0:
                    message = '远程版本已更新，可以升级'
                    data = {
                        'error': '0000',
                        'upgrade': 1,
                        'newversion': origin_ver
                    }
                else:
                    message = '当前版本已经是最新版本，无需升级'
                    data = {
                        'error': '0000',
                        'upgrade': 0,
                        'newversion': origin_ver
                    }            

        ret_arr = {'code': 20000,'message': message, 'data':data}
        return json.dumps(ret_arr)

    # 升级插件
    def update_pugin(self, pluginName):
        config_json = self.__load_pugin_info( pluginName )

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
            return PlugUp.startUpdate(config_json)
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

    # 卸载插件
    def uninstall_pugin(self, pluginName):
        filedir = pluginName + '/'
        json_file = os.path.join(self.pluginpath, filedir)
        if os.path.isdir(json_file):
            os.system('sudo rm -rf '+ json_file)
            message = '卸载插件数据成功'
            data = {'error': '0000'}
        else:
            message = '卸载插件失败，【'+pluginName+'】插件不存在'
            data = {'error': '1001'}

        ret_arr = {
            'code' : 20000,
            'message':message,
            'data': data
        }

        return json.dumps(ret_arr)

    # 发布插件
    def release_pugin(self, pluginName, author, webuid):
        config_json = self.__load_pugin_info( pluginName )

        config_json['author'] = author
        config_json['webuid'] = webuid

        post_data = {
            'data': json.dumps(config_json)
        }
        url = self.config['httpapi'] + '/raspberry/pluginrelease.html'
        ret = mylib.http_post(url,post_data)

        message = '发布插件失败，请检查网络连接状态是否正常'
        data = {'error':999}
        if str(ret['code']) == '0000':
            plugininfo = json.loads(ret['data'])
            if plugininfo['code'] == '0000':
                message = plugininfo['msg']
                data = {'error':0}
            else:
                message = plugininfo['msg']
                data = {'error':plugininfo['code']}

        ret_arr = {
            'code' : 20000,
            'message': message,
            'data': data
        }
        return json.dumps(ret_arr)

    def main(self):
        op   = self.query['op']
        name = self.query['name']

        # 检测版本
        if op=='checkver':
            return self.checkver_pugin( name )

        # 升级插件
        if op=='update':
            return self.update_pugin( name )
        
        # 安装插件
        if op=='install':
            return self.install_pugin( name )

        # 卸载插件
        if op=='uninstall':
            return self.uninstall_pugin( name )

        # 发布插件
        if op=='release':
            author = self.query['author']
            webuid = self.query['webuid']
            return self.release_pugin(name, author, webuid)
