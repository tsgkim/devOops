#!/usr/bin/python
# -*- coding: utf-8 -*-
import top.api
import psutil
import time
import ConfigParser
from subprocess import call, STDOUT
import subprocess
import signal
import sys
import json
import os
import requests
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

DEBUG_MODE = False #Won't dispatch SMSs

requests.packages.urllib3.disable_warnings() # http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package

#Parse configuration options
if DEBUG_MODE:
    print "[+] Starting DevOops monitor in debug mode (no SMS will be dispatched)"
else:
    print "[+] Starting DevOops monitor"

print "[-] Loading config file"
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

key = Config.get('ali','key')
secret = Config.get('ali','secret')
username = Config.get('ali','username')
sign = Config.get('ali','sign')
type = Config.get('ali','type')
phone = Config.get('ali','phone')
phone = Config.get('ali','phone')
notice-template = Config.get('ali','notice-template')
success-template = Config.get('ali','success-template')
error-template = Config.get('ali','notice-template')

INTERVAL = int(Config.get('Other', 'Interval'))  #Check every n seconds
FNULL = open(os.devnull, 'w')

#Read service monitoring file
print "[-] Loading Services file"
with open('services.json') as json_data:
    SERVICES = json.load(json_data)

print "[-] Loading Pid file"
with open('pid.json') as pid_data:
    PIDS = json.load(pid_data)

def isServiceRunning(name):
  "Check if a process name is running"
  for proc in psutil.process_iter():
    if proc.name() == name:
      return True
  return False

def isPidRunning(name):
  "Check if a pid name is running"
  res = subprocess.Popen(name,stdout=subprocess.PIPE,shell=True)
  tomcats=res.stdout.readlines()
  counts=len(tomcats)
  if counts == 1:
    return False
  return True

def notify(param, template):
  req = top.api.AlibabaAliqinFcSmsNumSendRequest()
  req.set_app_info(top.appinfo(key, secret))

  req.sms_type = type
  req.sms_free_sign_name = sign
  req.sms_param = param
  req.rec_num = phone
  req.sms_template_code = template
  try :
       resp = req.getResponse()
       dt=datetime.datetime.now()
       print (resp)
  except Exception,e:
       dt=datetime.datetime.now()
       print (e)

  return resp

def main():
    print "[+] Monitoring services...."
    #Inital pass through file to make sure services are running
    for s in SERVICES:
        if not isServiceRunning(s.get("proc")):
          print "[!] At least one service in your services.json is not already running. Please ensure services are already running before starting."
          exit(1)

    for p in PIDS:
        if not isPidRunning(p.get("proc")):
          print "[!] At least one pid in your services.json is not already running. Please ensure pid are already running before starting."
          exit(1)

    while True:
      mem = str(psutil.virtual_memory().percent) #Percent mem used
      cpu = str(psutil.cpu_percent())

      for s in SERVICES:
        name, proc, restart = s.get("name"), s.get("proc"), s.get("restart")
        if not isServiceRunning(proc):
          print "[*] %s has stopped. Dispatching SMS." % name
          if restart:
            notify("{name:%s,service:%s,cpu:%s%%,ram:%s%%}" %(username,name,cpu,mem),notice-template)
            r = call(restart.split(), stdout=FNULL, stderr=STDOUT)
            time.sleep(10)
            if isServiceRunning(proc):
                notify("{name:%s,service:%s}" %(username,name),success-template)
                print "[-] Successfully restarted %s" % name
            else:
                notify("{name:%s,service:%s}" %(username,name),error-template)
                print "[-] Failed to restart %s" % name

      for p in PIDS:
        name, proc, restart = p.get("name"), p.get("proc"), p.get("restart")
        if not isPidRunning(proc):
          print "[*] %s has stopped. Dispatching SMS." % name
          if restart:
            notify("{name:%s,service:%s,cpu:%s%%,ram:%s%%}" %(username,name,cpu,mem),notice-template)
            subprocess.Popen(restart,shell=True)
            time.sleep(120)
            if isPidRunning(proc):
                notify("{name:%s,service:%s}" %(username,name),success-template)
                print "[-] Successfully restarted %s" % name
            else:
                notify("{name:%s,service:%s}" %(username,name),error-template)
                print "[-] Failed to restart %s" % name


      time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
