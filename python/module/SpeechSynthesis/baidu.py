from api.BDaip import AipSpeech, config

class baidu():
    '''
    百合语音合成模块
    '''

    def __init__(self, CUID):
        self.config = config()
        self.CUID = CUID
    
    def main(self, text, fileName):
        APP_ID =  self.config['APP_ID']
        API_KEY =  self.config['API_KEY']
        SECRET_KEY =  self.config['SECRET_KEY']
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

        # 发音人选择, 基础音库：0 - 度小美，1 - 度小宇，3 - 度逍遥，4 - 度丫丫，
        # 精品音库：5 - 度小娇，103 - 度米朵，106 - 度博文，110 - 度小童，111- 度小萌，默认为度小美
        # PER = 4
        # 语速，取值0-15，默认为5中语速     SPD = 5
        # 音调，取值0-15，默认为5中语调     PIT = 5
        # 音量，取值0-9，默认为5中音量      VOL = 5
        # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
        # AUE = 6
        #
        try:
            auido = client.synthesis(text=text, options={'vol': 5, 'per': 4, 'aue': '3', 'cuid': self.CUID})
        except Exception as e:
            # logging.error('语音合成失败,%s' % e)
            return False

        with open(fileName, 'wb') as f:
            f.write(auido)
        # self.playSound(fileName)
        return fileName