#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys,json,urllib
from package.device import device
from package.data import data
from package.config import config
import urllib.parse

def load_json(value):
    value = value.replace('%u','\\u')           #将%uxxxx 替换换 \uxxxx 这才可以进行utf-8解码
    byts = urllib.parse.unquote_to_bytes(value) #返回的 byte
    byts = byts.decode('UTF-8')                 # decode UTF-8 解码只能解开 \uXXXX 的Unicode 标准形式
    return json.loads(byts)

if len(sys.argv) > 1:
    op = sys.argv[1]

    # 获取城市
    if op=='get_city':
        print(device().city_data())

    #获取配置信息
    if op=='getconfig':
        conf = config
        print( json.dumps(conf) )

    #获取用户列表
    if op=='getuserlist':
        ulist = data().user_list_get()
        if ulist:
            print(json.dumps(ulist))
        else:
            print('[]')