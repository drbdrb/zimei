import sys
import os
rootpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rootpath)
from MsgProcess import MsgProcess, MsgType

import multiprocessing as mp  # 多进程
import re
import time


class Remind(MsgProcess):

    def __init__(self, msgQueue):
        super().__init__(msgQueue)    
        self.kill = mp.Value("h",0)  #定义全局共享内存
        self.go = mp.Value("h",0)  #定义全局共享内存
        self.ai  ='' #记录备注
        
    #计算 参数输入 举例：一分钟 返回多少秒
    def second(self,t):   
        ints = ["一","二","两","三","四","五","六","七","八","九","零","十","百","千","万","亿",
            "1","2","3","4","5","6","7","8","9","0"
        ]
            
        data=""

        for x in t:
            for y in ints:
                if x ==y :
                    data +=y
        
        if len(str(data))>=1:      
            data = Str_int().main(data)
           
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
    def main(self,times,kill,go,data):
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
        
        self.say("时间到了,"+data)
        self.say("时间到了,"+data)
 
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
    def Text(self, message):   
        data = message['Data']
        
  
        if data[:2]=="提醒":
        
            self.kill.value  = 0
            try:
                if self.go.value  == 0:
                    t,name =self.analysis(data)
                    if name:            
                        m = mp.Process(target =lambda : self.main(t,self.kill,self.go,data) )
                        m.start()
                        self.ai = data
     
                        self.say("{0}，设置完成,总计{1}秒".format(data,t))
                       
                    else:
                        self.say("没有启动提醒功能，如：一分钟后提醒我") 
                        self.Stop()  # 报完IP即退出。
                       
                else:
                    self.say("{0}已经在计时，请说关闭提醒即可关闭".format(self.ai))

            except:
                self.say("没有启动提醒功能，如：一分钟后提醒我")
                self.Stop()  # 报完IP即退出。
            
            
    
        Triggers = ["取消提醒","关闭提醒"]

        if any(map(lambda w: data.__contains__(w), Triggers)):     
       
            if  self.go.value == 1:
                self.kill.value = 1
                self.say("提醒已经取消")
                self.Stop()  # 报完IP即退出。
            else:
                self.say("没有启动提醒功能")
                self.Stop()  # 报完IP即退出。
            
            
         

   

        
#字符串转数字类
class Str_int():

    no_unit = 0 
    dict_ = {"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,
                "八":8,"九":9,"零":0,"十":10,"百":100,"千":1000,
                "1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"0":0
                }

    def main(self,str_):
    
        try:
            list_ = []

            for  x in str_:
      
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

                else:
                    list_.append(self.dict_[x])
               
           
            if self.no_unit ==0: 
                return int("".join([str(x) for x in list_]))
                           
            else: 
                return sum(list_)
        except:
            return 0
