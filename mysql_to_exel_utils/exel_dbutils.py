import pymysql as mysql
import configparser


def execute_sql(sql):
    conn = None
    cur = None
    fields = ()          # 格式为元组嵌套元组，一列属性为一个元组
    result = ()          # 格式为元组嵌套元组，一行数据为一个元组
    conf = configparser.ConfigParser()
    conf.read('ssh.conf', encoding='utf-8')
    try:
        conn = mysql.connect(
            host=conf.get('mysql', 'mysql_host'), port=conf.getint('mysql', 'mysql_port'),
            user=conf.get('mysql', 'mysql_user'), passwd=conf.get('mysql', 'mysql_passwd'),
            db=conf.get('mysql', 'mysql_db'), charset=conf.get('mysql', 'mysql_charset')
        )
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        fields = cur.description
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return fields, result

