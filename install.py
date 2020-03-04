#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,time,re,sys
import hashlib
import sqlite3
if int(os.popen("id -u").read()) !=0:
    print("请用root权限执行：sudo ./install.py")
    exit()

class Install():
    '''
    系统安装文件
    通过源码安装或重置系统时可以使用此工具操作，使用方法：
    sudo ./install.py
    '''

    def __init__(self):
        self.root_path = os.path.abspath(os.path.dirname(__file__))
        os.chdir(self.root_path)


    #文件夹授权执行方法  参数一 权限  参数二 位置
    def cmd(self, permission, name):
        cmds = permission + " " + os.path.join(self.root_path, name)
        os.system(cmds)

    # 富文本提示
    def print_str(self, tistr = '', status = 'n', ln = ''):
        '''
        富文本提示
            tistr   --  提示字符串
            status  --  状态码
                w --  警告（红底白字）
                n --  正常（黑底白字）
                p --  提示（绿底白字）
            ln      -- 是否换行（不为空则不换行，默认空，换行）
        '''
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


    def copy_libfile(self):
        self.print_str("拷贝必要的*.so库文件到系统目录" ,'n','n')
        os.system("sudo cp python/bin/XFawake/libs/ARM/*.so /usr/lib/")
        self.print_str('[完成]','p')

    # 111111111111111111111111111111111111111

    # 设置目录权限
    def set_path_chmod(self):
        self.print_str("设置目录下文件权限" ,'n','n')

        self.cmd("sudo chmod +x",'app/moJing')
        self.cmd('sudo chmod +x','python/bin/setWifi/*')
        self.cmd('sudo chmod +x','python/bin/XFawake/*')

        #创建所需目录
        self.cmd('sudo mkdir -p',r'python/data/conf')
        self.cmd('sudo mkdir -p',r'python/runtime/log')
        self.cmd('sudo mkdir -p',r'python/runtime/photo')
        self.cmd('sudo mkdir -p',r'python/runtime/soundCache')
        self.cmd('sudo mkdir -p',r'/music')
        self.cmd('sudo mkdir -p',r'/music/cache')

        #该目录下全部权限
        self.cmd('sudo chown -R pi.pi','python/data/')
        self.cmd('sudo chmod -R 0777', 'python/data/')

        #该目录下全部不可执行，可读可写
        self.cmd('sudo chown -R pi.pi','python/runtime/')
        self.cmd('sudo chmod -R 0777', 'python/runtime/')
        self.cmd('sudo chown -R pi.pi','/music/cache')
        self.cmd('sudo chmod -R 0777', '/music/cache')

        #该目录下全部仅执行
        self.cmd('sudo chmod +x' , 'python/run.py')
        self.cmd('sudo chmod +x' , 'python/ControlCenter.py')
        self.cmd('sudo chmod +x' , 'python/WebServer.py')

        self.print_str('[完成]','p')

    # 222222222222222222222222222222222222222222222222

    # 创建系统默认数据库
    def CreateTables(self):
        self.print_str("创建系统默认数据库" ,'n','n')

        # 创建默认表
        create_db_arr = [
            'CREATE TABLE "user_list" ("uid" integer NOT NULL PRIMARY KEY AUTOINCREMENT,"realname" TEXT,"gender" integer,"birthday" TEXT,"nickname" TEXT,"facepath" TEXT);'
        ]
        if len(create_db_arr) <= 0 :
            self.print_str("跳过",'p')
            return

        # 备份数据库
        filename = time.strftime("%Y%m%d%H%M%S", time.localtime())
        old_data = os.path.join(self.root_path, 'python/data/config.db')
        mov_data = os.path.join(self.root_path, 'python/data/config_'+ str(filename) +'.db')
        os.system('sudo mv '+ old_data +' '+ mov_data)

        conn = sqlite3.connect(old_data)
        cur = conn.cursor()

        # 创建表
        for item in create_db_arr:
            try:
                cur.execute(item)
            except sqlite3.Error as e:
                self.print_str( e, 'w')

        conn.commit()
        cur.close()
        conn.close()
        os.system("sudo chown pi.pi "+ old_data)
        os.system("sudo chmod 777 "+ old_data)
        self.print_str("[完成]",'p')

        self.print_str("设置系统配置文件config.yaml" ,'n','n')
        bak_file = os.path.join(self.root_path, 'python/configBAK.yaml')
        con_file = os.path.join(self.root_path, 'python/config.yaml')
        os.system('sudo cp -f ' + bak_file + ' ' + con_file)
        os.system('sudo chmod 0666 python/config.yaml') 
        self.print_str("[完成]",'p')

        self.print_str("初始化音量配置asound.state", 'n', 'n')
        bak_file = os.path.join(self.root_path, 'python/data/asound.stateBAK')
        con_file = os.path.join(self.root_path, 'python/data/asound.state')
        os.system('sudo cp -f '+ bak_file +' '+ con_file)
        os.system("sudo chown pi.pi "+ con_file)
        os.system("sudo chmod 777 "+ con_file)
        self.print_str("[完成]",'p')

    # 333333333333333333333333333333333333333333333333333333

    # 管理计划任务
    def add_crontab(self):
        self.print_str("设置计划任务" ,'n','n')

        crontab = '/etc/crontab'
        f = open(crontab,"r")
        fstr = f.read()
        f.close()

        run_py = 'python/run.py'

        run_file = os.path.join(self.root_path, run_py)
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
        fo.write(fstr)
        fo.close()

        self.print_str("[完成]",'p')

        #===================================
        self.print_str("设置开机启动" ,'n','n')

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

        self.print_str("[完成]",'p')


    # 444444444444444444444444444444444444444444444444444444444

    # 设置默认声卡
    def set_soundcard(self):
        self.print_str("设置默认声卡" ,'n','n')

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
            fo.write( fstr )
            fo.close()

        self.print_str("[完成]",'p')

    # 555555555555555555555555555555555555555555

    # 开始清理工作
    def vacuuming(self):
        self.print_str("开始清理工作" ,'n','n')
        os.system('rm -f '+ os.path.join(self.root_path, "python/runtime/token") +'/*')
        os.system('rm -f '+ os.path.join(self.root_path, "python/runtime/hecheng") +'/*')
        os.system('rm -f '+ os.path.join(self.root_path, "python/runtime/log") +'/*')
        os.system('rm -f '+ os.path.join(self.root_path, "python/runtime/shijue") +'/*')
        self.print_str("[完成]",'p')

    # 666666666666666666666666666666666666666

    # 校准时间的方法
    def calibration_time(self):
        #需要安装包sudo apt-get install ntpdate

        self.print_str("正在设置时间核对……",'n','n')

        # 时区判断
        if os.popen("date -R").read().count("0800") == 1:
            pass
        else:
            #修改时区到中国上海
            with open("/etc/timezone","w") as x:
                x.write('Asia/Shanghai')
        #在继续修改时间
        os.system("sudo ntpdate ntp.sjtu.edu.cn")

        self.print_str('[完成]','p')

    # 777777777777777777777777777777777777777777777

    # 重置WiFi网络
    def reset_wifi(self):
        self.print_str("正在重置WiFi网络……",'n','n')
        restr = '''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
'''
        sys_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'
        fo = open(sys_supplicant, "w")
        fo.write( restr )
        fo.close()

        self.print_str('[完成]','p')

    # 88888888888888888888888888888888888

    #清理当前install位置和深层所有的__pycache__
    def del_pycache(self, file_dir = "./"):
        self.print_str("开始清理__pycache__" ,'n')
        for root, dirs, files in os.walk(file_dir):
            for x in dirs:
                if x == "__pycache__":
                    self.print_str("正在删除-->"+root+"/"+x, 'n', 'n')
                    os.system("sudo rm -r "+root+"/"+x)
                    self.print_str('[完成]','p')

    # del_pycache(self.root_path) 999999999999999999999999999999999999

    def main(self, argv=''):
        '''
        接收命令行参数 argv
        空      --  正常安装
        update  --  升级操作
            不重置数据库
            不重置WiFi网络
        release --  发布操作
            不重启设备
        '''
        self.copy_libfile()             # 拷贝必要的*.so库文件到系统目录
        self.set_path_chmod()           # 设置目录权限

        if argv != 'update':
            self.CreateTables()         # 创建系统默认数据库
            self.reset_wifi()           # 重置WiFi网络

        self.add_crontab()              # 管理计划任务
        # self.set_soundcard()          # 设置默认声卡
        self.vacuuming()                # 开始清理工作
        self.calibration_time()         # 正在设置时间核对
        self.del_pycache(self.root_path)

        self.print_str("安装工作全部完成*_^ ",'p')

        if argv != 'release':
            self.print_str("系统将在3秒钟后重启",'w')
            time.sleep(3)
            os.system('sudo reboot')

if __name__ == "__main__":
    argv = ''
    if len(sys.argv)>1:
        argv = sys.argv[1]
    Install().main(argv)
