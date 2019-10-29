#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys,json,urllib
from package.device import device
from package.data import data
import urllib.parse

def load_json(value):
    value = value.replace('%u','\\u')           #将%uxxxx 替换换 \uxxxx 这才可以进行utf-8解码
    byts = urllib.parse.unquote_to_bytes(value) #返回的 byte
    byts = byts.decode('UTF-8')                 # decode UTF-8 解码只能解开 \uXXXX 的Unicode 标准形式
    return json.loads(byts)

if len(sys.argv) > 1:
    op = sys.argv[1]

    #设备上线
    if op=='online':
        ret = device().online()
        print(ret)

    #是否为新设备
    if op=='isnewdev':
        device().is_newdev()

    #设置：新设备状态
    if op=='setnewdev':
        if len(sys.argv)>2:
            st = str(sys.argv[2])
            device().set_newdev(st)
        else:
            print('必须指定设置状态：0 / 1')

    # 获取城市
    if op=='get_city':
        print(device().city_data())

    #获取配置信息
    if op=='getconfig':
        conf = data().getconfig()
        print(  json.dumps(conf) )

    #获取用户列表
    if op=='getuserlist':
        ulist = data().user_list_get()
        if ulist:
            print(json.dumps(ulist))
        else:
            print('[]');

    #mqtt管理通道
    #if op=='admin':
    #    if len(sys.argv)>2:
    #        st = str(sys.argv[2])
    #        try:
    #            if type(st) is str:
    #                postjson = st.replace('%u', '\\u')
    #                postjson = urllib.parse.unquote(postjson.encode().decode('unicode-escape'))
    #                json_obj = json.loads( postjson )
    #                if type(json_obj) is dict:
    #                     用户注册
    #                    if json_obj['event'] == "USER_REG":
    #                        device().user_bind( json_obj['data'] )

    #                     用户修改
    #                    if json_obj['event'] == "USER_EDIT":
    #                        device().user_edit( json_obj['data'] )

    #                     用户删除
    #                    if json_obj['event'] == "USER_REMOVE":
    #                        device().user_del( json_obj['data'] )

    #                     设备音量
    #                    if json_obj['event'] == "DEVICE_VOLUME":
    #                        device().device_volume( json_obj['data'] )

    #                     设备屏幕控制
    #                    if json_obj['event'] == "DEVICE_SCREEN":
    #                        device().device_screen( json_obj['data'] )

    #                    屏幕旋转
    #                    if json_obj['event'] ==  "DEVICE_RTURN" :

    #                        device().device_rturn(json_obj['data'])

    #                     获取音量 屏幕 和全部
    #                    if json_obj['event'] == "DEVICE_STATE":
    #                        device().u_device(json_obj['data'])



    #        except Exception as bug:
    #            print('api:admin', bug )
    #    else:
    #        print('必须指定参数：0 / 1')

    #初始化创建热点
    '''
    if op=='init_ap':
        init_create_ap.main()

    #设置无线网络
    if op=='set_wifi':
        if len(sys.argv)>2:
            json_str = str(sys.argv[2])
            set_json = load_json(json_str)
            set_wifinet.main(set_json)
    '''
