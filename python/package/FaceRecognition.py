# -*- coding: utf-8 -*-
# @Date: 2020-01-14 10:02:49
# @LastEditTime: 2020-03-12 11:33:08
# @Description:  视觉类api,提供了调用摄像头拍照，人脸误别，人脸对比等基本api
'''
图形相关的api 高度抽像封装.
'''
import logging
import os
import re
import time
import cv2

from package.mylib import mylib

class FaceRecognition():
    '''人脸识别类'''

    def __init__(self):
        self.faceconfig = mylib.getConfig()['ApiConfig']['FaceRecognition']
        if self.faceconfig == 'Baidu':
            from module.ImageRecognition.faceBaidu import faceBaidu
            face = faceBaidu()
            self.IsFace = face.IsFace
            self.IsSameFace = face.IsSameFace

    def centerWindowPos(self, win_w, win_h):
        """计算出在当前屏幕分辨下，窗口宽为win_w,高win_h的窗口，居中显示初始坐标 X，Y 失败返回0,0 """
        text = os.popen('xrandr').read()
        pattren = r'(\d+)x(\d+)\+\d\+\d'
        math = re.search(pattren, text,  re.M | re.I)
        if math:
            screen_w, screen_h = int(math.group(1)), int(math.group(2))
            logging.info('screen_w = %d screen_h = %d ' % (screen_w, screen_h))
            X = (screen_w - win_w) / 2
            Y = (screen_h - win_h) / 2
            return int(X), int(Y)
        else:
            return 0, 0

    
    def IsFace(self, imgfile):
        """ 人脸识别，文件imgfile是包含人脸图片吗? 是返回True 其它返回Flase 默认分值大于80才会返回True"""
        pass


    def IsSameFace(self, img1, img2):
        """ 人脸对比 文件img1,文件img2 是同一个人吗? 是返回True 其它返回 Flase """
        pass

    def FromCaptureGetFaceImg(self, picfile, showFocus=False, timeOut=10):
        """ 打开摄像头,拍摄一张人脸照片并保存到picfile 
        timeOut超时失败退出时间。默认10秒
        参数showFocus显示聚焦框，并且只从聚焦框内取图
        仅在注册时才需要置为True
        返回值: 如果拍到人脸照片 并通过百度打分80以上则返回True 超时或失败返回False
        """
        CAMERA = mylib.getConfig()['CAMERA']
        if not CAMERA['enable']:
            logging.warning("摄像头配置为不启用")
            return False

        cap = cv2.VideoCapture(0)
        if not cap:
            logging.error('没有摄像头')
            return False

        lastTime = time.time()
        cv2.namedWindow(' ', cv2.WINDOW_AUTOSIZE)
        # cv2.namedWindow(' ', cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty(' ',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) # 全屏

        ret, frame = cap.read()
        x, y = self.centerWindowPos(frame.shape[1], frame.shape[0])
        cv2.moveWindow(' ', x, y)  # 窗口居中
        classfier = cv2.CascadeClassifier("data/opencv/haarcascade_frontalface_default.xml")
        if classfier.empty():
            logging.error('载入脸分类器失败')
            return False
        startTime = time.time()    
        while time.time() - startTime <= timeOut:
            ret, frame = cap.read()
            flip = int(CAMERA['flip'])
            if flip >= 0:
                cv2.flip(frame, flip, frame)
            bakup = frame.copy()
            if showFocus:      # 显示一个聚焦框(320,320 )，并只从框内取图
                Xstart = int((640 - 320) / 2)
                Ystart = int((480 - 320) / 2)
                Xend = Xstart + 320
                Yend = Ystart + 320
                (xsFocus, ysFocus) = (Xstart, Ystart)
                cv2.rectangle(frame, (Xstart, Ystart),
                            (Xend, Yend), (0, 255, 0), 2)
                grayImg = frame[Ystart:Yend, Xstart:Xend]
                grayImg = cv2.cvtColor(grayImg, cv2.COLOR_BGR2GRAY)
            else:
                grayImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faceRects = classfier.detectMultiScale(grayImg, scaleFactor=1.20, minNeighbors=5, minSize=(96, 96), maxSize=(256, 256))
            for faceRect in faceRects:
                x, y, w, h = faceRect
                if showFocus:
                    x += xsFocus
                    y += ysFocus
                Xstart, Ystart = (x - 30, y - 30)
                Xend, Yend = (x + w + 30, y + h + 30)
                cv2.rectangle(frame, (Xstart, Ystart),
                            (Xend, Yend), (0, 0, 255), 1)
                faceOnly = bakup[Ystart:Yend, Xstart:Xend]
                # cv2.imshow('face only', faceOnly)  #显示
                cv2.imwrite(picfile, faceOnly)
                if self.IsFace(picfile):
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
            fps = 'FPS:{}'.format(round(1 / (time.time() - lastTime)))
            lastTime = time.time()
            cv2.putText(frame, fps, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow(' ', frame)  # 显示每一帧
            key = cv2.waitKey(1)
            if key == 27:  # 按ESC键退出。
                break
        cap.release()
        cv2.destroyAllWindows()
        return False

    def WhoAmI(self):
        ''' 我是谁？ 调用摄像头拍照并从数据库中对比。
        如果存在用户，则返回用户的数据。其它返回None
        '''
        current = "runtime/photo/current.jpg"
        if self.FromCaptureGetFaceImg(current, showFocus=False, timeOut=60):
            import package.data as db
            data = db.data()
            user_list = data.user_list_get()
            if user_list and len(user_list) > 0:
                for user in user_list:
                    if user['facepath'] and os.path.exists(user['facepath']) and self.IsSameFace(user['facepath'], current):
                        return user
