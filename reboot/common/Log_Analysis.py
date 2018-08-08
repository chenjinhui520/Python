# 定义函数
def GetTopN(log_file):
    # 第一步：打开文件，统计IP,URL,status获取访问次数
    rt_dict = {}
    log_files = open(log_file, 'r')
    while True:
        line = log_files.readline()
        if not line:
            break
        (ip, url, status) = line.split()[0], line.split()[6], line.split()[8]
        rt_dict[(ip, url, status)] = rt_dict.get((ip, url, status), 0)+1
    log_files.close()
    # 字典数据转换成list，方便排序
    rt_list = rt_dict.items()
    result = sorted(rt_list, key=lambda x: x[1], reverse=True)
    return result


