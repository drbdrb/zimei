# -*- coding: utf-8 -*-
import os

config = {
    'version': '0.001',     #固件版本
    'root_path': os.path.dirname(os.path.dirname(__file__)),        #系统根目录
    'httpapi': 'https://hapi.16302.com',
    'database':'',

    # MQTT 配置定义，这里只是作初始化，具体定义在 package/data.py 里将重置
    'MQTT':{
        'server': 'mqtt.16302.com',
        'port': 1883,
        'clientid':'客户端ID',
        'mqttname':'账号',
        'mqttpass':'密码'
    },

    #硬件管脚定义
    'GPIO':{
        'pingmo_kg': 37,        #开关屏幕控制脚
        'pingmo_zt': {
            'pin': 33,          #获取屏幕状态脚
            'open': 1           #屏幕开的状态，电平值：1 高电平 0 低电平
        },        
        'fengshan_kg': 13,      #降温风扇开关控制脚，0 -- 为关闭此功能
        'deng_kg': 11,          #装饰灯控制脚
        'setnet_pin': 31,       #配网控制按钮脚
    },

    #语音唤醒
    'WAKEUP' :{
        'model': 'data/snowboy/xiaoduxiaodu.umdl',
        'sensit' : [0.5,0.50,0.5],
        #个人模型格式如下,记得#掉上面2行
        #'model': 'data/snowboy/dai_mojing.pmdl',
        #'sensit' : [0.5]
    },

    #百度API接口
    'BAIDUAPI':{
        'CUID': "123456PYTHON",                                                     # 语音识别，语音合成
        'url':{
            "shibie_token_url": "https://openapi.baidu.com/oauth/2.0/token",        # 百度语音识别获取token的网址
            "shibie_api_url"  : "http://vop.baidu.com/server_api",                  # 百度语音识别的网址
            "hecheng_api_url" : "http://tsn.baidu.com/text2audio",                  # 百度语音合成的网址
            "duibi_token_url" : "https://aip.baidubce.com/oauth/2.0/token?",        # 人脸对比token地址
            "duibi_api_url"   : "https://aip.baidubce.com/rest/2.0/face/v3/match",  # 百度人脸对比请求网址
        },

        'yuyin_conf':{
            "token_url"       : "https://openapi.baidu.com/oauth/2.0/token",      # 百度语音识别获取token的网址
            "shibie_api_url"  : "http://vop.baidu.com/server_api",                # 百度语音识别的网址
            "hecheng_api_url" : "http://tsn.baidu.com/text2audio",                # 百度语音合成的网址
            "body":{
                "grant_type"      : "client_credentials",
                "client_id"       : "8IUGBKypHccENIUzCeggIZt1",
                "client_secret"   : "kj0fIVYFe4BSjSkA0TBzyPWhcnqkwnu1"
            }
        },

        'renlian_conf':{
            "token_url"     : "https://aip.baidubce.com/oauth/2.0/token?",        # 人脸对比token地址
            "api_url"       : "https://aip.baidubce.com/rest/2.0/face/v3/match",  # 百度人脸对比请求网址
            "body":{
                "grant_type"    : "client_credentials",
                "client_id"     : "YwtrR3YSTCHRrOP0bOmGwVSS",
                "client_secret" : "RDOdZUF3KXawMAKWgMgrrGqrl9FKeAvG"
            }
        }
    },

    #摄像头
    "CAMERA":{
        'enable' : True         # 是否启用 ： True -- 启用，False -- 禁用
    }
}

config['database'] = config['root_path'] + '/data/config.db'            #数据库
