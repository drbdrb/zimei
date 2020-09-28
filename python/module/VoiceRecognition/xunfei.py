import api.XFapi.config as config
import requests
import time
import hashlib
import base64
import json,logging

class xunfei():
    """
    讯飞语音识别模块
    """

    def __init__(self):
        self.config = config.config()
        self.URL = "http://openapi.xfyun.cn/v2/aiui"
        self.APPID = self.config["APPID"]
        self.API_KEY = self.config["API_KEY"]
        self.AUE = "raw"
        self.AUTH_ID = self.config["AUTH_ID"]
        self.DATA_TYPE = "audio"
        self.SAMPLE_RATE = "16000"
        self.SCENE = "main"
        self.RESULT_LEVEL = "complete"
        self.LAT = "39.938838"
        self.LNG = "116.368624"
        self.FILE_PATH = "demo.wav"

    def buildHeader(self):
        curTime = str(int(time.time()))
        param = "{\"result_level\":\""+self.RESULT_LEVEL+"\",\"auth_id\":\""+self.AUTH_ID+"\",\"data_type\":\""+self.DATA_TYPE+"\",\"sample_rate\":\""+self.SAMPLE_RATE+"\",\"scene\":\""+self.SCENE+"\",\"lat\":\""+self.LAT+"\",\"lng\":\""+self.LNG+"\"}"
        paramBase64 = base64.b64encode(param.encode())
        m2 = hashlib.md5()
        m2.update(self.API_KEY.encode() + curTime.encode() + paramBase64)
        checkSum = m2.hexdigest()
        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.APPID,
            'X-CheckSum': checkSum,
        }
        return header

    def main(self, data):

        try:
            r = requests.post(self.URL, headers=self.buildHeader(), data=data)

            data =json.loads(r.text) #{'data': [{'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': '皑'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '如'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '山上'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '雪'}]}], 'sn': 1, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 1, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '皎'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '若'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '云'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '间'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '月'}]}], 'sn': 2, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 2, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '闻'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '君'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '有'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '两'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '意'}]}], 'sn': 3, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 3, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '故'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '来'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '相'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '决绝'}]}], 'sn': 4, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 4, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '今日'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '斗'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '酒会'}]}], 'sn': 5, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 5, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '明'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '旦'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '沟'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '水头'}]}], 'sn': 6, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 6, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '躞'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '蹀'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '御'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '沟'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '上'}]}], 'sn': 7, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 7, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '沟'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '水'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '东西'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '流'}]}], 'sn': 8, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 8, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '凄凄'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '复'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '凄凄'}]}], 'sn': 9, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 9, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '嫁娶'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '不'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '须'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '啼'}]}], 'sn': 10, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 10, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '愿'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '得'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '一'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '心'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '人'}]}], 'sn': 11, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 11, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '白头'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '不'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '相'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '离'}]}], 'sn': 12, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 12, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '竹竿'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '何'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '袅袅'}]}], 'sn': 13, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 13, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '鱼尾'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '和'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '喜'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '喜'}]}], 'sn': 14, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 14, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '男儿'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '重'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '意气'}]}], 'sn': 15, 'ed': 0, 'bg': 0, 'ls': False}, 'result_id': 15, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}, {'json_args': {'accent': 'mandarin', 'language': 'zh-cn'}, 'text': {'ws': [{'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '何'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '用'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '钱'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '刀'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': '为'}]}, {'bg': 0, 'cw': [{'sc': 0, 'w': ''}]}], 'sn': 16, 'ed': 0, 'bg': 0, 'ls': True}, 'result_id': 16, 'sub': 'iat', 'auth_id': '6adcfb2952316f599a01fdab85757cca'}], 'code': '0', 'sid': 'ara038cdaec@dx0001126f411a094000', 'desc': 'success'}

            printf = ""
            for x in data["data"]:
                for y in x['text']['ws']:
                    result = y["cw"][0]["w"]
                    # if result=="":
                    #     result=","
                    printf += result
            # printf = printf[:-1]+""
            logging.debug('语音识别已返回')
            return  printf
        except Exception as f:
            logging.error("语音识别遇到错误") 
































        # logging.info('语音识别...')
        # try:       
        #     bdResult = client.asr(speech=data, options={ 'cuid': self.CUID})
        # except Exception as e:
        #     logging.error('网络故障! %s' % e)
        #     return False
        # logging.debug('语音识别已返回')
        # text = ''

        # if bdResult['err_msg'] == 'success.':  # 成功识别
        #     for t in bdResult['result']:
        #         text += t
        #     logging.info(text)
        #     return text

        # elif bdResult['err_no'] == 3301:  # 音频质量过差
        #     text = '我没有听清楚您说的话'
        #     logging.info(text)
        #     return

        # elif bdResult['err_no'] == 3302:  # 鉴权失败
        #     text = '鉴权失败，请与开发人员联系。'
        #     logging.warning(text)
        #     return 

        # elif bdResult['err_no'] == 3304 or bdResult['err_no'] == 3305:  # 请求超限
        #     text = '请求超限，请与开发人员联系。'
        #     logging.warning(text)
        #     return 

        # text = '语音识别错误,代码{}'.format(bdResult['err_no'])
        # logging.error(text)    