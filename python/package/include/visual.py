import os,time
from package.base import Base,log

from package.include.opencv import Opencv         #人脸离线识别
import package.include.baiduapi.contrast as contrast  #人脸在线对比

class Visual(Base):
    """视觉类"""

    def __init__(self):
        log.info("初始化人脸对比")

        self.temp_photo = os.path.join(self.config['root_path'], "runtime/shijue/photos.jpg")

        self.is_video = False           # 是否启动人脸识别
        self.video_i = 0
        self.video_max = 10

        self.opencv = Opencv()          #人脸识别类
        self.opencv.success = self.success_max

        self.contrast = contrast.Contrast_face()  #人脸在线对比

    #开始使用百度在线人脸对比
    def start_contrast_face(self, user_info, i = 0 ):
        if i >= len(user_info) : return {}
        this_info = user_info[i]
        facepath = this_info['facepath']

        #log.info('facepath',facepath)
        #log.info('temp_photo',self.temp_photo)

        if facepath != None:
            if os.path.isfile(facepath):
                bjz = self.contrast.main( facepath, self.temp_photo )
                log.info('对比值:',this_info['uid'], bjz )
                if bjz >= 80:
                    return this_info
        i += 1
        time.sleep(0.2)
        return self.start_contrast_face(user_info, i )
        
    def success(self,data):
        print(data)
        
    #抓拍人脸成功
    def success_max(self, is_succ):

        if self.video_i >= self.video_max:
            return
        if is_succ:
            duibi_info = self.start_contrast_face( self.user_info, 0 )
            if len(duibi_info) <= 0:
                self.start_video()
            else:
                data = {
                    'enter': 'camera',
                    'type': 'system',
                    'state': True,
                    'msg': '识别成功',
                    'data': '嗨，你好！' + str(duibi_info['nickname']),
                    'body': duibi_info
                }
           
                self.success(data)

        else:
            self.start_video()

    #开始抓拍人脸
    def start_video(self):
        self.video_i += 1
        fier_file = os.path.join(self.config['root_path'], "data/shijue/haarcascade_frontalface_default.xml")
        #fier_file2 = os.path.join(self.config['root_path'], "data/shijue/haarcascade_righteye_2splits.xml")
        param = {
            'temp_file': self.temp_photo,
            'fier_file':{ 
                'file': fier_file,           
                },
         #   'show_win':{
         #      "is_show":False,
         #      "is_focus":False,
         #     },            
            }

        self.opencv.main_video( param )

    def main( self ):

        self.user_info = self.data.user_list_get()
        if self.user_info == False:
            log.info('暂无用户数据，人脸对比停止！')
            return
        if len(self.user_info) > 0:
            for x in self.user_info:
                if x['facepath'] == None:continue
                if len(x['facepath'])>0:
                    if os.path.isfile(x['facepath']):
                        self.is_video = True
            if self.is_video:self.start_video()

