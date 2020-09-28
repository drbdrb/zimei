import logging
import os
import re
from package.FaceRecognition import FaceRecognition
from MsgProcess import MsgProcess, MsgType
from package.data import data as dbdata


class User(MsgProcess):
    def __init__(self, msgQueue):
        super().__init__(msgQueue)
        self.data = dbdata()
        self.visual = FaceRecognition()

    def Text(self, message):
        text = message['Data']  
        if isinstance(text, str):
            Triggers = ["用户绑定", "绑定用户", "绑定设备", "设备绑定"]
            if any(map(lambda trig: trig in text, Triggers)):
                self.user_openbind(message)
                self.Stop()
                return
            
            Triggers = ["我是谁"]
            if any(map(lambda trig: trig in text, Triggers)):
                self.say('稍等，让我看看你是谁？')
                user = self.visual.WhoAmI()
                if user and isinstance(user, dict):
                    self.say('您好：' + user['nickname'])
                else:
                    self.say('我还不知道您是谁呢。您注册绑定后我就知道你您是谁了')
                self.Stop()
                return
            
        if isinstance(text, dict) and 'action' in text.keys():
            jsonText = text
            #  显示用户绑定的二维码
            if jsonText["action"] == "USER_OPENREG":
                return self.user_openbind(jsonText)
            # 用户注册绑定
            elif jsonText["action"] == "USER_REG":
                return self.user_bind(jsonText)
            # 用户修改
            elif jsonText["action"] == "USER_EDIT":
                return self.user_edit(jsonText)
            # 用户删除
            elif jsonText["action"] == "USER_REMOVE":
                return self.user_dels(jsonText)

    def user_openbind(self, jsonText):
        '''显示用户绑定的二维码'''
        clientid = self.config['httpapi']+'/xiaocx/dev/' + self.config['MQTT']['clientid']
        nav_json = {"event": "open", "size": {"width": 380, "height": 380}, "url": "desktop/Public/bind_user.html?qr=" + clientid}
        data = {'type': 'nav', 'data': nav_json}
        self.send(MsgType.Text, Receiver='Screen', Data=data)
        text = "设备绑定功能已启动，你现在可以打开微信小程序开始绑定设备了。"
        self.say(text)

    def user_bind(self, jsonText):
        '''用户绑定'''
        jsonText = jsonText['info']
        info = self.data.user_reg(jsonText)
        logging.info('read from database %s ' % info)

        re_json = {"code": '9999', "msg": "绑定操作失败，请重新操作"}
        if info['state'] < 0:  
            re_json = {"code": '1001', "msg": info['msg']}
            logging.warning('用户信息格式错误')
        elif info['state'] == 0:  
            re_json = {"code": '2001', "msg": info['msg']}
            logging.warning('绑定新用户信息失败')
        elif info['state'] == 1:  
            re_json = {"code": '0001',"uid": info['data']['uid'], "msg": info['msg']}
            logging.warning('已经绑到此设备')
        elif info['state'] == 2:  
            logging.info('绑定新用户信息成功')
            re_json = {"code": '0000',"uid": info['data']['uid'], "msg": info['msg']}

        mqtt = {"action": "USER_REG", "info": re_json}
        self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)

        if int(info['state']) >= 1:
            uid = info['data']['uid']
            self.uid = uid
            self.user_face_bind(uid)
            mqtt = {"action": "USER_REG","msg": "恭喜您，注册绑定成功！", "info": {"code": '0003'}}
            self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)  
        else:            
            mqtt = {"action": "USER_REG", "msg": '绑定新用户信息失败', "info": {"code": '9999'}}
            self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)  

        self.Stop()

    def user_face_bind(self, uid):
        ls_str = os.popen("sudo ls -al /dev/ | grep video").read()
        if re.search("video0", ls_str) == None:
            '''未检测到摄像头'''
            data = {'type': 'nav', 'data': {"event": "close"}}
            self.send(MsgType.Text, Receiver='Screen',Data=data)  # 取消显示二维码导航消息

            re_json = {"code": '0003', "msg": '未检测到摄像头'}
            mqtt = {"action": "USER_REG", "info": re_json}
            self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)  
            return True

        if self.config['CAMERA']['enable'] == '0':
            '''系统配置为不启用摄像头'''
            data = {'type': 'nav', 'data': {"event": "close"}}
            self.send(MsgType.Text, Receiver='Screen',Data=data)  # 取消显示二维码导航消息

            re_json = {"code": '0003', "msg": '系统配置为不启用摄像头'}
            mqtt = {"action": "USER_REG", "info": re_json}
            self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)
            return True

        picfile = "runtime/photo/" + str(uid) + ".jpg"    
        if self.visual.FromCaptureGetFaceImg(picfile, showFocus=True,timeOut=120):
            self.data.user_up(uid, {'facepath':picfile})
            data = {'type': 'nav', 'data': {"event": "close"}}
            self.send(MsgType.Text, Receiver='Screen',Data=data)  # 取消显示二维码导航消息                
            return True
        self.say('没有拍摄到清晰的图像,人脸识别暂时不可用。')
        return False

# - ------------------------------------------------
    # 获取当前设备用户列表
    def user_list(self):
        u_list = self.data.user_list_get()
        mqtt = {"action": "USER_LIST", "info": u_list}
        self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)

    # 用户注销
    def user_dels(self, jsonText):
        have = self.data.user_del(jsonText["data"]["uid"])
        if have["state"]:
            re_json = {"code": '0000', "msg": "注销用户信息成功"}
        else:
            re_json = {"code": '2001', "msg": "注销用户信息失败"}

        mqtt = {"action": "USER_DEL", "info": re_json}
        self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)
        return have

     # 用户修改
    def user_edit(self, jsonText):
        '''
        * 更新用户表数据
        * uid       --  用户uid
        * updata    --  更新数据(字典)
        '''
        have = self.data.user_up(
            jsonText["data"]["uid"], jsonText["data"]["updata"])
        if have['state']:
            re_json = {"code": '0000', "msg": "用户信息修改成功"}
        else:
            re_json = {"code": '2001', "msg": "用户修改信息失败"}

        mqtt = {"action": "USER_EDIT", "info": re_json}
        self.send(MsgType.Text, Receiver='MqttProxy', Data=mqtt)  
        return have
