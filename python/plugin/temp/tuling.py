# -*- coding: utf-8 -*-
import hashlib
import json
import time
import os
import re
import string
import urllib.request
from urllib.parse import urlencode

import jwt
from package.base import Base, log
from plugin import Plugin


class Tuling(Base,Plugin):

    def __init__(self, public_obj ):
        self.public_obj = public_obj

        self.music_path = '/music/'
        if os.path.exists(self.music_path)==False:
            os.system('sudo mkdir -p '+ self.music_path)

        self.payload = {
            'APPID' :'kWf7I8VjBre1BXP',
            'TOKEN' : 'o2GQF8Ri73Crcn9WiGH8X3K4e6huGb',
            'EncodingAESKey' : '2uetECGe8oob6bbSvLj4DBNjPh2epX1y8mws0pENF5g'
        }

        self.apiUrl  =  'https://openai.weixin.qq.com/openapi/message/'


    #保存音乐列表
    def save_music_list(self, sajson={}, list_name=''):
        save_dict = []
        for k in sajson:
            fname     = k['author']+'-'+k['name']
            md5_fname = hashlib.md5(fname.encode('utf-8')).hexdigest()
            play_list = {
                'url': k['url'],
                'name': k['name'],
                'hashname': md5_fname,
                'author': k['author']
            }
            save_dict.append(play_list)

        save_str = json.dumps(save_dict)
        this_play_list = os.path.join(self.music_path,'this_play_list.json')
        with open(this_play_list, 'w') as fso:
            fso.write(save_str)

        rejson = {'state': True, 'enter': 'mqtt', 'optype': 'start','ptype':'stay', 'name':'Music', 'data': list_name}
        enjson = {'optype': 'action','enter': 'mqtt','type': 'system','state': True,'msg': 'QQ音乐导入','data':rejson}
        self.public_obj.master_conn.send(enjson)

        del save_dict,play_list,save_str

    #保存fm列表
    def save_fm_list(self, sajson={}, list_name=''):
        save_dict = []
        for k in sajson:
            fname     = k['name']
            md5_fname = hashlib.md5(fname.encode('utf-8')).hexdigest()
            play_list = {
                'url': k['url'],
                'name': k['name'],
                'hashname': md5_fname
            }
            save_dict.append(play_list)

        save_str = json.dumps(save_dict)
        this_play_list = os.path.join(self.music_path,'this_playfm_list.json')
        with open(this_play_list, 'w') as fso:
            fso.write(save_str)

        del save_dict,play_list,save_str


    '''
    插件入口
    '''
    def start(self,name):
        try:
            if type(name) is not dict:
                return {'state':False,'data': '我不知道你说了啥','type':'system', 'msg':'参数1，需要输入图灵交流的文字。字符串类型！'}


            header = {"username":"小美","msg":name['data']}

            headers = {'alg': "HS256"}
            query = jwt.encode(header, self.payload['EncodingAESKey'],algorithm=headers['alg'],headers=headers).decode('ascii')

            url = self.apiUrl + self.payload['TOKEN']

            post_json = {"query":query}
            post_json = urlencode(post_json).encode('utf-8')
            
            page = urllib.request.urlopen(url,data=post_json, timeout = 25)      #响应时间定为了25秒

            #判断网络请求成功
            if page.getcode() == 200:
                html = page.read().decode("utf-8")
                #判断返回数据是否是字典,可能返回的是数字所以str
                if re.search(r'{.*}', str(html)):
                    res = json.loads(html)
                    # print(res)

                    #删除字典内容和网址
                    is_stop = False
                    if res['answer_type']=='text':
                        data = res['answer']

                    elif res['answer_type']=='music':
                        #print(res['more_info'])
                        music_ans_detail = list(res['more_info'].values())[0]
                        music_dict = json.loads(music_ans_detail)

                        if res['ans_node_name']=='音乐':
                            play_command = music_dict['play_command']
                            play_list = play_command['play_list']
                            #保存当前播放的音乐列表
                            self.save_music_list(play_list, str(res['answer']))

                        elif res['ans_node_name']=='FM-笑话':
                            play_command = music_dict['audio_play_command']
                            play_list = play_command['play_list']

                            self.save_fm_list(play_list, str(res['answer']))

                        data = res['answer']
                        is_stop = True

                    else:
                        data = res['ans_node_name'] + '功能尚未启用'

                    if data == '': data = "不知道"
                    del res,page,url,html

                    return {'state':True,'data':data ,'type':'tuling','msg':'对话机器人回复成功！','stop': True}
                else:
                    return {'state':False,'data':'我想不出来。','type':'system','msg':'服务器返回的不是字典！'}
            else:
                return {'state':False,'data':'网络可能有点问题，请检查一下网络哦。','type':'system','msg':'请求失败！'}
        except Exception as bug:
            log.warning('对话机器人超时',bug)
            return {'state':False,'data':'网络可能有点问题，需要检查一下网络。','type':'system','msg':'连接对话机器人服务器超时！'}

if __name__ == '__main__':


    print( Tuling().main('520'))
