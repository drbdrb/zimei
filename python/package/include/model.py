# -*- coding: utf-8 -*-
import json
import sqlite3

class model:
    '''数据库模型类'''
    dbPath = ''
    dbKey = ''
    datatable = ''     #数据表
    sql = ""           #sql语句
    wheresql = ""      #条件语句
    ordersql = ""      #排序语句
    limitsql = ""      #限制数量语句
    fields = "*"       #限制返回的字段

    def __init__(self, dbPath, dbKey='' ):
        self.connection = sqlite3.connect(dbPath)    #数据库对象
        self.dbPath = dbPath
        self.dbKey = dbKey

    def resetparame(self):         #重置所有参数
        self.datatable = ""
        self.sql =""           #sql语句
        self.wheresql = ""     #条件语句
        self.ordersql = ""     #排序语句
        self.limitsql = ""     #限制数量语句
        self.fields = "*"      #限制返回的字段;


    #---------------------------------------
    '''
     * 检测提交的数据是否正确
     * 数据格式:json/table
    '''
    def checkjson(self, jsonstr ):               #传入的数据如果是字典那么返回该字典数据不是就返回False
        json={}
        if self.typeof(jsonstr)!='dict':
            try:
                json = json.loads( jsonstr )   #将字符串json转换字典对象
            except:
                json = ''
        else:
            json = jsonstr

        if (len(json)>0):
            return json
        else:
            return False

    def typeof(self, variate):                   #检测类型模块，在返回类型
        type1 = ""
        if type(variate) == type(1):
            type1 = "int"
        elif type(variate) == type("str"):
            type1 = "str"
        elif type(variate) == type(12.3):
            type1 = "float"
        elif type(variate) == type([1]):
            type1 = "list"
        elif type(variate) == type(()):
            type1 = "tuple"
        elif type(variate) == type({"key1":"123"}):
            type1 = "dict"
        elif type(variate) == type({"key1"}):
            type1 = "set"
        return type1


    def getTable(self,sql):                                          #添加操作表
        tab=[]
        cursor = self.connection.cursor()
        cursor.execute(sql)                                   #cursor游标execute可以增删改查
        col_list = [tuple[0] for tuple in cursor.description]  #得到域的名字
        rs = cursor.fetchall()                                  #读取全部
        cursor.close()

        for row in rs:
            line_arr={}
            for i in range(len(col_list)):
                line_arr[col_list[i]] = row[i]                     #添加到字典
            tab.append(line_arr)
        return tab                                                  #返回了列表


    def table(self, datatab ):                                      #输入表名,输出self，且具有连贯操作
        self.datatable = datatab
        return self

    #查询条件转换
    '''
     * 查询条件转换
     * 用法：{'字段':{"EQ":"比较值"}}
     * db = model();
        tab ={'rowid':{"LT":"2"}}
        或
        tab ={'rowid':'2'}
        aa = db.table("Options").where(tab).sel();
    '''
    def wheresw(self, k, v):                #数据库读取添加等等操作时进行条件过滤#'key','clientid'
        val = v[1]                         #
        whereTab = {
            'EQ': k +"='"+ val +"'",      #等于
            'NEQ': k +"<>'"+ val +"'",    #不等于
            'GT': k +">"+val,             #大于
            'EGT': k +">="+val,           #大于等于
            'LT': k +"<"+val,             #小于
            'ELT': k +"<="+val,           #小于等于
            'LIKE': k +" LIKE "+val,      #模糊查询
            'BETWEEN': k +" BETWEEN "+val,#区间查询
            'IN': k +" IN "+val,          #IN 查询
            'NOTBETWEEN': k +" NOT BETWEEN "+val,
            'NOTIN': k +" NOT IN "+val
        }
        vv = v[0].upper()              #字母转换为大写
        restr = whereTab[vv]
        return restr


    def where(self, tab='' ):                              #where条件 假如是{'key':'clientid'}
        if len(tab)<=0: return self                        #（1）不传值那么返回self
        elif self.typeof(tab)=="str":                      #（2）如果是字符串
            self.wheresql = " WHERE " + tab                #条件语句self.wheresql=WHERE+字符串
        else:
            datatab = self.checkjson( tab )                #（3）self.checkjson检测提交的数据是否正确
                                                            ##传入的数据如果是字典那么返回该字典数据不是就返回False
            if datatab==False:
                return False                               #检测出不是字典那么直接返回 false

            sql = ''                                       #如果传入的是字典类型的数据
            for k in datatab:                               #循环输出字典datatab数据k=key
                sql1 = ""
                if self.typeof(datatab[k]) == 'list':        #datatab字典里的数据如果是列表### {'key':'clientid'}
                    sql1 = self.wheresw(k,datatab[k])      #'key','clientid'#!!!!
                elif self.typeof(datatab[k]) == "int":
                    sql1 = k + "="+ str(datatab[k])             #key=clientid
                else:
                    sql1 = k + "='"+ datatab[k] +"'"       #key='clientid'


                sql += sql1 +" AND "                       #sql='clientid' AND

            sql = sql.rstrip(" AND ")                      #sql按照要求去掉尾巴（AND）得到sql='clientid'
            self.wheresql = " WHERE " + sql                #self.wheresql =WHERE key='clientid'
        return self                                        #无论何值都返回self，支持连贯操作


    def order(self, str ):               #生成排序语句
        self.ordersql = " ORDER BY " + str
        return self


    def limit(self, start, ends=""):     #限制结果数量
        if (start==False): start = "1"
        if ends !="": ends = "," + ends
        self.limitsql = " LIMIT " + start + ends
        return self


    def field(self, strs):               #获取指定字段
        if self.typeof(strs)=="str":
            self.fields = strs
        else:
            self.fields = "*"
        return self


    def find(self):                      #返回单条记录

        sql = "SELECT " + self.fields + " FROM "+ self.datatable       #fields = "*"; 限制返回的字段。#datatable='' 是数据表
        if self.wheresql !="" : sql += self.wheresql                    #" WHERE " + tab;
        if self.ordersql !="" : sql += self.ordersql
        sql += " LIMIT 1"
        datatab = self.getTable( sql )
        self.resetparame()
        if datatab:
            return datatab
        else:
            return False


    def sel(self):                          #查询,多条
        sql = "SELECT " + self.fields + " FROM "+ self.datatable
        if self.wheresql !="": sql += self.wheresql
        if self.ordersql !="": sql += self.ordersql
        if self.limitsql !="": sql += self.limitsql
        rs = self.getTable(sql)
        self.resetparame()             #初始化
        if rs:
            return rs
        else:
            return False


    def count(self):                        #查询数量
        sql = "SELECT COUNT(" + self.fields + ") AS num FROM "+ self.datatable
        if (self.wheresql !=""): sql += self.wheresql
        if (self.ordersql !=""): sql += self.ordersql
        if (self.limitsql !=""): sql += self.limitsql
        rs = self.getTable(sql)
        self.resetparame()
        return rs!='' if rs[1]["num"] else "0"


    def add(self, tab ):                    #添加数据
        datatab = self.checkjson( tab )
        if (datatab==False): return False
        instr1 = ""
        instr2 = ""
        for k in datatab:
            instr1 +=  k +  ","
            instr2 +=  "'" + str(datatab[k]) + "',"

        instr1 = instr1.rstrip(",")
        instr2 = instr2.rstrip(",")
        sql = "INSERT INTO "+ self.datatable +" ("+ instr1 +") VALUES ("+ instr2 +");"
        return self.run( sql )

    #---------------------------------------------------------------------
    '''
    更新/保存更改
    按where条件更新数据,如果记录不存在则添加(add)
    缺陷。 未对WHERE 语句进行 转义
    '''
    def save(self, tab ):
        datatab = self.checkjson( tab )    #检测是否为字典类型
        if (datatab==False): return False

        upsql = "UPDATE "+ self.datatable +" SET "
        setsql = ""
        for k in datatab:
            setsql += k +  "='" + str(datatab[k]) + "',"
        setsql = setsql.rstrip(",")

        upsql += setsql
        if self.wheresql!="":
            upsql += self.wheresql
            ret = self.run( upsql )
            if ret:
                return True
            else:
                return False
        else:
            return False

    def setField(self, upkey, upval=''):    # 快速设置字段值
        datatab = self.checkjson( upkey )

        upsql = "UPDATE "+ self.datatable +" SET "
        setsql = ""
        if (datatab==False):
            if self.typeof(upkey)=="str" and upval!='':
                setsql = upkey +"='"+ str(upval) +"'"
            else:
                return False
        else:
            for k in datatab:
                setsql += k +  "='" + str(datatab[k]) + "',"
            setsql = setsql.rstrip(",")

        upsql += setsql
        if self.wheresql!="":
            upsql += self.wheresql
        ret = self.run( upsql )
        if ret:
            return True
        else:
            return False


    def delete(self):                               #删除
        sql = "DELETE FROM "+ self.datatable
        if self.wheresql!="": sql += self.wheresql
        return self.run( sql )


    def run(self, sql ):                            #执行
        newsql = sql
        cursor = self.connection.cursor()
        self.resetparame()
        exe = cursor.execute( newsql )
        self.commitTrans()
        cursor.close()
        return exe


    def close(self):            #关闭数据库
        #self.cursor.close();
        self.connection.close()


    def truncate(self):       #清空表格所有记录
        if (self.datatable==False):return False
        cursor = self.connection.cursor()
        re = cursor.execute("DELETE FROM %s",self.datatable)
        cursor.close()
        return re


    def drop(self):     #删除表格
        if (self.datatable==False):return False
        cursor = self.connection.cursor()
        re = cursor.execute("DROP TABLE %s",self.datatable)
        cursor.close()
        return re


    def vacuum(self):       #压缩数据库
        cursor = self.connection.cursor()
        cursor.execute("VACUUM")
        cursor.close()


    def encrypt(self):      #加密
        cursor = self.connection.cursor()
        cursor.rekey(self.dbKey)
        cursor.close()


    def decrypt(self):           #解密
        cursor = self.connection.cursor()
        cursor.rekey("")
        cursor.close()


    def changes(self):   #返回数据库最近一次运行exec()所改变的行数
        cursor = self.connection.cursor()
        count = cursor.changes()
        cursor.close()
        return count


    def busyTimeout(self, ms = "100000"):       #数据锁定冲突时的重试时间(以毫秒为单位)
        cursor = self.connection.cursor()
        cursor.busyTimeout(ms)
        cursor.close()


    def beginTrans(self):               #开始事务
        self.connection.beginTrans()


    def commitTrans(self):          #提交事务
        self.connection.commit()


    def rollbackTrans(self):         #回滚事务
        self.connection.rollback()


'''
查询表达式的使用格式

db.where()      查询条件 {'表字段':{'表达式'：'内容'}}

表达式          含义             协助记忆
--------------------------------------------
EQ              等于（=）        equal
NEQ             不等于（<>）     not equal
GT              大于（>）        greater
EGT             大于等于（>=）   equal or greater
LT              小于（<）        less than
ELT             小于等于（<=）   equal or less than
LIKE            模糊查询
[NOT]BETWEEN    （不在）区间查询
[NOT]IN         （不在）IN 查询
--------------------------------------------

db.order()      排序条件("id DESC/ASC")字符串
db.limit()      限制结果数量(1,20)从第1条记录开始查询20条结果
db.field()      获取指定字段db.field('user,pass')

----------------------------------------------
from package.model import model
db = model('./data.db')         数据模型操作类.
db.table() 添加操作表 传入值"表名，示例:db.table("user")"

db.close()  = 关闭数据库
db.drop()   = 删除表格
db.vacuum() = 压缩数据库
db.encrypt()= 加密数据库
db.decrypt()= 解密数据库

db.add(data)  添加数据
    data = {字段:内容}
    ret = db.table("").add(data);

db.save(data)  更新/保存数据
    condition={'field':{"EQ":"value"}}
    ret = db.table("").where(condition).save(data);
    #按where条件更新数据,如果记录不存在则添加(add)

db.find()  查询单条记录
    condition={'field':{"EQ":"value"}}
    tab = db.table("__").where(condition).order("rowid DESC").find();

db.sel()  查询多条记录
    condition={'field':{"EQ":"value"}}
    tab = db.table("__").where(condition).order("rowid DESC").sel()

db.count()  查询记录数量
    condition={'field':{"EQ":"value"}}
    count = db.table("__").field("rowid").where(condition).count()

db.changes()  返回数据库最近一次运行exec()所改变的行数

db.delete()  删除记录
    condition={'field':{"EQ":"value"}}
    db.table("__").where(condition).delete()

db.truncate() 删除表格所有记录
    db.table("__").truncate();

db.drop() 删除表格 =
    db.table("__").drop();

db.run(sql) 执行原生的SQL语句。

db.busyTimeout(10000);=数据锁定冲突时的重试时间,以毫秒为单位,成功返回True\nbusyHandler()函数控制重试次数,busyTimeout()函数控制重试时间\n这两个函数可相互影响,设置一个必然然取消另一个

db.beginTrans();=开始DEFERRED事务\n默认不获取任何锁,直到需要锁的时候才获取锁,\n开启事务以后,可使用rollbackTrans()函数撤消所有更改,\n使用commitTrans()函数提交所有更改.\n使用此函数可以避免sqlite为每个操作创建一个默认事务\n批量操作数据库时可显著提升sqlite执行效率.
db.commitTrans();=提交事务
'''
