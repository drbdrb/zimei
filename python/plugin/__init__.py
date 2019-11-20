class Plugin():
    '''插件基本类，所有插件入口类都需要继承此类'''
    
    def __init__( self, public_obj ):
        self.public_obj = public_obj

    #插件开始
    def start(self, sbobj={}):
        #print('执行了 插件默认开始start 方法---------')
        pass

    #插件等待（暂时停止）
    def pause(self, *enobj):
        #print('执行了 插件默认暂停pause 方法---------')
        pass

    #插件继续
    def resume(self, sbobj={}):
        #print('执行了 插件默认继续resume 方法---------')
        pass

    #插件结束
    def stop(self, *enobj):
        #print('执行了 插件默认停止stop 方法---------')
        return False

    def __del__(self):
        self.stop()
        #print('执行了 插件默认结束__del__ 方法---------')