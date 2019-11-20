from plugin import Plugin
import os

class Ip(Plugin):

    def start(self,x):
        data =  os.popen("hostname -I").read()
        if data:
            return {'state':True,'data': data ,'msg':'','stop':True}
        
        return {'state':True,'data': "没有网络",'msg':'','stop':True}

