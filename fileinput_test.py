import fileinput

'''
# 文件内容处理

# 获取文件
fileinput.input('content.txt')
# 判断当前行是否是文件的第一行
a = fileinput.isfirstline()
# 显示文件的行号
b = fileinput.lineno()
# 显示当前是在文件的第几行
c = fileinput.filelineno()
# 获取当前文件名
file_name = fileinput.filename()

'''

# backup：开启备份，文件后缀为 .bak
# inplace：直接修改源文件
for line in fileinput.input('content.txt', backup='.bak', inplace=1):
    line = line.replace('++', '#')
    print(line, end='')

