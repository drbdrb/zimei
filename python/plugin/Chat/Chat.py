# -*- coding: utf-8 -*-
# @Autor: atlight
# @Date: 2019-12-26 09:35:35
# @LastEditTime: 2020-01-15 13:59:46
# @Description: 聊天机器人，只要实现Text消息响应即可。

import json
import logging
import re
import string
import urllib.request
from urllib.parse import urlencode
import jwt
from MsgProcess import MsgProcess, MsgType


class Chat(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue=msgQueue)
        self.gameTalk = False

    # 处理文本消息
    def Text(self, message):
        text = message['Data']
        # self.qingyunke(text)
        self.WXSpeech(text)

    def qingyunke(self, text):
        " 青云客聊天机器人 "
        if text is None:
            return
        url = r'http://api.qingyunke.com/api.php?key=free&appid=0&msg='
        sendurl = url + text
        url = urllib.parse.quote(sendurl, safe=string.printable)
        page = urllib.request.urlopen(url)
        if page.getcode() == 200:
            html = page.read().decode("utf-8")
        # 判断返回数据是否是字典,可能返回的是数字所以str
        if re.sub(r'{.*}', "", str(html)) == "":
            res = json.loads(html)['content']
            self.say(res)

    def WXSpeech(self, text):
        ''' 腾讯聊天机器人   '''
        if text is None:
            return
        payload = {
            'APPID': 'kWf7I8VjBre1BXP',
            'TOKEN': 'o2GQF8Ri73Crcn9WiGH8X3K4e6huGb',
            'EncodingAESKey': '2uetECGe8oob6bbSvLj4DBNjPh2epX1y8mws0pENF5g'
        }
        apiUrl = r'https://openai.weixin.qq.com/openapi/message/'
        header = {"username": "小美", "msg": text}
        headers = {'alg': "HS256"}
        query = jwt.encode(header, payload['EncodingAESKey'],
                           algorithm=headers['alg'], headers=headers).decode('ascii')
        url = apiUrl + payload['TOKEN']
        post_json = {"query": query}
        post_json = urlencode(post_json).encode('utf-8')
        page = urllib.request.urlopen(
            url, data=post_json, timeout=5)  # 响应时间定为了5秒
        # 判断网络请求成功
        if page.getcode() == 200:
            html = page.read().decode("utf-8")
            if re.search(r'{.*}', str(html)):
                res = json.loads(html)
                if 'answer_type' not in res.keys():
                    logging.warning(res)
                    return

                if res['answer_type'] == 'text':
                    answer = res['answer']
                    logging.info(answer)
                    self.say(answer)

                    if self.gameTalk: 
                        userWords = self.listen(15)
                        if userWords:
                            Triggers = ['退出', '停止', '关闭', '不玩了']
                            if not any(map(lambda trigger: trigger in userWords, Triggers)):
                                return self.WXSpeech(userWords)
                        logging.info('关闭连续对话')
                        self.gameTalk = False
                        return self.WXSpeech('退出游戏')                           

                    if '欢迎来到成语接龙' in answer:
                        userWords = self.listen()
                        Triggers = ['准备好了', '开始游戏']
                        if any(map(lambda trigger: trigger in userWords, Triggers)):
                            self.gameTalk = True
                            logging.info('开启连续对话')
                        return self.WXSpeech(userWords)
                 
                    if answer[-1] == '？' or answer[-1] == '?' and self.gameTalk is False:  # 一次连续对话
                        return self.WXSpeech(self.listen())
                    return             

                elif res['answer_type'] == 'music':
                    if res['ans_node_name'] == '音乐':
                        music_ans_detail = list(res['more_info'].values())[0]
                        music_dict = json.loads(music_ans_detail)
                        music_list = music_dict['play_command']['play_list']
                        songList = list()
                        for k in music_list:
                            songname = '{}--{}'.format(k['name'], k['author']).strip()
                            songList.append(
                                dict({'songname': songname, 'songurl':  k['url']}))
    
                        self.send(MsgType=MsgType.QuitGeekTalk, Receiver='ControlCenter')
                        answer = res['answer']
                        self.say(answer)

                        # 歌单格式: songList =[{'songname':name,'songurl':url},{...}...]
                        self.send(MsgType=MsgType.LoadPlugin, Receiver='ControlCenter', Data='Music')
                        self.send(MsgType=MsgType.Text, Receiver='Music', Data=songList)
                        return

                    elif res['ans_node_name'] == 'FM-笑话':
                        screen = res['ans_node_name'] + '功能尚未启用'
                        logging.debug(screen)                      
                        return
                
                elif res['answer_type'] == 'news':
                    try:                      
                        news_ans_detail = res['more_info']['news_ans_detail']                   
                        news_ans_detail = json.loads(news_ans_detail)
                        docs = news_ans_detail['data']['docs']
                    except Exception as e:
                        logging.debug("%s %s" % (news_ans_detail, e))
                        self.say('新闻获取失败')
                        return                    
                    titles = ''
                    text = ''               
                    for news in docs:
                        titles += (news['title'] + '\n')
                        text += (news['title'] + ':' + news['abs_s'] + '\n')
                    self.send(MsgType=MsgType.QuitGeekTalk, Receiver='ControlCenter')
                    self.send(MsgType=MsgType.Text, Receiver='Screen', Data=titles)
                    self.send(MsgType=MsgType.Text, Receiver='SpeechSynthesis', Data=text)
                    # logging.debug(text)

                else:                    
                    screen = res['ans_node_name'] + '功能尚未启用'
                    logging.debug(screen)
        else:
            self.gameTalk = False
            logging.warning('网络可能有点问题，请检查一下网络')
