
# -*- coding:utf-8 -*-

import websocket
import hashlib
import base64
import hmac
import json
import logging
from urllib.parse import urlencode
import time
import ssl
from email.utils import formatdate
from threading import Thread


websocket_instance = {}
# 讯飞语音听写WebApi的接口地址
XF_URL = 'wss://iat-api.xfyun.cn/v2/iat'
HTTP_HEADER = "GET /v2/iat HTTP/1.1"
# 采样率
SAMPLE_RATE = 16000

FRAME_SIZE = 5120  # 每一帧的音频大小(单位:字节)
FRAME_INTERVEL = 0.04  # 发送音频间隔(单位:s),
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class VTTXunFei:
    def __init__(self):
        self.app_id = None
        self.ak = None
        self.sk = None
        self.url = None
        self.Algorithm = "hmac-sha256"
        self.BusinessArgs = {"domain": "iat",
                             "language": "zh_cn",
                             "accent": "mandarin"}

    def login(self, app_id, ak, sk):
        """
        :param app_id:在控制台-我的应用-语音听写（流式版）获取APPID
        :param ak: 在控制台-我的应用-语音听写（流式版）获取APIKey
        :param sk: 在控制台-我的应用-语音听写（流式版）获取APISecret
        :return:
        """
        self.ak = ak
        self.sk = sk
        self.app_id = {"app_id": app_id}
        self.url = self.create_url()
        websocket.enableTrace(False)

    def set_language(self, lang: str):
        """
        默认是普通话, 不需要处理, 仅当lang是别的值时, 才需要处理.
        lang可能的值:
            'zh_eng',  'mandarin', 'eng',
            'zh_ct'(粤语), 'zh_sc'(四川), 'zh_remote'
        """
        if 'eng' == lang:
            self.BusinessArgs['language'] = 'en_us'
        elif 'zh_sc' == lang:
            self.BusinessArgs['accent'] = 'lmz'
        elif 'zh_ct' == lang:
            self.BusinessArgs['accent'] = 'minnanese'

    def create_url(self):
        # RFC1123 时间字符串
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        signature_origin = "host: ws-api.xfyun.cn\n"
        signature_origin += "date: {}\n".format(date)
        signature_origin += HTTP_HEADER
        signature_sha = hmac.new(
            self.sk.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = ('api_key="{}", algorithm="{}", ' +
                                'headers="{}", signature="{}"').format(
            self.ak, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = '{}?{}'.format(XF_URL, urlencode(v))
        return url

    def upload(self, audio_file_path):
        ws = websocket.WebSocketApp(self.url,
                                    on_open=VTTXunFei.on_open,
                                    on_message=VTTXunFei.on_message,
                                    on_error=VTTXunFei.on_error,
                                    on_close=VTTXunFei.on_close)
        websocket_instance[ws] = {
            "app_id": self.app_id,
            "file_path": audio_file_path,
            "business": self.BusinessArgs,
            "data": []
        }
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        ret = websocket_instance.pop(ws)
        return ret

    @staticmethod
    def on_open(ws):
        app_id = websocket_instance[ws].get("app_id")
        file_path = websocket_instance[ws].get("file_path")
        business = websocket_instance[ws].get("business")

        def run(*args):
            # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
            status = STATUS_FIRST_FRAME
            raw = {
                "data": {
                    "status": 1,
                    "format": "audio/L16;rate={}".format(SAMPLE_RATE),
                    "encoding": "raw"
                }}

            with open(file_path, "rb") as fp:
                while True:
                    buf = fp.read(FRAME_SIZE)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME

                    raw["data"]["audio"] = str(base64.b64encode(buf), 'utf-8')
                    # 第一帧处理
                    if status == STATUS_FIRST_FRAME:
                        raw["data"]["status"] = 0
                        # appid 必须带上，只需第一帧发送
                        raw["common"] = app_id
                        # 发送第一帧音频，带business 参数
                        raw['business'] = business
                        ws.send(json.dumps(raw))
                        status = STATUS_CONTINUE_FRAME

                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        raw["data"]["status"] = 1
                        ws.send(json.dumps(raw))

                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        raw["data"]["status"] = 2
                        ws.send(json.dumps(raw))
                        time.sleep(1)
                        break
                    time.sleep(FRAME_INTERVEL)
            ws.close()
        Thread(target=run).start()

    @staticmethod
    def on_close(ws):
        """收到websocket关闭的处理"""
        pass

    @staticmethod
    def on_error(ws, error):
        """收到websocket错误的处理"""
        logging.error(str(error))

    @staticmethod
    def on_message(ws, message):
        """收到websocket消息的处理"""
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]

            websocket_instance[ws]['sid'] = sid
            websocket_instance[ws]['code'] = code
            if code != 0:
                err_msg = json.loads(message)["message"]
                websocket_instance[ws]['err_msg'] = err_msg
            else:
                data = json.loads(message)["data"]
                websocket_instance[ws]['data'].append(data)
        except Exception as e:
            logging.error(e)
            websocket_instance[ws]['err_msg'] = str(e)

class Shibie():
    def main(self,audio_file_path):
        audio_file_path="/keyicx/python/data/yuyin/wo.wav"
        """测试讯飞的接口"""
        vtt = VTTXunFei()
        vtt.login(app_id='5d9aef7b',
                  ak='f6e57d723270bd0ea2a677ffe634b4f6',
                  sk='2a2fce74da27f16cea9dcee1bab32767')
        ret = vtt.upload(audio_file_path)
        data = ret.get('data')
        import re
        pattern = re.compile(r'(?<=\'w\':\s)[\S]+(?=})')
        content = pattern.findall(str(data))
        text = ''.join(map(lambda x: x.split("'")[1], content))
        if text:
            return {'enter':'voice','state': True,'data':text,'msg':'识别成功！'}
        
        else:
            return {'enter':'voice','state': False,'data':'','msg':'语音识别失败。'}


if __name__ == '__main__' :
    
    
    
    print(Shibie().main('./1.wav'))
