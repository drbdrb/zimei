# -*- coding: utf-8 -*-
from plugin import Plugin
import os
import time
import re
import multiprocessing as mp 
from package.base import Base, log

class File_management(Base,Plugin):

    def __init__(self, public_obj ):  
        
        self.start()
        log.info("空间管理已启动")
                        
    #path:文件具体位置condition：数量伐值number：达到伐值删除多少
    def musicdel(self,path,condition,number):
        try:
            if len(os.listdir(path)) <condition:
                return
            datatime=[]
            for x in os.listdir(path):
                #记录所有歌曲的最后访问时间
                datatime.append(os.stat(path+x)[-3])
            #列表有小到大排列,和去重
            datatime.sort()
            deldata = list(set(datatime[:number]))
            '''
            for x in deldata:
                print("时间为：",time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(x)))

            print("符合删除",deldata)
            '''
            ints = 0
            #循环所有歌曲
            for x in os.listdir(path):
                #循环删除符合要求的
                for y in deldata:
                    #在所有歌曲中寻找=符合删除要求的歌曲
                    try:
                        if y == os.stat(path+x)[-3]:
                            ints +=1
                            #删除10首结束
                            if ints > number:
                                break
                            os.system("sudo rm -r {0}{1}".format(path,x))
                           # print(" 正在删除：{0}{1}".format(path,x))
                    #这个是为了防止已经删除的文件，还在内存列表里还是循环继续删除，导致错误
                    except:pass

        except Exception as bug :
            pass
            #print("删除"*10,bug)
            
    def main(self):
        while 1:
            #获取磁盘使用了百分之多少
            disk = int( re.compile(r'\d+\.?\d*').findall(os.popen("df -h").read())[3] )
            if  disk >=80:
            
                self.musicdel(  os.path.join(self.config['root_path'], 'runtime/hecheng/')  ,50,40)               
                self.musicdel("/music/cache/",100,50)                                 
                #print("空间使用了百分之",disk)
            time.sleep(600)
            
            
    def start(self):
        t = mp.Process(target = self.main )
        t.start()   
       
if __name__ == "__main__":
    File_management().start()    
        
        
        
        
        
        
        
        
        
        
        
        