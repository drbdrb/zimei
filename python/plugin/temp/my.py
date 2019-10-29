from package.base import Base,log
from plugin import Plugin

class My(Plugin,Base):


    def start(self,x):
        if self.public_obj.uid.value == 0:
            return {'state':True,'data': "不知道呢" ,'msg':'',}

        info = self.data.user_info( self.public_obj.uid.value )
        name = info['nickname']
        return {'state':True,'data': "你是{0},已经记在了我的心里，忘不掉了。".format(name) ,'msg':'',}


