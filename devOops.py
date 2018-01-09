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

reload(sys)
sys.setdefaultencoding('utf-8')

DEBUG_MODE = False

requests.packages.urllib3.disable_warnings()

if DEBUG_MODE:
    print "[+] Starting DevOops monitor in debug mode (no SMS will be dispatched)"
else:
    print "[+] Starting DevOops monitor"

print "[-] Loading config file"
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

key = Config.get('ali', 'key')
secret = Config.get('ali', 'secret')
username = Config.get('ali', 'username')
sign = Config.get('ali', 'sign')
type = Config.get('ali', 'type')
phone = Config.get('ali', 'phone')
noticeTemplate = Config.get('ali', 'noticeTemplate')
successTemplate = Config.get('ali', 'successTemplate')
errorTemplate = Config.get('ali', 'errorTemplate')

INTERVAL = int(Config.get('Other', 'Interval'))
FNULL = open(os.devnull, 'w')

# Read service monitoring file
print "[-] Loading Services file"
with open('services.json') as json_data:
    SERVICES = json.load(json_data)

print "[-] Loading Pid file"
with open('pid.json') as pid_data:
    PIDS = json.load(pid_data)


def is_service_running(name):
    """Check if a process name is running"""
    for proc in psutil.process_iter():
        if proc.name() == name:
            return True
    return False


def is_pid_running(name):
    """Check if a pid name is running"""
    res = subprocess.Popen(name, stdout=subprocess.PIPE, shell=True)
    tomcats = res.stdout.readlines()
    counts = len(tomcats)
    if counts == 1:
        return True
    return False


def notify(param, template):
    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(key, secret))

    req.sms_type = type
    req.sms_free_sign_name = sign
    req.sms_param = param
    req.rec_num = phone
    req.sms_template_code = template
    try:
        resp = req.getResponse()
        print (resp)
    except Exception, e:
        print (e)

    return resp


def main():
    print "[+] Monitoring services...."
    
    for s in SERVICES:
        if not is_service_running(s.get("proc")):
            print "[!] must all service in your services.json is already running. Please ensure all services are " \
                  "already running before starting. "
            exit(1)

    for p in PIDS:
        if not is_pid_running(p.get("proc")):
            print "[!] must all pid in your pid.json is already running. Please ensure all pid are already running " \
                  "before starting. "
            exit(1)

    while True:
        mem = str(psutil.virtual_memory().percent)  # Percent mem used
        cpu = str(psutil.cpu_percent())

        for s in SERVICES:
            name, proc, restart = s.get("name"), s.get("proc"), s.get("restart")
            if not is_service_running(proc):
                print "[*] %s has stopped. Dispatching SMS." % name
                if restart:
                    notify("{name:%s,service:%s,cpu:%s%%,ram:%s%%}" % (username, name, cpu, mem), noticeTemplate)
                    r = call(restart.split(), stdout=FNULL, stderr=STDOUT)
                    time.sleep(10)
                    if is_service_running(proc):
                        notify("{name:%s,service:%s}" % (username, name), successTemplate)
                        print "[-] Successfully restarted %s" % name
                    else:
                        notify("{name:%s,service:%s}" % (username, name), errorTemplate)
                        print "[-] Failed to restart %s" % name

        for p in PIDS:
            name, proc, restart = p.get("name"), p.get("proc"), p.get("restart")
            if not is_pid_running(proc):
                print "[*] %s has stopped. Dispatching SMS." % name
                if restart:
                    notify("{name:%s,service:%s,cpu:%s%%,ram:%s%%}" % (username, name, cpu, mem), noticeTemplate)
                    subprocess.Popen(restart, shell=True)
                    time.sleep(120)
                    if is_pid_running(proc):
                        notify("{name:%s,service:%s}" % (username, name), successTemplate)
                        print "[-] Successfully restarted %s" % name
                    else:
                        notify("{name:%s,service:%s}" % (username, name), errorTemplate)
                        print "[-] Failed to restart %s" % name

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
