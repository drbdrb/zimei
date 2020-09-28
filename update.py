#!/usr/bin/python3
import os,time,re,sys,json
import threading
import requests

if int(os.popen("id -u").read()) !=0:
    print("请用root权限执行：sudo ./update.py")
    exit()

exitFlag = 0
is_print = 0
class myThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def print_time(self,threadName):
        global exitFlag, is_print
        while True:
            if exitFlag:
                exit()
            if is_print:
                sys.stdout.write('■')
                sys.stdout.flush()
            time.sleep(0.5)

    def run(self):
        self.print_time(self.name)

class update():

    def __init__(self):
        #运行自美系统的根目录
        self.SYSTEM_ROOT = '/'

        #系统目录
        self.SYSTEM_DIR = os.path.join(self.SYSTEM_ROOT, 'keyicx')

        #升级目录
        self.UPDATE_DIR = '/tmp/zmupdate'

        #升级进度文件
        self.UPDATE_FILE = '/tmp/zmprogress'

        #升级库URL
        self.GITEE_URL = 'https://gitee.com/kxdev/zimeimojing'

        #进度条
        self.th_ress = myThread(1,"Thprog")
        self.th_ress.start()

    def progress(self, is_show):
        global is_print
        if self.th_ress.isAlive() is False:
            self.th_ress.start()
        if is_show:
            print("\033[?25l")
            is_print = 1
        else:
            print("\033[?25h")
            is_print = 0

    
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
            sys.stdout.write(ti_str)
        else:
            sys.stdout.write(ti_str+'\n')
        # sys.stdout.flush()

    def menu(self):
        global exitFlag
        tishi  = "━━━━━━☆ ★ ☆ 欢迎使用自美系统在线升级工具 V2.0 ☆ ★ ☆━━━━━━\n"
        tishi += " 1、查看官方最新版本号\n"
        tishi += " 2、查看本地版本号\n"
        tishi += " 3、一键检测并升级系统\n"
        tishi += " 4、退出\n"
        tishi += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        tishi += "直接输入操作命令前面的数字序号（回车）:"

        os.system('clear')
        a = input(tishi)
        if a == "1":
            self.menu_ckver('git')
            time.sleep(5)
            return self.menu()
        elif a == "2":
            self.menu_ckver('local')
            time.sleep(5)
            return self.menu()
        elif a == "3":
            self.menu_startup()
            return self.menu()
        elif a == "4":
            exitFlag = 1
            self.th_ress.join()
            exit()
        else:
            return self.menu()

    #比较版本号
    def versionCompare(self, v1="1.1.1", v2="1.2"):
        v1 = re.sub(r'^\D', "", v1)
        v2 = re.sub(r'^\D', "", v2)
        v1_check = re.match("\d+(\.\d+){0,2}", v1)
        v2_check = re.match("\d+(\.\d+){0,2}", v2)
        if v1_check is None or v2_check is None or v1_check.group() != v1 or v2_check.group() != v2:
            return -2   #"版本号格式不对，正确的应该是x.x.x,只能有3段"
        v1_list = v1.split(".")
        v2_list = v2.split(".")
        v1_len = len(v1_list)
        v2_len = len(v2_list)
        if v1_len > v2_len:
            for i in range(v1_len - v2_len):
                v2_list.append("0")
        elif v2_len > v1_len:
            for i in range(v2_len - v1_len):
                v1_list.append("0")
        else:
            pass
        for i in range(len(v1_list)):
            if int(v1_list[i]) > int(v2_list[i]):
                return -1
            if int(v1_list[i]) < int(v2_list[i]):
                return 1
        return 0

    #运行git命令
    def run_gitcmd(self, cmd, osrun='popen'):
        cmd = 'cd '+ self.UPDATE_DIR +'\n'+cmd
        if osrun == 'system':
            cmd += ' > /dev/null 2>&1'
            os.system( cmd )
        else:
            out = os.popen(cmd).read()
            return out

    #获取Git最新的版本
    def get_new_ver(self):
        url = self.GITEE_URL + '/raw/master/python/data/ver.txt'
        git_newver = ''
        try:
            response = requests.get(url, timeout=60)
            if int(response.status_code) == 200:
                git_newver = response.text
        except:
            pass
        return git_newver.strip()

    #获取本地版本号
    def get_local_ver(self):
        this_verfile = os.path.join(self.SYSTEM_DIR, 'python/data/ver.txt')
        file_ver = ""
        if os.path.exists(this_verfile):
            fo = open(this_verfile, "r+")
            file_ver = fo.read(-1)
            fo.close()

        return file_ver.strip()

    #下载新的文件
    def down_newfile(self):
        self.print_str('正在获取远程系统文件……','n','n')
        self.reset_progress()
        self.progress(1)
        git_cmd = ''
        if os.path.exists( os.path.join( self.UPDATE_DIR, '.git') ):
            git_cmd = 'git pull'        #拉取
            self.run_gitcmd( git_cmd, 'system' )
            time.sleep(1)
        else:
            git_cmd = 'git clone --recursive '+ self.GITEE_URL +'.git '+ self.UPDATE_DIR
            cmd = git_cmd +' > /dev/null 2>&1'
            os.system( cmd )
            time.sleep(1)

        self.print_str('[完成]','p')
        self.progress(0)


    #迁移目录
    def move_dir(self):
        if os.path.exists(self.UPDATE_DIR):
            datetime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            back_path = self.SYSTEM_DIR +'_'+str(datetime)

            self.print_str('正在备份原系统，请稍候……','n')
            self.progress(1)

            if os.path.isdir(self.SYSTEM_DIR):
                cmd = 'sudo mv '+ self.SYSTEM_DIR +' '+ back_path
                os.system( cmd )
                self.progress(0)
            else:
                os.system('sudo mkdir '+ self.SYSTEM_DIR)

            self.print_str('开始部署新系统，请稍候……（这里可能需要几分钟时间）','n')
            self.progress(1)
            time.sleep(1)

            cmd = 'sudo rsync -aq --exclude=.git '+ self.UPDATE_DIR +'/ '+ self.SYSTEM_DIR +'/'
            os.system( cmd )

            self.print_str('[完成]','p')
            self.progress(0)

            return True
        else:
            return False

    '''
    比较版本
    返回：
        True    --    需要更新
        False   --    不需要
    '''
    def diff_ver(self):
        git_newver = self.get_new_ver()      #获取最新的发行版本

        file_ver = self.get_local_ver()      #获取本地版本号

        if file_ver:
            self.print_str('当前系统版本号-->'+ file_ver)
            self.print_str('官方最新版本号-->'+ git_newver)

            diffver = self.versionCompare( file_ver, git_newver )
            if diffver > 0:
                self.print_str('官方最新版本高于当前版本，需要升级！','w')
                return True
            else:
                self.print_str('当前系统版本已经是最新版本，无需升级！','p')
                return False
        else:
            self.print_str('当前系统版本文件丢失，需更新升级！','w')
            #没有版本文件，默认即将更新的版本大于当前版本
            return True

    #查看版本号
    def menu_ckver(self, ty = 'git'):
        if ty=='git':
            git_newver = self.get_new_ver()      #获取最新的发行版本
            self.set_progress({'remotever': git_newver})
            self.print_str('官方最新版本号-->'+ git_newver,'w')
        if ty=='local':
            file_ver = self.get_local_ver()      #获取本地版本号
            self.set_progress({'localver': file_ver})
            self.print_str('当前系统版本号-->'+ file_ver,'p')

    #开始升级
    def menu_startup(self):
        self.down_newfile()
        self.set_progress({'progress': 30})
        is_up = self.diff_ver()
        if is_up is True:
            opis = self.move_dir()
            self.set_progress({'progress': 70})
            if opis:
                self.print_str('新版本文件环境部署完成！','p')
                self.print_str('开始准备安装！')

                self.set_progress({'progress': 100})
                os.system('sudo python3 '+ self.SYSTEM_DIR +'/install.py update')

                self.print_str('新系统安装成功，即将重启设备！','p')

        self.set_progress({'progress': 100})

        time.sleep(5)

    # 保存进度
    def set_progress(self, savejson):
        wstr = json.dumps(savejson)
        with open(self.UPDATE_FILE, 'w') as f:
            f.write(wstr)

    def reset_progress(self):
        os.system('sudo rm -f '+ self.UPDATE_FILE)

    def main(self):
        argv = ''
        if len(sys.argv)>1:
            argv = sys.argv[1]

        if argv=='isupdate':
            self.menu_ckver('git')

        elif argv=='startupdate':
            self.menu_startup()

        else:
            if os.path.isdir(self.SYSTEM_DIR):
                self.menu()
            else:
                self.menu_startup()

if __name__ == "__main__":
    update().main()