#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from package.config import config
from package.include.mylib import mylib
from package.include.model import model
import json                         #库模块类型转换

class data():
    """数据库接口"""

    def __init__(self):
        self.db = model(config['database'])


    #关闭数据库
    def close(self):
        self.db.close()

    #获取配置
    def getconfig(self):
        conf = {}
        res = self.db.table('config').sel()
        if res:
            for v in res:
                conf[v['key']] = v['value']
        return conf

    #修改数据库
    def setconfig(self, tab):                                   #将tab写入数据库
        if type(tab) == type([1]):
            for x in tab:
                self.db.table('config').add(x)

    #更新状态
    def up_config(self, st):
        where={'key':st['key']}                                 #得到st字典里st的'new_dev'值。where={key:'new_dev"}
        newcx = self.db.table('config').where(where).find()     #在数据库config里检测有没有找到{key:'new_dev"}
        if (newcx):                                             #如果是False或者None时则else
            self.db.table('config').where(where).save({'value':st['value']})   #
        else:
            self.db.table('config').add(st)


    #保存必要参数
    def save_necessary_data(self, jsonstr):
        try:
            create_tb_cmd='CREATE TABLE IF NOT EXISTS config(key TEXT,value TEXT,nona TEXT);'       #表头创建值
            self.db.connection.execute(create_tb_cmd)        #主要就是上面的语句
        except:
            print('表存在')

        ret_dict = {}

        where = {'key':'clientid'}
        cx = self.db.table('config').where(where).find()
        if(cx):
            self.db.table('config').where(where).setField('value',jsonstr['clientid'])
        else:
            self.db.table('config').add({'key':'clientid','value':jsonstr['clientid'],'nona':'设备ID'})

        where = {'key':'mqtt_name'}
        cx = self.db.table('config').where(where).find()
        if(cx):
            self.db.table('config').where(where).setField('value',jsonstr['clientid'])
        else:
            self.db.table('config').add({'key':'mqtt_name','value':jsonstr['clientid'],'nona':'MQTT用户名'})

        where = {'key':'mqtt_pass'}
        cx = self.db.table('config').where(where).find()
        if(cx):
            self.db.table('config').where(where).setField('value',jsonstr['skey'])
        else:
            self.db.table('config').add({'key':'mqtt_pass','value':jsonstr['skey'],'nona':'MQTT密钥'})

        where = {'key':'mqtt_devid'}
        cx = self.db.table('config').where(where).find()
        if(cx):
            self.db.table('config').where(where).setField('value',jsonstr['devid'])
        else:
            self.db.table('config').add({'key':'mqtt_devid','value':jsonstr['devid'],'nona':'MQTT密钥ID'})

        ret_dict = {
            'clientid'   : jsonstr['clientid'],
            'mqttname'  : jsonstr['clientid'],
            'mqttpass'  : jsonstr['skey']
        }
        return ret_dict


    ##是否为新设备
    def	get_newdev(self,deviceid):
        where = {'key':'clientid'}
        cx = self.db.table('config').where(where).find()                            #检测{'key':'clientid'}
        is_new = '0'
        if (cx):
            cx = cx[0]
            if (str(deviceid)==str(cx['value'])):       #mac地址和数据库mac地址对比
                newcx = self.db.table('config').where({'key':'new_dev'}).find()    #读取数据库的key的new_dev值=newcx变量
                if (newcx):
                    is_new = str(newcx[0]['value'])      #0或1
                else:
                    is_new = '1'
                    self.db.table('config').add({'key':'new_dev','value':'1','nona':'是否为新设备'})
            else:
                is_new = '1'
                self.db.table('config').add({'key':'new_dev','value':'1','nona':'是否为新设备'})
        else:
            is_new = '1'
            self.db.table('config').add({'key':'clientid','value':deviceid,'nona':'设备ID'})
            self.db.table('config').add({'key':'new_dev','value':'1','nona':'是否为新设备'})
        self.db.close()

        ret = {'code':'9999','msg':'未知错误','data':''}
        if (is_new=='1'):
            ret['code'] = '0000'
            ret['data'] = 1
            ret['msg']  = '新设备'
        else:
            ret['code'] = '0000'
            ret['data'] = 0
            ret['msg']  = '非新设备'
        return json.dumps(ret)

    '''
    * =========================================================
    * 用户表相关操作
    * =========================================================
    '''

    #获取用户列表数据
    def user_list_get(self, field = True ):
        res = self.db.table('user_list').field(field).sel()
        return res

    #获取单个用户信息
    def user_info(self, uid):
        info = {}
        if uid <=0: return info
        res = self.db.table('user_list').where({'uid':uid}).find()
        if res:
            info = res[0]
        return info

    #用户注册
    def user_reg(self, userinfo ):
        if not type(userinfo) is dict:
            return {'state':-1,'data':'','msg':'用户信息格式错误','stop':True}

        realname = userinfo['realname']
        mmap = {'realname': realname}
        res = self.db.table('user_list').where(mmap).find()
        if res:
            return {'state':1,'data':res[0],'msg': realname +'已经绑到此设备。','stop':True}
        else:
            add_data = {
                'realname': userinfo['realname'],
                'gender'  : userinfo['gender'],
                'birthday': userinfo['birthday'],
                'nickname': userinfo['nickname']
            }
            res = self.db.table('user_list').add(add_data)
            if res:
                user_info = {}
                uinfo = self.db.table('user_list').where(mmap).find()
                if uinfo: user_info = uinfo[0]
                return {'state':2,'data':user_info,'msg':'绑定新用户信息成功！','stop':True}
            else:
                return {'state':0,'data':'','msg':'绑定新用户信息失败！','stop':True}

    '''
    更新用户表数据
    uid       --  用户uid
    updata    --  更新数据(字典)
    '''
    def user_up(self,uid, update):
        mmap = {'uid':uid}
        if self.db.table('user_list').where(mmap).find():
            self.db.table('user_list').where(mmap).save(update)
            return {'state':True,'data': "更新用户信息完成",'msg':'','type':'system','stop':True}
        else:
            return {'state':False,'data': "更新用户信息失败",'msg':'','type':'system','stop':True}

    '''
    删除用户的方法
    uid       --  用户uid
    '''
    def user_del(self,uid):
        mmap = {"uid":uid}
        if self.db.table('user_list').where(mmap).find():
            self.db.table('user_list').where(mmap).delete()
            return {'state':True,'data': "注销完成",'msg':'','type':'system','stop':True}
        else:
            return {'state':False,'data': "注销失败",'msg':'','type':'system','stop':True}



