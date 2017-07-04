#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def makeTag(tag_name, tag_time):
    u'''打标记'''
    import commands

    TAG_SERVICE = '/usr/bin/perl /usr/local/jobclient/bin/tag_service.pl'
    t = Time()
    date = t.changeFormat(tag_time, 'yyyy-mm-dd HH:MM:SS', 'yyyymmdd')
    cmd = TAG_SERVICE + ' --act=M --name=' + tag_name + ' --date=' + date
    printLog(cmd)
    (result, response) = commands.getstatusoutput(cmd)
    if result == 0 and response == '1':
        return True

    return False

def printLog(message, level=1):
    import sys
    u'''打印日志'''

    LEVEL_INFO = {
        0: 'DEBUG',
        1: 'INFO',
        2: 'WARNING',
        3: 'ERROR',
    }

    t = Time()
    if level > 3 or level < 0:
        level = 0

    print t.getNow() + ' [' + LEVEL_INFO[level] + '] ' + message
    sys.stdout.flush()

    return None

def getLocalIP(ifname='eth0'):
    import socket
    import fcntl
    import struct

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError, e:
        return None

    return ip

def httpRequest(url, params, port='80', method='POST', debug=False):
    u'''发起GET或者POST请求'''
    import urllib, urllib2

    body = urllib.urlencode(params);

    if debug:
        print url + '?' + body

    #返回
    result = None

    try:
        if method == 'GET':
            ret = urllib2.urlopen("%s?%s" % (url, body))
        elif method == 'POST':
            ret = urllib2.urlopen(url, body)
        result = ret.read()
    except Exception, e:
        print e

    return result

class DB:
    u'''数据库操作的一些方法'''
    def __init__(self):
        self.conn = ''
        self.host = ''
        self.db = ''
        self.user = ''
        self.passwd = ''
        self.port = ''
        self.charset = ''

    def connMySQL(self, host, db, user, passwd, port=3306, charset='utf8'):
        u'''连接MySQL数据'''
        import MySQLdb
        try:
            conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=int(port), charset=charset)
            self.conn = conn
            self.host = host
            self.db = db
            self.user = user
            self.passwd = passwd
            self.port = port
            self.charset = charset
            return conn
        except MySQLdb.Error, e:
            print "Connect to mysql failed [%d]: %s" % (e.args[0], e.args[1])
        return None


    def close(self):
        u'''断开数据库连接'''
        import MySQLdb

        try:
            self.conn.close()
        except MySQLdb.Error, e:
            print "disconnect from mysql failed [%d]: %s" % (e.args[0], e.args[1])
        return None

    def _testConn(self):
        u'''断线重连功能'''
        import MySQLdb

        if not self.conn:
            print "No connection to mysql!"
            return False

        try:
            self.conn.ping()
            return True
        except MySQLdb.Error, e:
            print "Connection failed, reconnect to Mysql..."
            if self.connMySQL(self.host, self.db, self.user, self.passwd, self.port, self.charset):
                return True
            else:
                print "Connect to mysql failed [%d]: %s" % (e.args[0], e.args[1])
                return False

        return False

    def getResult(self, sql):
        u'''执行SQL获得返回数据'''
        import MySQLdb

        if not self._testConn():
            return None

        conn = self.conn
        try:
            cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
            cur.execute(sql)
            return cur.fetchall()

        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            return None

    def execSql(self, sql):
        u'''执行一条SQL语句'''
        import MySQLdb

        if not self._testConn():
            return None

        conn = self.conn
        try:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            return True

        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            return None

    def execSqlParam(self, sql, param):
        u'''带参数的执行一条SQL'''
        import MySQLdb

        if not self._testConn():
            return None

        conn = self.conn
        try:
            cur = conn.cursor()
            cur.execute(sql, param)
            conn.commit()
            return True

        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            return None

class Time:
    u'''时间处理相关的一些方法'''
    def getNow(self, format="yyyy-mm-dd HH:MM:SS"):
        u'''获取当前时间'''
        import time
        return time.strftime(self._transFormat(format), time.localtime())

    def unixTimeStamp(self, str, format="yyyy-mm-dd HH:MM:SS"):
        u'''获取指定时间的unix时间戳, 精确到秒'''
        import time
        return int(time.mktime(self._strToArray(str, self._transFormat(format))))

    def fromUnixTime(self, str, format="yyyy-mm-dd HH:MM:SS"):
        u'''从时间戳转化为时间字符串'''
        import time
        return time.strftime(self._transFormat(format), time.localtime(str))

    def isMonthEnding(self, str, format="yyyy-mm-dd HH:MM:SS"):
        u'''判断给定的日期是不是月末'''
        next_day = self.dateAdd(str, 1, 'days', format)
        if int(self.changeFormat(next_day, format, 'dd')) == 1:
            return True
        else:
            return False

    def dateAdd(self, str, interval, type, format="yyyy-mm-dd HH:MM:SS"):
        u'''时间增加'''

        to_second = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600,
            'days': 86400,
            'weeks': 604800,
        }
        try:
            new_time = self.unixTimeStamp(str, format) + interval * to_second[type]
            return self.fromUnixTime(new_time, format)
        except KeyError, e:
            print "wrong type: " + type + ", in [seconds|minutes|hours|days|weeks]"
            return None

    def changeFormat(self, str, from_format, to_format):
        u'''改变给定时间的输出格式'''
        import time
        return time.strftime(self._transFormat(to_format), self._strToArray(str, self._transFormat(from_format)))

    def _transFormat(self, format):
        u'''内部方法, 将输入的format转化为格式化的format'''
        format = format.replace('yyyy', '%Y')
        format = format.replace('yy', '%y')
        format = format.replace('mm', '%m')
        format = format.replace('dd', '%d')
        format = format.replace('HH', '%H')
        format = format.replace('MM', '%M')
        format = format.replace('SS', '%S')

        return format

    def _strToArray(self, str, format='%Y-%m-%d %H:%M:%S'):
        u'''内部方法, 将日期字符串转化为时间数组'''
        import time
        return time.strptime(str, format)
