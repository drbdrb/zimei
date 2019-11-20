# -*- coding: utf-8 -*-
import multiprocessing as mp  # 多进程
import os
import re
import time

from package.base import Base, log
from plugin import Plugin


class Remind(Base,Plugin):

    def __init__(self, public_obj ):
        self.kill = mp.Value("h",0)  #定义全局共享内存
        self.go = mp.Value("h",0)  #定义全局共享内存
        self.ai  ='' #记录备注
        
    #计算 参数输入 举例：一分钟 返回多少秒
    def second(self,t):   
        ints = ["一","二","三","四","五","六","七","八","九","零","十","百","千","万","亿"]
        ints2= ["1","2","3","4","5","6","7","8","9","0"]        
        
        data=""

        for x in t:
            for y in ints:
                if x ==y :
                    data +=y
        
        if len(str(data))>=1:      
            data = Str_int().main(data)
        if len(str(data))<1:
            for x in t:
                for y in ints2:
                    if x ==y :
                        data +=y  
        data = int(data)
        if t.count("分钟"): 
            name = "分钟"
            datas =data * 60
        elif t.count("秒"):
            name = "秒"
            datas =data 
        elif t.count("小时"): 
            name = "小时"
            datas =data * 60 * 60
        return datas
        
    #排序  参数1举例：一个小时一分钟30秒 参数2 ：手动写入 这句话有哪些单位  
            #同时返回累积秒 和 中文时间
    def sort(self,t,lists=["小时",'分钟',"秒"]):
        key2 = 0
        data = 0
        names =''
        for x in lists:            
            key =re.search(x, t) .span()[1]
            name = t[key2:key]
            data +=self.second(name) 
            names += name
            key2=key
            
        return data,names
    #进程
    def main(self,times,kill,go):
        on1 = time.time()
        self.go.value =1 #启动1
        while 1: 
            time.sleep(1)
            if kill.value == 1: 
                go.value  = 0#关闭0
                kill.value  = 0
                return  

            if time.time()-on1 >= times:
                break
        kill.value  = 0
        go.value  = 0#关闭0     
        os.system("sudo aplay  -q "+ os.path.join(self.config['root_path'], "data/yuyin/time.wav"))
        os.system("sudo aplay  -q "+ os.path.join(self.config['root_path'], "data/yuyin/time.wav"))
 
    #解析 参数一 输入原始语句 如：一个小时一分钟30秒
            #同时返回累积秒 和 中文时间
    def analysis(self, t):
        try:

            #------------------------------------
            if t.count("小时") and t.count("分钟") and t.count("秒"):
                return self.sort(t,["小时",'分钟',"秒"])
            if t.count("小时") and t.count("分钟") :
                return self.sort(t,["小时",'分钟'])
            if t.count("小时") and t.count("秒") :
                return self.sort(t,["小时",'秒']) 
            if t.count("小时") :
                return self.sort(t,["小时"])             
            #-------------------------------------
            if  t.count("分钟") and t.count("秒"):
                return self.sort(t,['分钟',"秒"])
            if  t.count("分钟"):
                return self.sort(t,['分钟']) 
            #-------------------------------------
            if t.count("秒") :
                return self.sort(t,['秒'])   
            else:
                return False,False
        except:
            return False,False
    #开始        
    def start(self, enobj):

        self.kill.value  = 0
        try:
            if self.go.value  == 0:
                t,name =self.analysis(enobj["data"])
                if name:            
                    m = mp.Process(target =lambda : self.main(t,self.kill,self.go) )
                    m.start()
                    self.ai = enobj["data"]
 
                    return {'state':True,'data':"{0}后提醒完成".format(name),'msg':'','stop':True}
                   
                else:
                    return {'state':True,'data':"没有启动提醒功能，如：一分钟后提醒我",'msg':'','stop':True}                   
                   
            else:
                return {'state':True,'data':"{0}已经在计时，请说关闭提醒即可关闭".format(self.ai),'msg':'','stop':True}

        except:
            return {'state':True,'data':"没有启动提醒功能，如：一分钟后提醒我",'msg':'','stop':True}
            
    #停止
    def stop(self, enobj={"name":"keyword"}):
        if enobj["name"] == "keyword":
            return

        if  self.go.value == 1:
            self.kill.value = 1
            return {'state':True,'data':"提醒已经取消",'msg':'','stop':True}
        else:
            return {'state':True,'data':"没有启动提醒功能",'msg':'','stop':True}

    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
      
        
        
#字符串转数字类
class Str_int():

    no_unit = 0 #不带单位
    dict_ = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"零":0,"十":10,"百":100,"千":1000,"万":10000,"亿":100000000} #映射
    def print_(self,*text):pass
      #  print(text)

    # 设计理念 : 列表会记住所有的字典里的文字对于的数字
    # 发现单位 就获取列表最后一位数字和单位乘积
    # 在del删除之前这个列表数字  在提交新的乘积到列表

    # 执行函数  参数字符串类型数字 包括百分比  输出存数字
    def main(self,str_):
        list_ = []
        new_ints=0
        for  x in str_:
            try:
                if x == "十":
                    self.no_unit+=1
                    t = list_[-1:][0]*self.dict_["十"]
                    del list_[-1:]
                    list_.append(t)
                elif x == "百":
                    self.no_unit+=1
                    t = list_[-1:][0]*self.dict_["百"]
                    del list_[-1:]
                    list_.append(t)
                elif x == "千":
                    self.no_unit+=1
                    t = list_[-1:][0]*self.dict_["千"]
                    del list_[-1:]
                    list_.append(t)
                elif x == "万":
                    self.no_unit+=1
                    t = list_[-1:][0]*self.dict_["万"]
                    del list_[-1:]
                    list_.append(t)
                elif x == "亿":
                    self.no_unit+=1
                    t = list_[-1:][0]*self.dict_["亿"]
                    del list_[-1:]
                    list_.append(t)
                else:
                    list_.append(self.dict_[x])
            except:list_ = [] #支持百分比,所以异常就清空记录
        #  没有单位的 情况下
        if self.no_unit ==0:
            new_str = ""
            for x in list_ :
                new_str += str(x)
          
            return int(new_str)
        else:
            kexue = []#记录一下是否存在超亿的数字
            save =0
            for  x in list_:
                if x >save:
                    kexue.append(x)# 记录一下是否存在超亿的数字
                    save =0 # 记录一下是否存在超亿的数字,发现了 后重新 开始计算亿后的数

                save +=x
                self.print_(save)
            self.print_(save,kexue[1:] )

            #单独计算亿前面的数字,但是不一定存在,所以异常保护
            yi=0
            try:
                for x in list_:
                    yi+=x
                    if x == kexue[1:][0]:
                        yi-=kexue[1:][0]
                        break
            except: yi = 0
            self.print_(yi)
            if int(str(yi)+str(save)) <20:
                return int(str(yi)+str(save))+10
            return int(str(yi)+str(save))
