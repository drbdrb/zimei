import os
import re
import time
import urllib

import package.mymqtt as mymqtt
from package.base import Base  # 基本类
from plugin import Plugin
from package.include.opencv import Opencv        #人脸离线识别
import package.include.baiduapi.contrast as contrast  #人脸在线对比

class User(Base,Plugin):
    '''用户管理插件'''
    
    def __init__(self, public_obj):
        self.public_obj = public_obj
        self.Mqtt = mymqtt.Mymqtt(self.config)

    #打开绑定信息
    def user_openbind(self, postjson):
        clientid = self.config['httpapi']+'/'+ self.config['MQTT']['clientid']
        nav_json = {"event":"open","size":{"width":380,"height":380},"url":"Public/bind_user.html?qr="+ clientid }
        self.public_obj.sw.send_nav( nav_json )
        return {'state':True,'data': "设备绑定功能已启动，你现在可以打开微信小程序开始绑定设备了",'msg':'','type':'system','stop':True}


    #用户绑定操作
    def user_bind(self, postjson):
        postjson = postjson['data']
        re_json = {"code":'9999',"msg":"绑定操作失败，请重新操作"}
        if not type(postjson) is dict:
            self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )
            return

        info = self.data.user_reg( postjson )

        if info['state'] < 0:           #用户信息格式错误
            re_json = {"code":'1001',"msg":info['msg']}
        elif info['state'] == 0:        #绑定新用户信息失败
            re_json = {"code":'2001',"msg":info['msg']}
        elif info['state'] == 1:        #已经绑到此设备
            re_json = {"code":'0001',"data": info['data'], "msg":info['msg']}
        elif info['state'] == 2:        #绑定新用户信息成功
            re_json = {"code":'0000',"data": info['data'], "msg":info['msg']}

        self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )

        if int(info['state']) >= 1:
            uid = info['data']['uid']
            self.user_face_bind(uid)
            return {'state':True,'data': "恭喜您，注册绑定成功！",'msg':'','type':'system','stop':True}


    #用户人脸绑定
    def user_face_bind(self, uid ):
        ls_str = os.popen("sudo ls -al /dev/ | grep video").read()
        if re.search("video0", ls_str) == None:
            self.public_obj.sw.send_nav({"event" : "close"})                 #取消显示二维码导航消息
            re_json = {"code":'0003', "msg":'未检测到摄像头'}
            self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )
            return

        if self.config['CAMERA']['enable']=='0':
            '''系统配置为不启用摄像头'''
            self.public_obj.sw.send_nav({"event" : "close"})                 #取消显示二维码导航消息
            re_json = {"code":'0003', "msg":'系统配置为不启用摄像头'}
            self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )
            return

        #保存用户图像成功
        temp_photo = os.path.join(self.config['root_path'], "runtime/shijue/photos_"+ str(uid) +".jpg")
        ding_wav = os.path.join(self.config['root_path'], "data/snowboy/ding.wav")

        def success(is_succ):

            if is_succ and contrasts.main( temp_photo, temp_photo ) >80:
            
                opencv.close()
                
                postup = {'facepath':temp_photo}
                self.data.user_up( uid, postup )
                os.popen("sudo aplay -q "+ ding_wav )
                time.sleep(1)
                #取消显示二维码导航消息
                self.public_obj.sw.send_nav({"event" : "close"})
                re_json = {"code":'0003', "msg":'人脸图像已经保存成功'}
                self.Mqtt.send_admin('xiaocx', 'USER_REG', re_json )


        opencv = Opencv()
        opencv.success = success        
        contrasts = contrast.Contrast_face()  #人脸在线对比

        

 
        def start_video():
            fier_file  = os.path.join(self.config['root_path'], "data/shijue/haarcascade_frontalface_default.xml")
            
            fier_file = [{'file':fier_file,'scaleFactor': 1.2,'minNeighbors': 5,'minSize': (40,40)}]
            
            window    = {'name':'Facerecognition','size':(640,480),'is_focus':(300,300),'is_capture': 1}
            
            save      = {'type': 3,'color': 1}
            
            opencv.main_video(temp_file=temp_photo,fier_file =fier_file,window =window  ,save=save,camera_angle = 0,thre = 0.5  )  

        start_video()


    #用户注销
    def user_dels(self,name):

        have = self.data.user_del(name["data"]["uid"])

        if have["state"]:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'0000',"msg":"注销用户信息成功"})
            return have
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_REMOVE',{"code":'2001',"msg":"注销用户信息失败"})
            return have

     #用户修改
    def user_edit(self,name):
        '''
        * 更新用户表数据
        * uid       --  用户uid
        * updata    --  更新数据(字典)
        '''
        have = self.data.user_up(name["data"]["uid"],name["data"]["updata"])
        if have['state']:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'0000',"msg":"用户信息修改成功"})
            return have
        else:
            self.Mqtt.send_admin('xiaocx', 'USER_EDIT',{"code":'2001',"msg":"用户修改信息失败"})
            return have


    def start(self,name):
        #用户注册绑定
        if name["action"] == "USER_OPENREG":
            return self.user_openbind(name)

        #用户注册绑定
        elif name["action"] == "USER_REG":
            return self.user_bind(name)
        #用户修改
        elif name["action"] == "USER_EDIT":
            return self.user_edit(name)
        #用户删除
        elif name["action"] == "USER_REMOVE":
            return self.user_dels(name)

if __name__ == '__main__':
    pass
    #User().user_bind()
