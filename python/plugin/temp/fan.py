import RPi.GPIO as GPIO
from plugin import Plugin

class Fan(Plugin):
    channel = 15
    GPIO.setmode(GPIO.BOARD) #//设置引脚编号规则
    GPIO.setup(channel, GPIO.OUT)   # //将11号引脚设置成输出模式

    def start(self,name):
        if name["trigger"].count("打开") >=1:
            GPIO.output(self.channel, 1)   #//将引脚的状态设置为高电平，此时LED亮了            
            return {'state':True,'data': "风扇已经打开" ,'msg':'','stop':True}

        elif name["trigger"].count("关闭") >=1:
            GPIO.output(self.channel, 0)   #//将引脚状态设置为低电平，此时LED灭了
            return {'state':True,'data': "风扇已经关闭" ,'msg':'','stop':True}
        else:
            return {'state':True,'data': "风扇没有执行任何操作" ,'msg':'','stop':True}

