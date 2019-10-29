# -*- coding: utf-8 -*-
from package.base import Base,log
import os,json,requests,time

class Token(Base):
    '''百度语音识别'''

    def __init__(self, conf_info ):
        self.conf_info = conf_info

    '''wenjian_guoqi#文件过期，指的是该文件修改时间距离现在没有超过25天
        参数 :
            wenjian: 必须是一个文件，如TXT等等
        返回：
            没有超过25天就返回False
            超过就返回  True
    '''
    def wenjian_guoqi(self, wenjian):
        try:
            wenjian_shijianchuo = os.path.getmtime(wenjian)
            #print('时间差',int(time.time())-int(wenjian_shijianchuo))  25* (24*60*60)
            if int(time.time())-int(wenjian_shijianchuo) >= 2160000:
                return True
            else:
                return False
        except:
           # print('识别过期出差错了')
            return True

    '''联网获取token
    返回：
        正常： 返回token
        网络异常;返回'No_network'
    '''
    def __lianwang_huoqutoken(self):
        log.info('正在网络请求：access_token')
        #获取token秘钥
        url  = self.conf_info['token_url']
        body = self.conf_info['body']

        try:
            r = requests.post(url,data=body,verify=True,timeout=5)
            respond = json.loads(r.text)
            return {'state': True, 'access_token': respond["access_token"], 'msg':'获取access_token成功'}
        except:
            return {'state': False,'access_token':'','msg':'网络连接超时'}
            #在这里无论是没有网络还是获取token秘钥失败和异常都返回没有网络


    '''（私有方法）__huancun_token#缓存联网获取的token25天
        返回：
            正常： 返回token
            网络异常;返回'No_network'
    '''
    def __huancun_token(self):
        token_file = self.conf_info['token_file']
        jiancha = os.path.exists( token_file )#检查

        log.info('是否存在本地缓存access_token', jiancha)

        if jiancha == False:        #没有该文件的话，创建一下，并写入，在返回token
            p_path = os.path.dirname(token_file)
            if os.path.isdir(p_path)==False:
                os.system('sudo mkdir -p '+ p_path)
                
            token = self.__lianwang_huoqutoken()
            if token['state']==False:
                return token
            with open(token_file,'w',encoding='utf-8') as of:
                of.write(token['access_token'])         #初始化写入的是tokenk
                return {'state': True, 'access_token': token["access_token"], 'msg':'获取access_token成功'}

        else:       #如果有的话,过滤获取得到tokenk在返回
            if self.wenjian_guoqi(token_file)==True:
                log.warning('本地缓存已过期')
                os.remove(token_file)
                #time.sleep(1)
                return self.__huancun_token()
            else:
                log.info('正在读取本地缓存access_token')
                f_token = ''
                with open(token_file,'r', encoding='utf-8') as of:
                    f_token = of.read()

                if f_token == '':
                    os.remove(token_file)
                    #time.sleep(1)
                    return self.__huancun_token()
                else:
                    return {'state': True, 'access_token': f_token, 'msg':'获取access_token成功'}

    '''（私有方法）__huoqu_token #获取百度api的token的方法
        参数：
            无
        返回：
            正常：返回百度api的token
            异常：返回 No_network#没有网  类型;字符串
    '''
    def main(self):
        return self.__huancun_token()