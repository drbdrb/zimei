
import sys
import os
import RPi.GPIO as GPIO
rootpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rootpath)
from MsgProcess import MsgProcess, MsgType

    
class Light(MsgProcess):

    def Text(self, message):
        data = message['Data']
        
        pin_deng=11
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_deng,GPIO.OUT)
                                   
        Triggers = ['打开灯']
        if any(map(lambda w: data.__contains__(w), Triggers)):
            
             
            GPIO.output(pin_deng,GPIO.HIGH)
            self.say("灯已经打开") 
            
            
        Triggers = ['关闭灯']
        if any(map(lambda w: data.__contains__(w), Triggers)):
               
            GPIO.output(pin_deng,GPIO.LOW)
            self.say("灯已经关闭")  
            
            
        self.Stop() 

    