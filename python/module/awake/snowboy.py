import os
import socket
import time
from bin.pyAlsa import pyAlsa
from api.snowboy import snowboydetect, config

class snowboy:

    def __init__(self):
        self.config = config()
        self.BindFile = '/tmp/Record.zimei'

    def awakeSuccess(self):
        pass

    def main(self):
        path = os.path.join(os.getcwd(), r'api/snowboy')

        resource = (os.path.join(path, 'common.res')).encode()
        model = (os.path.join(path, self.config['model'])).encode()
        sensitivity = self.config['sensitivity']

        detector = snowboydetect.SnowboyDetect(resource, model)
        detector.ApplyFrontend(True)
        sensitivity = (str(sensitivity) + ',') * detector.NumHotwords()
        detector.SetSensitivity(sensitivity.encode())
        stream = pyAlsa.pyAlsa()
        # logging.info('snowboy唤醒已加载,提供socket录音:%s' % self.config['snowboy']['supplyRecord'])
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        while True:
            data = stream.read()
            status = detector.RunDetection(b''.join(data))
            if self.config['supplyRecord']:
                try:
                    client.sendto(data, self.BindFile)
                except Exception:
                    pass                # 没有接收方，直接放弃
            if status == -1:
                # logging.error("Error initializing streams or reading audio data")
                return
            elif status == -2:
                # logging.debug('silence found')
                time.sleep(0.05)
                continue
            elif status == 0:
                # logging.debug('voice found')
                continue
            elif status >= 1:
                # logging.debug('Hotword Detected!')
                self.awakeSuccess()
                # self.send(MsgType=MsgType.Awake, Receiver='ControlCenter')