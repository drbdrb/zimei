from api.BDaip import face, config
import base64

class faceBaidu():
    '''人脸对比 -- 百度接口'''
    
    def __init__(self):
        self.config = config()
        # self.CUID = hex(uuid.getnode())
    
    def IsFace(self, imgfile):
        '''图片是否为人脸'''

        with open(imgfile, 'rb') as f:
            faceimg = base64.b64encode(f.read()).decode("utf-8")

            BDFace = face.AipFace(self.config['APP_ID'], self.config['API_KEY'], self.config['SECRET_KEY'])

            result = BDFace.detect(faceimg, 'BASE64')
            if result and result['error_msg'] == 'SUCCESS':
                return result['result']['face_list'][0]['face_probability'] >= 0.8
        return False

    def IsSameFace(self, img1, img2):
        ''' 人脸对比 文件img1,文件img2 是同一个人吗? 是返回True 其它返回 Flase '''

        BDFace = face.AipFace(self.config['APP_ID'], self.config['API_KEY'], self.config['SECRET_KEY'])
        img1 = str(base64.b64encode(open(img1, 'rb').read()), 'utf-8')
        img2 = str(base64.b64encode(open(img2, 'rb').read()), 'utf-8')
        result = BDFace.match([
            {'image': img1, 'image_type': 'BASE64'},
            {'image': img2, 'image_type': 'BASE64'}])
        if result and isinstance(result, dict) and 'result' in dict(result).keys():
            return result['result']['score'] >= 80
        return False