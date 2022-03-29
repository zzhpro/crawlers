# 查看没正常结束的python进程
ps -f | grep python 

# 并取第二列，kill
ps -f | grep python | awk '{print $2}' | xargs kill

ps    # 简略显示当前tty的进程
ps -e # 简略显示所有进程
ps -f # 展开显示当前tty的进程
ps -ef# 展开显示所有进程

grep -v xxx #去除含有xxx的行
grep -n xxx #标注行号
grep -i xxx #忽视大小写

df -h # 以人可读的方式查看挂载的各文件系统信息

lastlog --user xxx # 查看xxx用户上次登录的记录

top 
# 其中的 %CPU含义为， 更新周期内该进程使用的CPU时间 / 更新周期，若该进程包含多个线程且CPU确实为多核，则这个数字可以大于100%
# %MEM，使用内存占物理内存的比例


touch filename
# 在不修改文件的情况下更新文件的最近修改时间
# 也可以用于创建新的空文件

var_name=xxx #定义变量
$var_name 引用变量
