# -*- coding: UTF-8 -*-
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import logging
import requests
import ruamel.yaml as yaml


class mylib:
    '''我的基本类库'''

    @staticmethod
    def yamlLoad(yamlfile):
        ''' 读取yamlfile的数据并返回 失败返回False '''
        try:
            with open(yamlfile, mode='r', encoding='utf-8') as f:
                data = yaml.load(f, Loader=yaml.RoundTripLoader)
                return data
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def yamlDump(data, yamlfile):
        ''' 存储数据到yamlfile文件中 成功返回True 失败返回False '''
        try:
            with open(yamlfile, mode='w') as f:
                yaml.dump(data, f, Dumper=yaml.RoundTripDumper, allow_unicode=True, encoding='utf-8')
                return True
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def getConfig():
        ''' 读取config.yaml 取得全局配置  '''
        file = 'config.yaml'
        return mylib.yamlLoad(yamlfile=file)
       
    @staticmethod
    def saveConfig(config):
        ''' 保存全局配置数据到config.yaml'''
        file = 'config.yaml'
        return mylib.yamlDump(data=config, yamlfile=file)

    # http访问
    @staticmethod
    def http_post(url, postdata={}):
        res = {'code': '9999', 'msg': '[error:mylib.http_post]网络请求失败！', 'data': ''}
        try:
            response = requests.get(url, params=postdata, timeout=5)       # post不兼容本服务器
            if int(response.status_code) == 200:
                res['code'] = '0000'
                res['msg'] = '请求成功！'
                res['data'] = response.text
        # 没有网络或者请求超时依然返回,正常情况下也返回
        finally:
            return res

    # http访问2
    @staticmethod
    def http_urllib(url, postdata={}, timeout=5):
        try:
            res = {'code': '9999', 'msg': '[error:mylib.http_post]网络请求失败！', 'data': ''}
            data = urlencode(postdata)
            req = Request(url, data.encode('utf-8'))
            f = urlopen(req, timeout=timeout)
            if f.getcode() == 200:
                response = f.read().decode()
                res['code'] = '0000'
                res['msg'] = '请求成功！'
                res['data'] = response
            else:
                return res
        # 没有网络或者请求超时依然返回,正常情况下也返回
        finally:
            return res

    @staticmethod
    def SoundCardIsPlay():
        ''' 声卡是否在播放   是则返回True 否则返回False '''
        cmd = 'cat /proc/asound/wm8960soundcard/pcm0p/sub0/status' 
        return "RUNNING" in os.popen(cmd).read()

    @staticmethod
    def strHasany(source, test):
        ''' 查找source字符串，是否包含了test集合中的任意一个子字符串
        例:strHasany(text,['打开屏幕'，'启动屏幕','点亮屏幕']) '''
        for t in test:
            if t in source:
                return True
        return False

    @staticmethod
    def ChineseNum2Arab(oriStr):
        ''' 将字符串中的汉字数字转为数值 '''
        def chinese2digits(uchars_chinese):
            common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
                                        '九': 9, '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
            common_used_numerals = {}
            for key in common_used_numerals_tmp:
                common_used_numerals[key] = common_used_numerals_tmp[key]
            total = 0
            r = 1  # 表示单位：个十百千...
            for i in range(len(uchars_chinese) - 1, -1, -1):
                val = common_used_numerals.get(uchars_chinese[i])
                if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
                    if val > r:
                        r = val
                        total = total + val
                    else:
                        r = r * val
                        # total =total + r * x
                elif val >= 10:
                    if val > r:
                        r = val
                    else:
                        r = r * val
                else:
                    total = total + r * val
            return total

        num_str_start_symbol = ['一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十']
        more_num_str_symbol = ['零', '一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿']
        lenStr = len(oriStr)
        aProStr = ''
        if lenStr == 0:
            return aProStr 
        hasNumStart = False
        numberStr = ''
        for idx in range(lenStr):
            if oriStr[idx] in num_str_start_symbol:
                if not hasNumStart:
                    hasNumStart = True 
                numberStr += oriStr[idx]
            else:
                if hasNumStart:
                    if oriStr[idx] in more_num_str_symbol:
                        numberStr += oriStr[idx]
                        continue
                    else:
                        numResult = str(chinese2digits(numberStr))
                        numberStr = ''
                        hasNumStart = False
                        aProStr += numResult
                aProStr += oriStr[idx]
                pass 
        if len(numberStr) > 0:
            resultNum = chinese2digits(numberStr)
            aProStr += str(resultNum)
        return aProStr

    @staticmethod
    def versionCompare(v1="1.1.1", v2="1.2"):
        '''
        比较版本号
        v1 原版本号，v2 新版本号
        返回：
        1 - 需要更新/0 - 不需要/ -1 - 不需要/ -2 -- 格式错误 
        '''
        v1 = re.sub(r'^\D', "", v1)
        v2 = re.sub(r'^\D', "", v2)
        v1_check = re.match("\d+(\.\d+){0,2}", v1)
        v2_check = re.match("\d+(\.\d+){0,2}", v2)
        if v1_check is None or v2_check is None or v1_check.group() != v1 or v2_check.group() != v2:
            return -2   #"版本号格式不对，正确的应该是x.x.x,只能有3段"
        v1_list = v1.split(".")
        v2_list = v2.split(".")
        v1_len = len(v1_list)
        v2_len = len(v2_list)
        if v1_len > v2_len:
            for i in range(v1_len - v2_len):
                v2_list.append("0")
        elif v2_len > v1_len:
            for i in range(v2_len - v1_len):
                v1_list.append("0")
        else:
            pass
        for i in range(len(v1_list)):
            if int(v1_list[i]) > int(v2_list[i]):
                return -1
            if int(v1_list[i]) < int(v2_list[i]):
                return 1
        return 0
