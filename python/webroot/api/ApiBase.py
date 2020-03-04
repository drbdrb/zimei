import json
import sys
import os
from urllib import parse

sys.path.append(os.getcwd())
from package.mylib import mylib

class ApiBase():
    '''
    WebApi 基本类，所有具体操作需继承此类，基本已封装好常用的常量和变量   
    self.query -- 为客户端请求参数    
    '''

    def __init__(self, handler):
        self.mimetype = handler.mimetype
        self.command = handler.command

        if self.command=='OPTIONS':
            handler.send_content('', self.mimetype, 200)
            return

        self.query = {}
        if hasattr(handler, 'query'):
            query = handler.query
            if len(query)>0:
                argv_dict = parse.parse_qs(query)
                if len(argv_dict) > 0:
                    for argv_item in argv_dict:
                        argv_dict[argv_item] = argv_dict[argv_item][0]
                    self.query = argv_dict
                del argv_dict

        self.config = mylib.getConfig()  # 取全局配置
        self.handler = handler

    def main(self):
        data = '感谢使用自美人工智能系统'
        return data
                