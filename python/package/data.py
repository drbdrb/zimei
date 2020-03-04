# -*- coding: UTF-8 -*-
import json

from package.model import model
from package.mylib import mylib

config = mylib.getConfig()


class data():
    """数据库接口"""

    def __init__(self):
        database = r'data/config.db'
        self.db = model(database)

    # 关闭数据库
    def close(self): 
        self.db.close()

    def search_list(self, lists, key):
        for item in lists:
            if item['id'] == key:
                return item
        return False


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
            return {'state':-1,'data':'','msg':'用户信息格式错误'}

        realname = userinfo['realname']
        mmap = {'realname': realname}
        res = self.db.table('user_list').where(mmap).find()
        if res:
            return {'state':1,'data':res[0],'msg': realname +'已经绑到此设备。'}
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
                return {'state':2,'data':user_info,'msg':'绑定新用户信息成功！'}
            else:
                return {'state':0,'data':'','msg':'绑定新用户信息失败！'}

    '''
    更新用户表数据
    uid       --  用户uid
    updata    --  更新数据(字典)
    '''
    def user_up(self,uid, update):
        mmap = {'uid':uid}
        if self.db.table('user_list').where(mmap).find():
            self.db.table('user_list').where(mmap).save(update)
            return {'state':True,'data': "更新用户信息完成",'msg':''}
        else:
            return {'state':False,'data': "更新用户信息失败",'msg':''}

    '''
    删除用户的方法
    uid       --  用户uid
    '''
    def user_del(self,uid):
        mmap = {"uid":uid}
        if self.db.table('user_list').where(mmap).find():
            self.db.table('user_list').where(mmap).delete()
            return {'state':True,'data': "注销完成",'msg':''}
        else:
            return {'state':False,'data': "注销失败",'msg':''}
