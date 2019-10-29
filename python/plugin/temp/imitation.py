from plugin import Plugin
class Imitation(Plugin):

    def start(self,name):

        data = name["data"][len(name["trigger"]):]
        if len(data) >= 2:return {'state':True,'data': data,'msg':'参数1，需要输入字典类型！'}
        else:return {'state':True,'data': "你想让我说什么?",'msg':'参数1，需要输入字典类型！'}




