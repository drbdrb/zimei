import logging

logging.basicConfig(level = logging.INFO,format = '%(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

class log():
    '''
    调试打印日志
    *a代表该函数方法无论传入多少值，都打包成元祖
    在使用列表堆到式遍历元祖的值，把所以值转换为字符串类型，在打包为新的列表
    在使用"".join把列表转换为一句字符串
    '''

    @classmethod
    def info(self,*a):
        return
        #logger.info(' '.join([str(i) for i in a]))

    @classmethod
    def debug(self,*a):
        logger.debug(' '.join([str(i) for i in a]))

    @classmethod
    def warning(self,*a):
        logger.warning(' '.join([str(i) for i in a]))