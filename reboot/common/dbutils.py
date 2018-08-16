import pymysql as mysql
import configparser


class MySQLHelper(object):
    # 定义初始化属性函数
    def __init__(self):
        self.conf = configparser.ConfigParser()
        self.conf.read('D:\\Flask\\reboot\conf\\reboot.conf')
        self.__host = self.conf.get('mysql', 'MYSQL_HOST')
        self.__port = self.conf.getint('mysql', 'MYSQL_PORT')
        self.__user = self.conf.get('mysql', 'MYSQL_USER')
        self.__passwd = self.conf.get('mysql', 'MYSQL_PASSWD')
        self.__db = self.conf.get('mysql', 'MYSQL_DB')
        self.__charset = self.conf.get('mysql', 'MYSQL_CHARSET')
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

    # 执行单行
    def execute(self, sql, args=()):
        count = 0
        try:
            count = self.cur.execute(sql, args)
            self.commit()
            self.close()
        except Exception as e:
            print(e)
        return count

    # 执行多行
    def execute_many(self, sql, args=()):
        count = 0
        try:
            count = self.cur.executemany(sql, args)
            self.commit()
            self.close()
        except Exception as e:
            print(e)
        return count

    # 查询一行
    def fetch_one(self, sql, args=()):
        result = ()
        count = self.execute(sql, args)
        try:
            result = self.cur.fetchone()
            self.close()
        except Exception as e:
            print(e)
        return count, result

    # 查询指定行
    def fetch_many(self, number, sql, args=()):
        result = ()
        count = self.execute(sql, args)
        try:
            result = self.cur.fetchmany(number)
            self.close()
        except Exception as e:
            print(e)
        return count, result

    # 查询所有行
    def fetch_all(self, sql, args=()):
        result = ()
        count = self.execute(sql, args)
        try:
            result = self.cur.fetchall()
            self.close()
        except Exception as e:
            print(e)
        return count, result

    # 提交方法
    def commit(self):
        if self.conn:
            self.conn.commit()

    # 关闭连接方法
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


