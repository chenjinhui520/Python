import pymysql as mysql
from reboot import gconf


class MySQLconnection(object):
    # 定义初始化属性函数
    def __init__(self, host, port, user, passwd, db, charset='utf8'):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db = db
        self.__charset = charset
        self.conn = None
        self.cur = None
        self.__content()

    # 连接方法
    def __content(self):
        try:
            self.conn = mysql.connect(host=self.__host, port=self.__port,
                                      user=self.__user, passwd=self.__passwd,
                                      db=self.__db, charset=self.__charset)
            self.cur = self.conn.cursor()
        except Exception as e:
            print(e)
    # 具体的方法（拼接胳膊和腿）
    # 提交方法

    def commit1(self):
        if self.conn:
            self.conn.commit()
    # 关闭连接方法

    def close(self):
        self.commit1()
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    # 执行动作方法

    def execute1(self, sql, args=()):
        count = 0
        if self.cur:
            count = self.cur.execute(sql, args)
        return count
    # 查询方法

    def fetch(self, sql, args=()):
        count = 0
        rt_list = []
        if self.cur:
            count = self.execute1(sql, args=args)
            rt_list = self.cur.fetchall()
        return count, rt_list

    # 类的对外方法（犹如太极拳，柔阔所有机器零件，整合成一个完整的方法）
    @classmethod
    def execute_sql1(cls, sql, args=(), fetch=True):
        rt_list = []
        conn = MySQLconnection(host=gconf.MYSQL_HOST, port=gconf.MYSQL_PORT,
                               user=gconf.MYSQL_USER, passwd=gconf.MYSQL_PASSWD,
                               db=gconf.MYSQL_DB, charset=gconf.MYSQL_CHARSET)
        if fetch:
            count, rt_list = conn.fetch(sql, args)
        else:
            count = conn.execute1(sql, args)
        conn.close()
        return count, rt_list

def execute_sql(sql, args=(), fetch=True):
    conn = None
    cur = None
    count = 0
    rt_list = []
    try:
        conn = mysql.connect(host=gconf.MYSQL_HOST, port=gconf.MYSQL_PORT,
                             user=gconf.MYSQL_USER, passwd=gconf.MYSQL_PASSWD,
                             db=gconf.MYSQL_DB, charset=gconf.MYSQL_CHARSET)
        cur = conn.cursor()
        count = cur.execute(sql, args)
        if fetch:
            rt_list = cur.fetchall()
        else:
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return count, rt_list
def executemany_sql(sql, args=(), fetch=True):
    conn = None
    cur = None
    count = 0
    rt_list = []
    try:
        conn = mysql.connect(host=gconf.MYSQL_HOST, port=gconf.MYSQL_PORT,
                             user=gconf.MYSQL_USER, passwd=gconf.MYSQL_PASSWD,
                             db=gconf.MYSQL_DB, charset=gconf.MYSQL_CHARSET)
        cur = conn.cursor()
        count = cur.executemany(sql, args)
        if fetch:
            rt_list = cur.fetchall()
        else:
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return count, rt_list

class User(object):
    pass


