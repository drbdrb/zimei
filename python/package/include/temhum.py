# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time

class weidushidu:
    """温度湿度"""
    channel = 18        #管脚18
    first = True        #第一次读取状态位

    #获取温湿度
    def readTemHum(self):
        #上电第一次读取需要等待1s
        if self.first==True:
            time.sleep(0.5) #停止1s
            self.first=False

        #读取次数，DHT11读的是前一次测量的结果，为了避免错误，读取俩次或以上结果
        times=0
        while True:

            #向DHT11发送读取请求
            GPIO.setmode(GPIO.BOARD) #管脚模式BCM
            GPIO.setup(self.channel, GPIO.OUT) #管脚设为输出模式
            GPIO.output(self.channel, GPIO.LOW) #输出低电位
            time.sleep(0.02) #延时20us
            GPIO.output(self.channel, GPIO.HIGH) #输出高电位
            GPIO.setup(self.channel, GPIO.IN) #输入模式

            #DHT11响应
            #80us低电平，接收到高电平结束循环
            while GPIO.input(self.channel) == GPIO.LOW:
                continue
            #80us高电平，接收到低电平结束循环
            while GPIO.input(self.channel) == GPIO.HIGH:
                continue

            #数据
            data = []
            #数据长度j
            j = 0
            while j < 40:
                k = 0
                while GPIO.input(self.channel) == GPIO.LOW:
                    continue
                while GPIO.input(self.channel) == GPIO.HIGH:
                    k += 1 #高电平，k自加1
                    if k > 100: #k超过100就退出，防止时序错误，卡死这儿
                        break
                if k < 8: #经实际测算26-28us，大概计数6-7个，data写0
                    data.append(0)
                else:     #大于8，date写1
                    data.append(1)

                j += 1 #j自加1，共读取40位

            #数据处理
            humidity = self.count(data[0:8])
            humidity_point = self.count(data[8:16])
            temperature = self.count(data[16:24])
            temperature_point = self.count(data[24:32])
            checksum = self.count(data[32:40])

            #读得数据数据的校验和
            tmp=humidity+humidity_point+temperature+temperature_point

            #读取次数增加1
            times+=1
            #数据校验和与读得数据一致，则读数正确，返回数据
            if checksum==tmp:
                if times > 1:
                    break

            #为了增加保护，不频繁读取，停顿0.5s
            time.sleep(0.5)

        #GPIO复位
        GPIO.cleanup()
        return {'temperature':temperature,'humidity':humidity}

    def count(self, data):
        res=0
        for i in range(len(data)):
            res+=data[i]*2**(7-i)
        return res

    #返回结果
    def main(self):
        res = self.readTemHum()
        temperature = res['temperature']
        humidity = res['humidity']
        #print("空气温度: "+str(temperature)+"℃  空气湿度:"+str(humidity)+"%")
        ret = {
            'temperature':str(temperature),
            'humidity': str(humidity)
        }
        return ret


if __name__ == '__main__':
    ret = weidushidu().main()
    print( ret )