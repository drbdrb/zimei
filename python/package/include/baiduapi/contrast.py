# encoding:utf-8
import base64
import json
import os
import urllib.request

import requests

import package.include.baiduapi.token as key
from package.base import Base, log


class Contrast_face(Base):
    '''视觉-人脸对比类'''

    def __init__(self):
        token_file  = os.path.join(self.config["root_path"],'runtime/token/face_token.txt')

        self.renlian_conf = self.config['BAIDUAPI']['renlian_conf']     #读取配置里人脸识别参数
        self.renlian_conf['token_file'] = token_file

        self.huoqu_token = key.Token(self.renlian_conf)
        log.info("在线人脸对比初始化完成")

    def success(self,jieguo):
        log.info(jieguo)

    def error(self,bug='bug'):
        log.info(bug)

    '''
    * 开始人脸对比
    * sou_name  -   源图片
    * new_name  -   对比图片
    '''
    def main(self, sou_name, new_name):
        datas = self.huoqu_token.main()
        if datas['state']:
            request_url = self.renlian_conf['api_url'] + "?access_token=" + datas['access_token']
        else:
            return 0
        with open(sou_name, 'rb') as f:
        # 参数images：图像base64编码
            img1 =base64.b64encode(f.read()).decode("utf-8")
        # 二进制方式打开图文件
        with open(new_name, 'rb') as f:
        # 参数images：图像base64编码
            img2 = base64.b64encode(f.read()).decode("utf-8")

        params = json.dumps(
            [{"image":str(img1), "image_type": "BASE64",
            "face_type": "LIVE", "quality_control": "LOW"},
             {"image":str(img2), "image_type": "BASE64",
              "face_type": "IDCARD", "quality_control": "LOW"}]).encode("utf-8")
        try:
            request = urllib.request.Request(url=request_url, data=params)
            request.add_header('Content-Type', 'application/json')      #表头
            response = urllib.request.urlopen(request,timeout=20)
        except():
            return 0
        try:
            content = response.read()
            content = bytes.decode(content) #去掉字典b头
            json_str = json.loads(content)
            if 'result' in json_str.keys():
                if type(json_str['result']) is dict:
                    return json_str['result']['score']

            return 0
        except():
            return 0

if __name__ == '__main__':

    Duibi().main()
