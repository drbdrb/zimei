#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from package.config import config
from package.include.model import model
from package.include.mylib import mylib
import os;
import re;
import time;
import requests

#状态通知
def state_notice(devname='', is_online=0 ):
    post = {}
    post['title']   = '手机是否在家状态通知';
    post['content'] = '手机：'+devname+'<br/>状态：'+ str('在家' if (is_online) else '离开') + '<br/>时间：'+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());

    r = mylib.emain_notice( post )      # 调用邮件通知接口
    print(r)

#读取配置
def get_conf(db):
    config={}
    cursor = db.table('nmap_config').sel()
    for row in cursor:
        config[row['key']] = row['value']
    #config['is_nmapall'] = '1'
    return config

#扫描单机
def nmap_mon(db):
    config = get_conf(db);
    if config['is_nmapall']=='1':
        nmap_all(db)
        return False;

    maplist = db.table('nmap_mon').sel();
    is_nmapall = False;
    for v in maplist:
        if v['ip']:
            cmd ='nmap -T5 -sn '+ v['ip'] + '|grep '+ v['mac'];
            out = os.popen(cmd).read()
            updata={}
            updata['up_time'] = str(int(time.time()))
            if len(out)>0:
                #print( v['mac']+"-在线\r\n" )
                updata['is_online'] = 1;
                db.table('nmap_mon').where({'mac':v['mac']}).save(updata);
                # 记录行为
                #end_uptime = db.table('nmap_mon_list').where({'mac':v['mac']}).order('id desc').getField('up_time');
                #uplist['mac'] = v['mac'];
                #uplist['up_time'] = date('Y-m-d H:i:s',updata['up_time']);
                #uplist['jiange']  = updata['up_time'] - strtotime(end_uptime);
                #db.table('nmap_mon_list').add(uplist);
                #unset(uplist);
            else:
                #print( v['mac'] + "-离线-" + str(int(updata['up_time']) - int(v['up_time'])) +"\r\n");
                if ((int(updata['up_time'])-int(v['up_time'])) <= 500):
                    updata['is_online'] = v['is_online'];
                else:
                    updata['is_online'] = 0;
                    del updata['up_time']
                    db.table('nmap_mon').where({'mac':v['mac']}).save(updata);

            if updata['is_online'] != v['is_online']: state_notice(v['notename'], updata['is_online']);
            del out,updata
        else:
            is_nmapall = True

    if is_nmapall: db.table('nmap_config').where({'key':'is_nmapall'}).setField('value',1)

#扫描全部
def nmap_all(db):
    config = get_conf(db);
    if config['is_nmapall']!='1':return False;

    cmd = 'nmap -T5 -sP '+config['startip']+config['endip'];
    pat_ip = re.compile(r"((\d{1,3}\.){3}\d{1,3})");
    pat_mac = re.compile(r"([A-F0-9]{2}(:[A-F0-9]{2}){5})\s*\((.+)\)");
    out = os.popen(cmd).read()
    outarr = out.split('Nmap')
    db.table('nmap_online').setField({'is_online':0});		#全部设备离线
    for x in outarr:
        item_arr=x.splitlines()
        new_data = {'ip':'','mac':'','name':''};
        res = pat_ip.findall(item_arr[0])
        if res:
            new_data['ip']=res[0][0]

        if len(item_arr)>2:
            res = pat_mac.findall(item_arr[2])
            if res:
                new_data['mac']=res[0][0]
                new_data['name'] = res[0][2]

        show_mac = new_data['mac'];
        if show_mac:
            new_data['up_time'] = int(time.time())
            new_data['is_online'] = 1
            where={'mac':new_data['mac']};
            cx = db.table('nmap_online').where(where).find()
            if cx:
                del new_data['mac']
                up = db.table('nmap_online').where(where).save(new_data);
            else:
                up = db.table('nmap_online').add(new_data);
            #print(where['mac']+' ==> '+new_data['ip']+' ==> '+str('在线'if(new_data['is_online']==1)else'离线')+"\n")


    #更新监控库
    maplist = db.table('nmap_mon').sel();
    if maplist:
        for k in maplist:
            where={'mac':k['mac']};
            recx = db.table('nmap_online').where(where).find();
            if len(recx)>0:
                cx = recx[0]
                updata={}
                updata['ip'] 		 = cx['ip'];
                updata['up_time'] 	 = cx['up_time'];
                updata['is_online']  = cx['is_online'];
                db.table('nmap_mon').where(where).save(updata);
                del updata;

    #将扫描全局改为不扫描
    db.table('nmap_config').where({'key':'is_nmapall'}).setField('value',0)

def main():
    db = model(config['database']);
    nmap_mon(db)
    db.close();

#开始扫描
if __name__ == '__main__':
    main()
