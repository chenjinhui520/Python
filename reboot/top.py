# 定义函数
def getTopN(log_file, topN=10):
    # 第一步：打开文件，统计IP,URL,status获取访问次数
    rt_dict = {}
    log_files = open(log_file, 'r')
    while True:
        line = log_files.readline()
        if not line:
            break
        (ip, url, status) = line.split()[0], line.split()[6], line.split()[8]
        rt_dict[(ip, url, status)] = rt_dict.get((ip, url, status), 0) + 1
    log_files.close()
    # 字典数据转换成list，方便排序
    rt_list = rt_dict.items()
    # 冒泡排序，获取TOPN
    # for j in range(topN):
    #     for i in range(0, len(rt_list)- 1):
    #         if rt_list[i][1] > rt_list[i + 1][1]:
    #             rt_list[i],rt_list[i+1] = rt_list[i+1],rt_list[i]
    # result = rt_list[-1:-(topN+1):-1]
    result = sorted(rt_list, key=lambda x: x[1], reverse=True)[:topN]
    return result
    html = '''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>

        <body>
            <h3>Hello Reboot!</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th>Count</th>
                        <th>IP</th>
                        <th>URL</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {tbody}
                </tbody>
            </table>
        </body>
    </html>
    '''
    title = 'Reboot教育'
    tbody = ''
    for line in result:
        tbody += '<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>' % \
                 (line[1], line[0][0], line[0][1], line[0][2])
    with open('templates/logs.html', 'w') as f:
        f.write(html.format(title=title, tbody=tbody))

