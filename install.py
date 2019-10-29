#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,time,re,sys
import hashlib
import sqlite3
if int(os.popen("id -u").read()) !=0:
    print("请用root权限执行：sudo ./install.py")
    exit()

'''
接收命令行参数
空      --  正常安装
update  --  升级操作
    不重置数据库
    不重置WiFi网络
release --  发布操作
    不重启设备
'''
argv = ""
if len(sys.argv)>1:
    argv = sys.argv[1]

root_path = os.path.abspath(os.path.dirname(__file__))

#文件夹授权执行方法  参数一 权限  参数二 位置
def cmd(permission , name):
    cmds = permission + " " + os.path.join(root_path, name)
    os.system(cmds)

'''
富文本提示
    tistr   --  提示字符串
    status  --  状态码
        w --  警告（红底白字）
        n --  正常（黑底白字）
        p --  提示（绿底白字）
    ln      -- 是否换行（不为空则不换行，默认空，换行）
'''
def print_str( tistr = '', status = 'n', ln = ''):
    ti_str = tistr
    if status=='w':
        ti_str = '\033[41m{0}\033[0m'.format(ti_str)
    elif status=='p':
        ti_str = '\033[42m{0}\033[0m'.format(ti_str)
    if len(ln)>0:
        print(ti_str, end='')
    else:
        print(ti_str)
    sys.stdout.flush()


def md5_file(path):
    if not os.path.isfile(path):
        return None
    try:
        hash = hashlib.md5()
        f = open(path, "rb")
        while True:
            b = f.read(1024)
            if not b:
                break
            hash.update(b)
        f.close()
        return hash.hexdigest()
    except:
        return None

'''
比较文件差异
return：
    True    --  相同
    False   --  不同
'''
def diff_file(file1, file2):
    hash1 = md5_file(file1)
    hash2 = md5_file(file2)

    if hash1 is None:
        if hash2 is None:
            return True
        else:
            return False
    else:
        if hash2 is None:
            return False
    if hash1 == hash2:
        return True
    else:
        return False
#--------------------------------------------

#设置目录权限
def set_path_chmod():
    print_str("设置目录下文件权限" ,'n','n')

    cmd("sudo chmod +x", 'app/moJing')
    cmd('sudo chmod +x' , 'python/bin/*')

    #创建所需目录
    cmd('sudo mkdir -p','python/data/conf')
    cmd('sudo mkdir -p','python/runtime/log')
    cmd('sudo mkdir -p','python/runtime/hecheng')
    cmd('sudo mkdir -p','python/runtime/shijue')
    cmd('sudo mkdir -p','python/runtime/token')

    #该目录下全部权限
    cmd('sudo chown -R pi.pi','python/data/')
    cmd('sudo chmod -R 0777', 'python/data/')

    #该目录下全部不可执行，可读可写
    cmd('sudo chown -R pi.pi','python/runtime/')
    cmd('sudo chmod -R 0777', 'python/runtime/')

    #该目录下全部仅执行
    cmd('sudo chmod +x' , 'python/api.py')
    cmd('sudo chmod +x' , 'python/run.py')
    cmd('sudo chmod +x' , 'python/main.py')

    print_str('[完成]','p')


set_path_chmod()

'''
---------------------------------------------------------
* 以下是创建数据库内容，下面注释信息为定界符，不能修改！
---------------------------------------------------------
'''
# 创建新表
def CreateTables( db_arr = [] ):
    print_str("创建系统默认数据库" ,'n','n')
    if len(db_arr) <= 0 :
        print_str("跳过",'p')
        return

    filename = time.strftime("%Y%m%d%H%M%S", time.localtime())
    old_data = os.path.join(root_path, 'python/data/config.db')
    mov_data = os.path.join(root_path, 'python/data/config_'+ str(filename) +'.db')
    os.system( 'sudo mv '+ old_data +' '+ mov_data )

    conn = sqlite3.connect(old_data)
    cur = conn.cursor()

    for item in db_arr:
        try:
            cur.execute(item)
        except sqlite3.Error as e:
            print_str( e, 'w')

    conn.commit()
    conn.close()
    os.system("sudo chmod 777 "+ old_data)

    print_str("[完成]",'p')


create_table = []

#=[CreatedatabaseStart]=
create_table=['CREATE TABLE "config" ("key" TEXT(20),"value" TEXT(20),"nona" TEXT(200));', 'CREATE TABLE "nmap_config" ("key" TEXT(20),"value" TEXT(20),"nona" TEXT(200));', 'CREATE TABLE "nmap_mon" ("mac" TEXT(20) NOT NULL PRIMARY KEY,"ip" TEXT(15),"notename" TEXT(30),"up_time" TEXT(11),"is_online" INTEGER);', 'CREATE TABLE "nmap_mon_list" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"mac" TEXT(20),"up_time" TEXT(20),"jiange" INTEGER);', 'CREATE TABLE "nmap_online" ("mac" TEXT(20) NOT NULL PRIMARY KEY,"ip" TEXT(15),"name" TEXT(50),"notename" TEXT(50),"up_time" TEXT(11),"is_online" INTEGER);', 'CREATE TABLE "user_list" ("uid" integer NOT NULL PRIMARY KEY AUTOINCREMENT,"realname" TEXT,"gender" integer,"birthday" TEXT,"nickname" TEXT,"facepath" TEXT);']
#=[CreatedatabaseEnd]=

if len(create_table) > 0 and argv != 'update':
    CreateTables(create_table)


'''
------------------------------------------------------
* 管理计划任务
------------------------------------------------------
'''
def add_crontab():
    print_str("设置计划任务" ,'n','n')

    crontab = '/etc/crontab'
    f = open(crontab,"r")
    fstr = f.read()
    f.close()

    run_py = 'python/run.py'

    run_file = os.path.join(root_path, run_py)
    run_cmd = '*/5 * * * * pi export DISPLAY=:0 && '+ run_file  + " &" #必须加 & 不然计划任务失效     #每隔5分钟检测一次

    time_file = 'ntpdate ntp.sjtu.edu.cn'
    #每隔1小时检测一次
    times_cmd = "0 */1 * * * root "+ time_file + " &"

    r_runfile = r'^\*.+pi export DISPLAY=:0 &&.+\&$'
    matc = re.search( r_runfile, fstr, re.M|re.I )
    if matc==None:
        fstr = "\n" + run_cmd
    else:
        fstr = re.sub(r_runfile, run_cmd, fstr, flags=re.M|re.I )

    time_matc = re.search( time_file , fstr, re.M|re.I )
    if time_matc==None:
        fstr += "\n" + times_cmd

    fo = open(crontab, "w+")
    line = fo.write(fstr)
    fo.close()

    print_str("[完成]",'p')

    #===================================
    print_str("设置开机启动" ,'n','n')

    autostart = '/etc/xdg/autostart'
    if os.path.exists(autostart) is False:
        #print('目录不存在')
        os.system('mkdir -p '+ autostart )

    start_mojing = os.path.join( autostart,'Start_Mojing.desktop')

    mojing_str  = '[Desktop Entry]\n'
    mojing_str += 'Type="Application"\n'
    mojing_str += 'Exec="'+ run_file +'"'

    with open(start_mojing, 'w') as fso:
        fso.write(mojing_str)

    print_str("[完成]",'p')


add_crontab()

'''
------------------------------------------------------
# 设置默认声卡
------------------------------------------------------
'''
def set_soundcard():
    print_str("设置默认声卡" ,'n','n')

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

    print_str("[完成]",'p')

set_soundcard()

'''
------------------------------------------------------
# 设置摄像头
------------------------------------------------------
'''
def set_camera():
    print_str("设置摄像头" ,'n','n')

    config = '/boot/config.txt'
    f = open(config,"r")
    fstr = f.read()
    f.close()

    is_write = False
    restr = r'^start_x=1$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fstr += "\nstart_x=1"
        is_write = True

    restr = r'^gpu_mem=128$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fstr += "\ngpu_mem=128"
        is_write = True

    if is_write:
        fo = open(config, "w")
        line = fo.write( fstr )
        fo.close()


    fstr = ""
    #-----------------------------------
    conf = '/etc/modules-load.d/modules.conf'
    f = open(conf,"r")
    fstr = f.read()
    f.close()

    restr = r'^bcm2835-v4l2$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fo = open(conf, "a+")
        fo.seek(0, 2)
        line = fo.write('bcm2835-v4l2')
        fo.close()

    print_str("[完成]",'p')

set_camera()


'''
----------------清空处理-------------------
 new字典格式要求
 key=该文件绝对路径
 vealue=[文件名和后缀]列表内可以是多个文件名
-------------------------------------------
'''
def vacuuming():
    print_str("开始清理工作" ,'n','n')
    os.system('rm -f '+ os.path.join(root_path, "python/runtime/token") +'/*')
    os.system('rm -f '+ os.path.join(root_path, "python/runtime/hecheng") +'/*')
    os.system('rm -f '+ os.path.join(root_path, "python/runtime/log") +'/*')
    os.system('rm -f '+ os.path.join(root_path, "python/runtime/shijue") +'/*')
    print_str("[完成]",'p')

vacuuming()

'''
----------------关闭电脑屏保-------------------
#禁止屏保方法
-------------------------------------------
'''
def ban_screen_savers():
    print_str("禁止屏幕保护事件" ,'n','n')
    with open("/etc/profile.d/Screen.sh","w") as x :
        x.write("xset dpms 0 0 0\nxset s off")
    print_str("完成",'p')

ban_screen_savers()
'''
----------------校准时间-------------------
#校准时间的方法
-------------------------------------------
'''
def calibration_time():
    #需要安装包sudo apt-get install ntpdate

    print_str("正在设置时间核对……",'n','n')

    # 时区判断
    if os.popen("date -R").read().count("0800") == 1:
        pass
    else:
        #修改时区到中国上海
        with open("/etc/timezone","w") as x:
            x.write('Asia/Shanghai')
     #在继续修改时间
    os.system("sudo ntpdate ntp.sjtu.edu.cn")

    print_str('[完成]','p')

calibration_time()
'''
----------------链接前后端-------------------
#链接前后端的方法
-------------------------------------------
'''
def set_js():
    print_str("设置显示端基本配置",'n','n')

    conf_path = os.path.join( root_path,"app/resources/app/config.js")

    f = open(conf_path,"r")
    fstr = f.read()
    f.close()

    restr = r'\/*const\s+rootpath\s*=\s*[\'|\"]\/.+[\'|\"]\;?'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        root_path2 = root_path
        if root_path2[-1:] != "/": root_path2 = root_path2 + "/"
        new_api = "const rootpath = '" +root_path2+ "';"
        fstr = re.sub(restr, new_api, fstr, 1, re.M|re.I )

        #删除本地配置
        redel = r'\/*const\s+rootpath\s*=\s*[\'|\"]python.+[\'|\"]\;?.*\n'
        fstr = re.sub(redel, '', fstr, 1, re.M|re.I )

        fo = open(conf_path, "w")
        line = fo.write( fstr )
        fo.close()

    print_str('[完成]','p')
set_js()

#重置WiFi网络
def reset_wifi():
    print_str("正在重置WiFi网络……",'n','n')
    restr = '''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
'''
    sys_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf';
    fo = open(sys_supplicant, "w")
    line = fo.write( restr )
    fo.close()

    print_str('[完成]','p')

if argv != 'update':reset_wifi()

'''
----------清理所有__pycache__-------------
'''
#清理当前install位置和深层所有的__pycache__
def del_pycache(file_dir = "./"):
    print_str("开始清理__pycache__" ,'n')
    for root, dirs, files in os.walk(file_dir):
        for x in dirs:
            if x == "__pycache__":
                print_str("正在删除-->"+root+"/"+x, 'n', 'n')
                os.system("sudo rm -r "+root+"/"+x)
                print_str('[完成]','p')

del_pycache(root_path)

print_str("安装工作全部完成*_^ ",'p')

if argv != 'release':
    print_str("系统将在3秒钟后重启",'w')
    time.sleep(3)
    os.system('sudo reboot')
