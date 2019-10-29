# -*- coding: utf-8 -*-
import base64
import json
import os
import re
import urllib.request

import requests

import package.include.baiduapi.token as key
from package.base import Base, log

#参考资料https://www.cnblogs.com/Pond-ZZC/p/6718205.html
#播放声音https://blog.csdn.net/xiongtiancheng/article/details/80577478

class Shibie(Base):
    '''百度语音识别'''

    def __init__(self):
        token_file  = os.path.join(self.config["root_path"],'runtime/token/yuyin_token.txt')
        self.yuyin_conf = self.config['BAIDUAPI']['yuyin_conf']     #读取配置里人脸识别参数
        self.yuyin_conf['token_file'] = token_file
        self.huoqu_token = key.Token(self.yuyin_conf)


    '''（私有方法）__yuyin_shibie_api#   链接百度语音识别的api方法
    参数：
        audio_data :  二进制
    返回：
        正常:返回识别出的文字.  类型： 列表
        识别异常：返回 识别失败" 类型： 字符串
        网络异常:返回No_network#没有网络
    '''
    def __yuyin_shibie_api(self,audio_data):
        token = self.huoqu_token.main()
        if token['state'] == False:
            return token

        speech_data = base64.b64encode(audio_data).decode("utf-8")
        #用Base64编码具有不可读性，需要解码后才能阅读
        speech_length = len(audio_data)
        post_data = {"format":"wav","rate": 16000,
        "channel": 1,"cuid":self.config['BAIDUAPI']['CUID'],
        "token": token['access_token'], "speech": speech_data,"len": speech_length}

        url = self.yuyin_conf['shibie_api_url']
        json_data = json.dumps(post_data).encode("utf-8")
        json_length = len(json_data)

        try:
            req = urllib.request.Request(url,data=json_data)
            req.add_header("Content-Type", "application/json")
            req.add_header("Content-Length", json_length)
            resp = urllib.request.urlopen(req,timeout=20)##合成时间不多，识别最耗时
            resp = resp.read()
            resp_data = json.loads(resp.decode("utf-8"))

        except:
            log.warning('超时s2')
            return {'enter':'voice','state': False,'data':'网络可能有点问题，请检查网络。','msg':{'errtype':'neterror'}}

        if resp_data["err_no"] == 0:
            return {'enter':'voice','state': True,'data':resp_data["result"][0],'msg':'识别成功！'}
        else:
            return {'enter':'voice','state': False,'data':'','msg':'语音识别失败。'}

    '''zhixing# 对外调用接口
    参数：
        name: 声音文件 ,类型是wav
    返回：
        正常:返回识别出的文字  类型：字符串
        网络异常:返回No_network#没有网络   类型：字符串
    '''
    def main(self,audio_data):
        try:
            resp = self.__yuyin_shibie_api(audio_data)
            del audio_data
            log.info('识别结果',resp)
            if resp['state'] == False:
                return resp
            else:
                return resp
        except :
            resp = {'enter':'voice','state': False,'data':'','msg':'识别失败。'}
            return resp

if __name__ == '__main__':
    lei=Shibie()
    print(lei.main("data/yuyin/wo.wav"))
