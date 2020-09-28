from MsgProcess import MsgProcess, MsgType


class GeneralSwith(MsgProcess):
    '''万能开关插件'''

    def switch(self, data):
        if data[0:2] == '打开':
            state = 1
        else:
            state = 0

        send_data = {'type': 'switch', 'state': state, 'pin': 2}
        self.send(MsgType=MsgType.Text, Receiver="MqttProxy", Data=send_data)

    def Text(self, message):

        print(message)
        Data = message['Data']
        if isinstance(Data, dict):
            if 'type' in dict(Data).keys():
                # 这是万能开关传过来数据
                if Data['type'] == 'switch':
                    if Data['state'] == 1:
                        msg = '灯已打开'
                        self.send(MsgType=MsgType.Text, Receiver='SpeechSynthesis', Data=msg)
                        self.send(MsgType=MsgType.Text, Receiver='Screen', Data=msg)
                    elif Data['state'] == 0:
                        msg = '灯已关闭'
                        self.send(MsgType=MsgType.Text, Receiver='SpeechSynthesis', Data=msg)
                        self.send(MsgType=MsgType.Text, Receiver='Screen', Data=msg)

                    state = {'action': 'switch', 'switch': int(Data['state']), 'statustext': msg}
                    self.send(MsgType.Text, "MqttProxy", state)
            
            elif 'initstate' in dict(Data).keys() and Data['initstate'] == 'onLoad':
                send_data = {'type': 'switch', 'pin': 2}
                self.send(MsgType=MsgType.Text, Receiver="MqttProxy", Data=send_data)
        else:
            if Data[-1:] == '灯':
                self.switch(Data)