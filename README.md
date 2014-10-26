hyperv-tool
===========

##hyperv管理工具

服务器安装

1. 准备工作
安装包请看 prepare文件夹
1.1 安装 python
1.2 安装 pywin
1.3 安装 wmi
1.4 安装 bottle
1.5 安装 requests (requests为cli依赖，根据情况选择安装)
注意
1. python 安装完成设置环境变量 path, 使可以从cmd中执行执行python命令
2. wmi, bottle, requests安装，先解压，然后 python setup.py install

++++++++++++++++++++++++++++++++++++++++

2. 安装程序
拷贝hyperv到服务器本地，盘符根目录下

1. 更改配置：
restapi.py文件
IMAGE_PATH 表示景象存储的根目录

2. 创建景象
手动创建vm，获得景象，以vhd结尾的文件，放到第一步配置的目录 _base下
文件名为48e66e4d9a1745f2957ed6d9a0b74d51.vhd
比如：
设置的 IMAGE_PATH="I:\\images" , 则景象文件存放到 I:\images\_base下，已48e66e4d9a1745f2957ed6d9a0b74d51.vhd
作为文件名, 如果有多个景象，则以不同文件名，但保证以vhd为后最

3. 安装
python restapi.py
验证启动成功
netstat -ano | findstr 8080
安装完成后，会在服务列表中看到，名字为 bottleServer, 重启的话，直接重启服务


===================================================================

客户端安装

1. 安装requests
2. 拷贝 hyperv文件夹
3. 更改host.py文件，写入所有hyper-v服务器列表

命令

python agentctl.py host_list
python agentctl.py use_host #说明：执行下面命令前先执行此命令，设置当前要链接的host，即host.py中设置的key
python agentctl.py help image_list
python agentctl.py help instance_create
python agentctl.py help instance_delete
python agentctl.py help instance_suspend
python agentctl.py help instance_resume
python agentctl.py help instance_list
python agentctl.py help instance_show
python agentctl.py help instance_pause
python agentctl.py help instance_unpause
python agentctl.py help instance_console 
# instance console会返回一个命令，比如：
{"rdp_console": "wfreerdp.exe /vmconnect:7EF512FB-BF28-4F28-BE5D-65175A329CAD /v:<host_ip>:2179"}
更改 <host_ip>为虚拟机所在hyper-v ip，使用tool文件夹下的 freerdp，解压，并在freerdp目录打开cmd
输入命令：wfreerdp.exe /vmconnect:7EF512FB-BF28-4F28-BE5D-65175A329CAD /v:<host_ip>:2179
会打开对应虚拟机的远程链接提示，输入对应hyper-v服务器用户名密码，即可

