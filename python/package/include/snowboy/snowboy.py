# -*- coding: UTF-8 -*-
import package.include.snowboy.snowboydecoder as snowboydecoder
from package.include.logbug import log    #我的类库

class Snowboy():
    """snowboy语音唤醒类"""

    def __init__(self):
        pass

    #唤醒成功回调
    def success(self):
        log.info('唤醒成功')

    def main(self, check_func, model='xiaoduxiaodu.umdl', sensit=[0.5,0.50,0.5], resource='data/snowboy/common.res'):
        self.success = check_func
        '''
        model -- 参数（模型文件）
        sensitivity -- 灵敏度
        '''
        detector = snowboydecoder.HotwordDetector(model, resource, sensitivity = sensit)
        log.info('成功启动语音唤醒,按Ctrl+Z退出')

        # main loop
        detector.start(detected_callback = check_func,
                       interrupt_check = lambda: False,
                       sleep_time=0.03)

        detector.terminate()

if __name__ == '__main__':
    Snowboy().main()

