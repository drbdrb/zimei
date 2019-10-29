from package.include.model import model
from package.base import Base,log
import re,os,string

class Lstm(Base):
    '''数据库自然语言处理'''
    
    def __init__(self):

        self.db   = model(os.path.join(self.config['root_path'],"data/lstm.db"))

        self.trigger = self.db.table( "dz_trigger" ).where({'status':1}).sel()          #获取触发词
        self.option  = self.db.table( "dz_option" ).where().sel()           #获取具体操作表数据
        self.action  = self.db.table( "dz_action" ).where().sel()           #获取动作词


    #获取数据表数据
    def get_basedata(self, tabname = ""):
        all_ = self.db.table( tabname ).where().sel()
        return all_

    #匹配动作词
    def match_action(self, action_str = ""):
        for item in self.action:
            name = item['name'].strip()
            matchObj = re.search( name, action_str, re.M|re.I)
            if matchObj:
                if len(matchObj.group()) > 0:
                    return item['cmd'].strip()
        return False


    #匹配指令方法
    def match_option(self, trigger_dict={} ):
        for item in self.option:
            if item['name'].strip() == trigger_dict['name'].strip():
                item['trigger'] = trigger_dict['trigger']
                item['level'] = trigger_dict['level']
                if trigger_dict['action']:
                    item['action'] = trigger_dict['action']
                else:
                    find_cmd = self.match_action( trigger_dict['trigger'] )
                    if find_cmd:
                        item['action'] = find_cmd
                    else:
                        item['action'] = ''

                return item
        return False


    #在用户指令中查找触发词
    def find_trigger(self, entxt ):

        #去首尾中文、英文标点
        cn_str = r"[。|！|；|，]"
        en_str = r"[\.|\!|\;|\,]"

        entxt = re.sub( r"^" + cn_str, "", entxt, re.M|re.I)
        entxt = re.sub( cn_str + "$", "", entxt, re.M|re.I)
        entxt = re.sub( en_str + "$", "", entxt, re.M|re.I)

        all_trigger = []
        for item in self.trigger:
            key = re.sub( r"^\|","^", item['key'], re.M|re.I)
            key = re.sub( r"\|$","$", key, re.M|re.I)
            key = re.sub( r"{\d}","(.*)", key, re.M|re.I)

            matchObj = re.search( key, entxt, re.M|re.I)
            if matchObj:
                if len(matchObj.group()) > 0:
                    item_se = {
                        'trigger': matchObj.group(),
                        'level': len(matchObj.group()),
                        'name': item['name'],
                        'action': item['action']
                    }
                    all_trigger.append(item_se)

        ret_arr = {'trigger':'','level':0,'name':''}
        for x in all_trigger:
            if x['level'] > ret_arr['level']:
                ret_arr = x

        if ret_arr['level']>0:
            return ret_arr
        else:
            return False

    '''
    启动方法
    参数:
        enjson :    --  json格式的语句体
        {
            'optype': 'action'              -- 操作类型（action动作 / snowboy唤醒）
            'enter': 'voice',               -- 入口（voice-语音、camera-摄像头、mqtt）
            'type': 'system',               -- 控制类型（系统类型-合成语音会被缓存）
            'state': False,                 -- 操作状态
            'msg': '识别失败！',            -- 操作状态中文提示
            'data': '我没听清你说了啥',     -- 返回文本（屏幕提示）
        }
    返回：
        {
            "state": 布尔类型 ,
            "data":原始字符串,
            "trigger":"数据库返回的触发词",
            "action":动作指令,
            "ptype":插件类别,
            "name":插件名
        }
    '''
    def main( self, enjson ):
        entext = enjson['data']
        dict_none =  {"state": False ,"data": '',"trigger":"","action":'',"ptype":'',"name":''}

        trigger_cmd = self.find_trigger( entext )

        have_cmd = False
        if trigger_cmd:
            if trigger_cmd['name'] == 'keyword':
                #如果是系统保留关键字，作特殊处理
                have_cmd = trigger_cmd
                have_cmd['ptype'] = 'keyword'
            else:
                have_cmd = self.match_option( trigger_cmd )

        if have_cmd:
            if re.search(r'不' + have_cmd['trigger'], entext, re.M|re.I):
                return dict_none

            #一路通过结果
            return {
                "state": True,
                "data": entext,
                "trigger": have_cmd['trigger'],
                "action": have_cmd["action"],
                "ptype": have_cmd["ptype"],
                "name": have_cmd["name"]
            }
        else:
            return dict_none

