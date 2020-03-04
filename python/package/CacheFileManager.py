# -*- coding: utf-8 -*-
# @Author: Guanghui Sun
# @Date: 2020-01-01 15:42:36
# @LastEditTime: 2020-01-21 14:34:59
# @Description:  cache文件管理方法

import time
import re
import datetime
import json
import os
import logging
#import yaml

class CacheFileManager:
    '''
    cache文件管理办法,为减少开销,所有方法都是静态方法,直接调用即可,每次在创建cache文件或访问时 
    用add(file)方法加入到管理列表,以后可以用delfile(days)方法删除超出days天的文件.
    只有这两个函数.
    '''    
    accessTimeFile = r'./data/CacheFileAccessTime.json'
    #accessTimeFile = r'./data/CacheFileAccessTime.yaml'
    dtfmt = r"%Y-%m-%d %H:%M:%S"
    @staticmethod
    def __readFile2dict():
        if os.path.exists(CacheFileManager.accessTimeFile):
            if os.path.getsize(CacheFileManager.accessTimeFile) >= 1:
                with open(CacheFileManager.accessTimeFile, 'r') as fp:
                    try:
                        data = json.load(fp)
                        #data = yaml.load(fp,Loader=yaml.FullLoader)
                        return dict(data)                 
                    except:
                        logging.warning('重建:%s' % CacheFileManager.accessTimeFile)
        return dict()

    @staticmethod
    def __writeDict2file(dicts):
        with open(CacheFileManager.accessTimeFile, 'w') as fp:
            # yaml.dump(dicts,fp,encoding='utf-8',allow_unicode=True , sort_keys=True)
            json.dump(dicts, fp, ensure_ascii=False, indent=4, sort_keys=True)
            
    @staticmethod
    def scanCacheFile(cacheFolder):
        now = datetime.datetime.now()
        accessTime = CacheFileManager.__readFile2dict()
        for file in os.listdir(cacheFolder):
            absFile = os.path.abspath(os.path.join(cacheFolder, file))
            if os.path.isfile(absFile) and (absFile not in accessTime.keys()):
                accessTime[absFile] = now.strftime(CacheFileManager.dtfmt)                
        CacheFileManager.__writeDict2file(accessTime)

    @staticmethod
    def add(file):
        '''将文件file加入管理列表,在创建文件和访问文件时都必须调用此方法'''
        file = os.path.abspath(file)        
        accessTime = CacheFileManager.__readFile2dict()
        accessTime[file] = datetime.datetime.now().strftime(CacheFileManager.dtfmt)
        CacheFileManager.__writeDict2file(accessTime)
        
    @staticmethod
    def delfile(days=60):            
        '''将管理列表中超出days天没有访问的文件删除,days也可以为小数!'''

        Folder = [r'./runtime/soundCache', r'/music/cache']
        for f in Folder:
            CacheFileManager.scanCacheFile(f)

        delta = datetime.timedelta(days=days)
        now = datetime.datetime.now()
        accessTime = CacheFileManager.__readFile2dict()
        delfiles = list()
        for (file, atime) in accessTime.items():
            if delta < now - datetime.datetime.strptime(atime, CacheFileManager.dtfmt):
                delfiles.append(file)
        for file in delfiles:
            print('删除cache文件:', file)
            accessTime.pop(file)        
            if os.path.exists(file):
                os.remove(file)
        CacheFileManager.__writeDict2file(accessTime)


if __name__ == "__main__":
    CacheFileManager.delfile()