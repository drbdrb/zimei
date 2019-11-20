from plugin import Plugin
import os,time
import pyzbar.pyzbar as pyzbar
from PIL import Image as Image2
from tkinter import *
import multiprocessing as mp  # 多进程



class Code_recognition(Plugin):
    def __init__( self, public_obj ):
      
        self.public_obj = public_obj
    def pinmuxy(self,root):#窗口居中
     
        sw = root.winfo_screenwidth()#得到屏幕宽度x
        sh = root.winfo_screenheight()#得到屏幕高度y
        ww = root.winfo_width()#307#窗口宽x
        wh = root.winfo_height()#140#窗口高y
        x = (sw-ww)/2
        y = (sh-wh)/2        
        
        root.geometry("%dx%d+%d+%d" % (ww,wh,x,y))

    def xx(self,root):
          
        for x in range(100):
            time.sleep(0.1)
            root.update()


    def start(self,x):
              
  
        root=Tk()
        root.protocol("WM_DELETE_WINDOW",lambda:None)
        root.resizable(width=False, height=False)#关闭拉伸
        root.title('二维码扫描')
        
        

        txts=Text(root,font=("宋体", 30, "bold"),width=28, height=8)
        txts.grid() 
        root.update()
        self.pinmuxy(root)        
        txts.insert(INSERT,'正在扫描...')   
     
   

                
                
        kill =0
        while 1:
            root.update()
            kill  +=1
            os.system("raspistill -o /2.png -w 400 -h 300 -rot 180   -t 1000 -n")
    
            img = Image2.open("/2.png")
            img.show()
            barcodes = pyzbar.decode(img)
            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8") 
                
                txts.delete('0.0', END)               
                txts.insert(INSERT,barcodeData)  
                root.update()
                               
                self.p1 = mp.Process(target = lambda : self.xx(root))  
                self.p1.start()    
                
                return {'state':True,'data': "二维码内容:"+barcodeData ,'msg':'','stop':True}   

          
            if kill >10:              
                return {'state':True,'data': "识别结束" ,'msg':'','stop':True}     
                
            root.update()
            
            
            
            
            
            
            
            
            
            
            
            
            
            