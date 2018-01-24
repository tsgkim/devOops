#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import json
import os
import subprocess
import sys
import time
from subprocess import call, STDOUT
import psutil
import requests
import top.api
import smtplib
from email.mime.text import MIMEText

reload(sys)
sys.setdefaultencoding('utf-8')

requests.packages.urllib3.disable_warnings()


# 获取时间
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


print get_time(), " --- 加载 config.ini"

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

# 短信配置
key = Config.get('ali', 'key')
secret = Config.get('ali', 'secret')
username = Config.get('ali', 'username')
sign = Config.get('ali', 'sign')
ali_type = Config.get('ali', 'type')
phone = Config.get('ali', 'phone')
noticeTemplate = Config.get('ali', 'noticeTemplate')
successTemplate = Config.get('ali', 'successTemplate')
errorTemplate = Config.get('ali', 'errorTemplate')

# 邮件配置
mail_host = Config.get('mail', 'mail_host')
mail_user = Config.get('mail', 'mail_user')
mail_pass = Config.get('mail', 'mail_pass')
mail_receivers = Config.get('mail', 'mail_receivers').split(',')
mail_subject = Config.get('mail', 'mail_subject')

FNULL = open(os.devnull, 'w')

print get_time(), " --- 加载 services.json"
with open('services.json') as json_data:
    SERVICES = json.load(json_data)

print get_time(), " --- 加载 pid.json"
print
with open('pid.json') as pid_data:
    PIDS = json.load(pid_data)


# 短信发送配置
def send_sms(param, template):
    print get_time(), "短信发送中......"
    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(key, secret))

    req.sms_type = ali_type
    req.sms_free_sign_name = sign
    req.sms_param = param
    req.rec_num = phone
    req.sms_template_code = template
    try:
        resp = req.getResponse()
        print get_time(), ' --- ', resp
        print get_time(), " --- 短信发送成功！"
    except Exception, e:
        print get_time(), ' --- ', e
        print get_time(), " --- 短信发送失败！"

    return resp


# 邮件发送配置
def send_mail(content):
    print content
    print get_time(), "邮件发送中......"
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = mail_subject
    msg['From'] = mail_user
    # msg['To'] = ";".join(mail_to_list)
    try:
        s = smtplib.SMTP_SSL(mail_host, 465)
        s.login(mail_user, mail_pass)
        s.sendmail(mail_user, mail_receivers, msg.as_string())
        s.close()
        print get_time(), " --- 邮件发送成功！"
    except Exception, e:
        print e
        print get_time(), " --- 邮件发送失败！"


# 服务是否运行
def is_service_running(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            return True
    return False


# 进程是否运行
def is_pid_running(name):
    res = subprocess.Popen(name, stdout=subprocess.PIPE, shell=True)
    tomcats = res.stdout.readlines()
    counts = len(tomcats)
    if counts == 1:
        return True
    return False


# 通知
def notify(param, template, content):
    send_sms(param, template)
    send_mail(content)


def main():
    # 内存使用率
    mem = str(psutil.virtual_memory().percent)
    # CPU 使用率
    cpu = str(psutil.cpu_percent())

    for s in SERVICES:
        name, proc, restart = s.get("name"), s.get("proc"), s.get("restart")
        if not is_service_running(proc):
            print get_time(), " --- %s 服务已停止，发送短信、邮件通知......" % name
            if restart:
                notify("{name:%s, service:%s, cpu:%s%%, ram:%s%%}" % (username, name, cpu, mem),
                       noticeTemplate,
                       "%s 服务已停止，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                call(restart.split(), stdout=FNULL, stderr=STDOUT)
                time.sleep(10)
                if is_service_running(proc):
                    notify("{name:%s, service:%s}" % (username, name), successTemplate,
                           "%s 服务重启成功，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                    print get_time(), " --- %s 服务重启成功" % name
                else:
                    notify("{name:%s, service:%s}" % (username, name), errorTemplate,
                           "%s 服务重启失败，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                    print get_time(), " --- %s 服务重启失败" % name
            print

    for p in PIDS:
        name, proc, restart = p.get("name"), p.get("proc"), p.get("restart")
        if not is_pid_running(proc):
            print get_time(), " --- %s 进程已经停止运行，发送短信、邮件通知......" % name
            if restart:
                notify("{name:%s, service:%s, cpu:%s%%, ram:%s%%}" % (username, name, cpu, mem),
                       noticeTemplate,
                       "%s 进程已停止，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                subprocess.Popen(restart, shell=True)
                time.sleep(240)
                if is_pid_running(proc):
                    notify("{name:%s, service:%s}" % (username, name), successTemplate,
                           "%s 进程重启成功，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                    print get_time(), " --- %s 进程重启成功" % name
                else:
                    notify("{name:%s, service:%s}" % (username, name), errorTemplate,
                           "%s 进程重启失败，CPU: %s%%，RAM：%s%%" % (name, cpu, mem))
                    print get_time(), " --- %s 进程重启失败" % name
            print


if __name__ == "__main__":
    main()