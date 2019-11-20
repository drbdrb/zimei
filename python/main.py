#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import re
import package.master as master  # 主控制

# 设置默认声卡
def set_soundcard():
    cardtext = os.popen("aplay -l").read()
    restr = r'card\s(\d)\:\swm8960soundcard'
    matc = re.search( restr, cardtext, re.M|re.I )
    cardnum = 0
    if matc!=None:
        cardnum = matc.group(1)
    else:
        return

    alsa_conf = '/usr/share/alsa/alsa.conf'
    f = open(alsa_conf,"r")
    fstr = f.read()
    f.close()

    is_write = False
    restr = r'^defaults.ctl.card\s+\d\s*$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        fstr = re.sub(restr, "defaults.ctl.card "+ str(cardnum), fstr, 1, re.M|re.I )
        is_write = True

    restr = r'^defaults.pcm.card\s+\d\s*$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        fstr = re.sub(restr, "defaults.pcm.card "+ str(cardnum), fstr, 1, re.M|re.I )
        is_write = True

    if is_write:
        fo = open(alsa_conf, "w")
        line = fo.write( fstr )
        fo.close()
    del cardtext,restr,matc,cardnum,alsa_conf,fstr,is_write,line

if __name__ == '__main__':
    #设置默认声卡
    set_soundcard()

    #启动：主控制
    master.Master().main()
