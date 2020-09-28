from api.BDaip import AipSpeech, config
import uuid
import logging

class baidu():

    def __init__(self):
        self.config = config()
        self.CUID = hex(uuid.getnode())

    def main(self, data):
        APP_ID = self.config['APP_ID']
        API_KEY = self.config['API_KEY']
        SECRET_KEY = self.config['SECRET_KEY']
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        # client.setConnectionTimeoutInMillis = 5000  # 建立连接的超时毫秒
        # client.setSocketTimeoutInMillis = 5000  # 传输数据超时毫秒

        logging.info('语音识别...')
        try:       
            bdResult = client.asr(speech=data, options={'dev_pid': 1536, 'cuid': self.CUID})
        except Exception as e:
            logging.error('网络故障! %s' % e)
            return False
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