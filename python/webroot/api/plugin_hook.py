import json
import os
import copy

from .ApiBase import ApiBase
from package.mylib import mylib

class plugin_hook(ApiBase):
    '''
    插件WebApi钩子
    '''

    def __init__(self, handler):
        super().__init__(handler)

        self.pluginpath = r'./plugin'


    # 加载本地插件列表
    def __load_pugin_html(self, fileext = '.css'):
        file_docs = ''

        for filedir in os.listdir(self.pluginpath):
            if os.path.isdir(os.path.join(self.pluginpath, filedir)) and filedir != '__pycache__':
                html_path = os.path.join(self.pluginpath, filedir, 'html')
                if os.path.isdir(html_path):
                    for s in os.listdir(html_path):
                        cssjs = os.path.join(html_path, s)
                        if os.path.isfile(cssjs) and os.path.splitext(cssjs)[1] == fileext:
                            if fileext=='.js':
                                return cssjs.replace('./plugin','/plugin',1)
                            with open(cssjs, 'r') as f:
                                file_docs += f.read()

        return file_docs

    def main(self):
        # 获取所有插件中HTML代码
        if self.query['get']=='html':
            return self.__load_pugin_html('.html')

        # 获取所有插件中CSS样式代码
        if self.query['get']=='css':
            return self.__load_pugin_html('.css')

        # 获取所有插件中JS代码
        if self.query['get']=='js':
            return self.__load_pugin_html('.js')          
