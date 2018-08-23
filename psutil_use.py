import psutil

'''
# CPU使用统计
print(psutil.cpu_count(logical=False))
print(psutil.cpu_times())

for x in range(10):
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    print(cpu)

# 内存使用统计
print(psutil.virtual_memory())
print(psutil.swap_memory())

# 磁盘使用统计
print(psutil.disk_partitions())
print(psutil.disk_usage('D:\\'))
print(psutil.disk_io_counters())


# 网络使用统计
print(psutil.net_connections())
print(psutil.net_if_addrs())
print(psutil.net_if_stats())
print(psutil.net_io_counters())
'''

print(psutil.pids())
p = psutil.Process(9280)
print(p.name())
print(p.exe())
print(p.cwd())
print(p.cmdline())
print(p.ppid)
print(p.parent())
print(p.children)
print(p.status())
print(p.username())
print(p.create_time())
# print(p.terminal())
print(p.cpu_times)
print(p.memory_info)
print(p.open_files())
print(p.connections())
print(p.num_threads())
print(p.threads())
print(p.environ())

print(psutil.test())
