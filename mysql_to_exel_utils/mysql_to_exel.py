import string
from openpyxl import Workbook
from mysql_to_exel_utils.exel_dbutils import execute_sql


# 自动生成 SQL 字段列表长度工具
def GenerateCharacter(n, limit=1048576):
    c = int(n / 26)
    y = int(n % 26)
    if n <= 26:
        character = []
        for i in range(n):
            character.append(string.ascii_uppercase[i])
        return character
    elif n <= limit:
        character = [c for c in string.ascii_uppercase]
        for i in range(c):
            if i + 1 == c:
                for e in range(y):
                    character.append(character[i] + string.ascii_uppercase[e])
            else:
                for e in [character[i] + c for c in string.ascii_uppercase]:
                    character.append(e)
        return character
    else:
        return "more than %s restrictions" % limit


def mysql_to_exel(sql, path):
    # 获得工作簿对象
    file = Workbook()

    # 创建 sheet，第一种方式
    # sheet = file.active

    # 创建 sheet，pos 为 sheet 的名称，index=0 表示这是第一个 sheet，第二种方式
    sheet = file.create_sheet('p2p', index=0)

    # 删除某个 sheet
    # file.remove(sheet)

    # 定义 sheet 名称
    # sheet.title = 'p2p'

    # 定义 sheet 颜色
    sheet.sheet_properties.tabColor = '1072BA'

    # 操作 cell
    # sheet['A1'] = 4

    # 执行查询 SQL 语句
    fields, result = execute_sql(sql)
    # 统计 SQL 的字段长度
    ascii_uppercase = GenerateCharacter(len(fields))

    # 插入列
    for field in range(0, len(fields)):
        sheet["%s%d" % (ascii_uppercase[field], 1)] = fields[field][0]

    # 插入行
    for row in range(1, len(result) + 1):
        for field in range(0, len(fields)):
            sheet["%s%d" % (ascii_uppercase[field], row + 1)] = result[row - 1][field]

    # 保存 exel 文件
    file.save(path)


mysql_to_exel('select * from user', 'C:\\Users\liygmf\Desktop\p2p.xlsx')
