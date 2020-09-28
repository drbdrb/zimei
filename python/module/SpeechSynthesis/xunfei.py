import api.XFapi.config as config
import requests,wave
import time
import hashlib
import base64
import json,logging

class xunfei():
    """
    讯飞语音合成模块
    """

    def __init__(self, CUID):
        self.config = config.config()
        self.URL = "http://openapi.xfyun.cn/v2/aiui"
        self.APPID =  self.config["APPID"]
        self.API_KEY = self.config["API_KEY"]
        self.AUE = "raw"
        self.AUTH_ID = self.config["AUTH_ID"]
        self.DATA_TYPE = "text"
        self.SAMPLE_RATE = "16000"
        self.SCENE = "IFLYTEK.tts"
        self.RESULT_LEVEL = "complete"
        self.LAT = "39.938838"
        self.LNG = "116.368624"
        
  
    def buildHeader(self):
        
        curTime = str(int(time.time()))
        param = '{"sfl":1,"aue":"lame","ent":"aisound","vcn":"xiaoyan","result_level":"'+self.RESULT_LEVEL+'","auth_id":"'+self.AUTH_ID+'","data_type":"'+self.DATA_TYPE+'","sample_rate":"'+self.SAMPLE_RATE+'","scene":"'+self.SCENE+'","lat":"'+self.LAT+'","lng":"'+self.LNG+'"}'
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
        
    def main(self, text, fileName):

        try:
            r = requests.post(self.URL, headers=self.buildHeader(), data=text.encode('utf-8')   )
            resuit = json.loads(r.text)
            wf = open(fileName,'wb')
            wf.write( base64.b64decode(resuit["data"][0]["content"]) ) 
            wf.close() 
            logging.debug('语音合成已返回')
            return fileName
        except Exception as f:
            logging.error("语音合成遇到错误") 