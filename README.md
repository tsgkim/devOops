# devOops

服务、进程监听，挂掉自动重启，并用阿里大于短信自动通知

在 https://github.com/glennzw/DevOops 上改版而成，感谢原作者

# 使用说明：
#### 安装 python、pip 

#### git clone 本项目

#### 配置 services.json
```
eg: 配置 nginx
     {
       # 短信通知是哪个服务
       "name" : "nginx", 
       # 服务真正名称，必须和服务名一样
       "proc" : "nginx",
       # 服务启动命令，必须和服务启动命令一样
       "restart": "service nginx start"
     }
```

#### 配置 pid.json
```
eg: 配置 jenkins
    说明：jenkins 是一个 war 包，在tomcat容器中运行
     {
       # 短信通知是哪个进程
       "name" : "jenkins",
       # 进程真正名称，必须和进程名一样
       "proc" : "ps -ef | grep -v grep | egrep /usr/local/tomcat7/jenkins/conf/logging.properties",
       # 进程启动脚本，必须和进程启动命令一样（就是 怎样启动 这个 jenkins 所在的 tomcat 命令，我这里封装了一个脚本，所以写成这样）
        "restart": "sh /script/jenkins/start.sh"
     }
```
       
#### 配置 阿里大于短信通知、程序定时执行配置
```
[ali]
# 阿里大于短信发送 app-key
key: 
# 阿里大于短信发送 app-secret
secret:
# 阿里大于短信发送 签名名称
sign: 
# 默认，无需配置
type: normal
# 接收短信手机号
phone: 
# 阿里大于短信发送模板变量
username: 
# 服务异常通知短信模板
noticeTemplate: 
# 服务重启成功短信模板
successTemplate: 
# 服务重启失败短信模板
errorTemplate: 

[Other]
# 设置多长时间重新监听服务、进程
Interval: 10
```
因为程序中配置了下面模板中的变量，请务必按照此模板配置在你的阿里大于上面，如果你能改程序，请随意配置...

服务异常通知短信模板

![服务异常通知短信模板](http://resource.tsg.kim/%E6%9C%8D%E5%8A%A1%E7%9B%91%E5%90%AC%E9%80%9A%E7%9F%A5.png)

服务重启成功短信模板

![服务重启成功短信模板](http://resource.tsg.kim/%E6%9C%8D%E5%8A%A1%E7%9B%91%E5%90%AC%E6%88%90%E5%8A%9F%E9%80%9A%E7%9F%A5.png)

服务重启失败短信模板

![服务重启失败短信模板](http://resource.tsg.kim/%E6%9C%8D%E5%8A%A1%E9%87%8D%E5%90%AF%E5%A4%B1%E8%B4%A5%E9%80%9A%E7%9F%A5.png)
          
#### 安装 必要的包
```
说明：如果下面包有，请忽略此步骤，如果后台运行 devOops.py 提示缺少包，请按照下面示例安装 -->  pip install 缺少的包名
pip install top
pip install psutil
```

#### 后台运行 devOops.py
```
 nohup python -u devOops.py > /var/log/python/devOops.log 2>&1 &
 运行日志存放位置： /var/log/python/devOops.log
```

#### 不懂配置请联系我QQ: 1515503123
