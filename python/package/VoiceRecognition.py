# -*- coding: utf-8 -*-
# @Autor: atlight
# @Date: 2019-12-29 13:34:16
# @LastEditTime: 2020-01-12 16:32:50
# @Description: 语音识别类，可以增加多家产品,暂实现百度语音识别
from package.BDaip.speech import AipSpeech
import logging
import uuid
from package.mylib import mylib


class VoiceRecognition:
    ''' 语音识别 '''
    CUID = hex(uuid.getnode())

    def Start(self, data):
        return self.BDVoicerecognition(data)

    def BDVoicerecognition(self, data):
        BDAip = mylib.getConfig()['BDAip']
        APP_ID = BDAip['APP_ID']
        API_KEY = BDAip['API_KEY']
        SECRET_KEY = BDAip['SECRET_KEY']
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        # client.setConnectionTimeoutInMillis = 5000  # 建立连接的超时毫秒
        # client.setSocketTimeoutInMillis = 5000  # 传输数据超时毫秒

        logging.info('语音识别...')
        try:       
            bdResult = client.asr(speech=data, options={'dev_pid': 1536, 'cuid': VoiceRecognition.CUID})
        except Exception as e:
            logging.error('网络故障! %s' % e)
        logging.debug('语音识别已返回')
        text = ''

        if bdResult['err_msg'] == 'success.':  # 成功识别
            for t in bdResult['result']:
                text += t
            logging.info(text)
            return text

        elif bdResult['err_no'] == 3301:  # 音频质量过差
            text = '我没有听清楚您说的话'
            logging.info(text)
            return

        elif bdResult['err_no'] == 3302:  # 鉴权失败
            text = '鉴权失败，请与开发人员联系。'
            logging.warning(text)
            return 

        elif bdResult['err_no'] == 3304 or bdResult['err_no'] == 3305:  # 请求超限
            text = '请求超限，请与开发人员联系。'
            logging.warning(text)
            return 

        text = '语音识别错误,代码{}'.format(bdResult['err_no'])
        logging.error(text)
