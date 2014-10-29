#!/usr/bin/env python
#-*-coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 配置加载 db_config.json
# 定期更新配置及重载未更新成功的history记录,
# 未更新成功记录文本history.log，更新成功后改名

import simplejson as json
import datetime
import time
import os
import logging
import MySQLdb,socket
import MySQLdb.cursors


socket.setdefaulttimeout(5)


def initlog(logfile):
    import logging
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

 
class DBConn:
    conn = None
    def __init__(self):
        self.host='192.168.1.31'
        self.user='root'
        self.password='123456'
        self.port=3759
    #建立和数据库系统的连接
    def connect(self):
        self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.password,port=self.port,cursorclass = MySQLdb.cursors.DictCursor)
    #获取操作游标
    def cursor(self):
        try:
            return self.conn.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            return self.conn.cursor()
    def commit(self):
        return self.conn.commit()
    #关闭连接
    def close(self):
        return self.conn.close()

  

def loadmysql():
    dbconn = DBConn()
    try:
        dbconn.connect()
        conn=dbconn.cursor()
        conn.execute('set names utf8')
        sql = "SELECT urltable.urlid,urltable.url,urltable.projectname,rstable.rsid,rstable.rs FROM httptest.urltable,httptest.rstable WHERE urltable.urlid=rstable.urlid ORDER BY urlid"
        conn.execute(sql)    
        alldata = conn.fetchall()
        db_cfg=[]
        for i in alldata:
            result={}
            result['urlid']=i['urlid']
            result['url']=i['url']
            result['projectname']=i['projectname']
            result['rsid']=i['rsid']
            result['rs']=i['rs']
            db_cfg.append(result)
    except (Exception,MySQLdb.Error,AttributeError,IOError),args:
        print args
    return db_cfg


def reloadsave(data):
    dbconn = DBConn()
    try:  
        dbconn.connect()
        conn=dbconn.cursor()
        conn.execute('set names utf8')
        for i in open(data).readlines():
            #print i
            conn.execute(i)
        dbconn.commit()
    except (Exception,MySQLdb.Error,AttributeError,IOError),args:
        print args
        logging=initlog("Warning.log")
        logging.warning(str(args)+'\n')
    dbconn.close()
def check():
        f = urllib2.urlopen(install_url)
        data = f.read()
        f.close()
        json_list = eval(data)
def createconfig(db_config):
    format2="%Y-%m-%d %H:%M:%S"
    info= "%s loadconfig success!"%(time.strftime(format2))
    try:
        file=open("db_cfg.json","w+")
        file.write(db_config.encode('utf-8'))
        print info
        logging.info(info)
    except IOError,args:
        print args
    file.close()
    
if __name__ == "__main__":
    format="%Y%m%d%H%M%S"
    
    t1=time.strftime(format)
    logging=initlog("debug.log")
    db_hosts_info=loadmysql()
    try:
        db_config=json.dumps(db_hosts_info,sort_keys=True,indent=4,ensure_ascii = False)
    except  (TypeError, ValueError),args:
        print args
   
    createconfig(db_config)
    if os.path.exists("history.log"):
        reloadsave("history.log")
        newname="history%s.log"%t1
        try:
            os.rename("history.log",newname)
        except IOError,args:
            print args
        print "rename history.log to %s"%newname
    else:
        print "not exists history.log"
  
    
     
  
