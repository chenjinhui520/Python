import os


# os.sep 路径分隔符，自动识别系统平台（Linux / Windows）
p = 'D:' + os.sep + 'get' + os.sep + 'SS' + os.sep + 'views'

for parent, dirname, filenames in os.walk(p):
    # parent：父目录
    # dirname：父目录下面的子目录
    # filenames：父目录或子目录下面的所有文件，一个目录下面的文件构成一行列表
    for filename in filenames:
        # 将文件名切割成前缀和后缀
        prefix, suffix = filename.split('.')
        # 获取旧的文件名
        old_file_name = prefix + '.' + suffix
        # 获取新的文件名
        new_file_name = prefix + '.html'
        # 获取旧的文件绝对路径
        old_name = os.path.join(parent, old_file_name)
        # 获取新的文件绝对路径
        new_name = os.path.join(parent, new_file_name)
        # 重命名文件
        os.rename(old_name, new_name)
