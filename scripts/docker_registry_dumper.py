#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

this is a modified version of DokerRegistryDumper from SyzikSecu 
at `https://github.com/Syzik/DockerRegistryGrabber`

the script is used to enumerate all the docker images present on a docker registry
instance and dump all the blobs present
my edits add token authorizations on top of the already present username:password format method
"""

import requests
import argparse
import re
import json
import sys
import os
from base64 import b64encode
import urllib3
from rich.console import Console
from rich.theme import Theme
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
req = requests.Session()

http_proxy = ""
os.environ['HTTP_PROXY'] = http_proxy
os.environ['HTTPS_PROXY'] = http_proxy


custom_theme = Theme({
    "OK": "bright_green",
    "NOK": "red3"
})


def manageArgs():
    parser = argparse.ArgumentParser()
    # Positionnal args
    parser.add_argument("url", help="URL")
    # Optional args
    parser.add_argument("-p", dest='port', metavar='port', type=int,
                        default=5000, help="port to use (default : 5000)")
    # Authentification
    auth = parser.add_argument_group("Authentication")
    auth.add_argument('-U', dest='username', type=str,
                      default="", help='Username')
    auth.add_argument('-P', dest='password', type=str,
                      default="", help='Password')
    auth.add_argument('-T', dest='token', type=str,
                      default="", help='Bearer token')
    # Args Action en opposition
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dump", metavar="DOCKERNAME",
                        dest='dump', type=str,  help="DockerName")
    action.add_argument("--list", dest='list', action="store_true")
    action.add_argument("--dump_all", dest='dump_all', action="store_true")
    args = parser.parse_args()
    return args


def printList(dockerlist):
    for element in dockerlist:
        if element:
            console.print(f"[+] {element}", style="OK")
        else:
            console.print(f"[-] No Docker found", style="NOK")


def tryReq(url, username=None, password=None, token=None):
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        elif username and password:
            headers['Authorization'] = f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'

        if headers:
            r = req.get(url, verify=False, headers=headers)
        else:
            r = req.get(url, verify=False)

        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        console.print(f"Http Error: {errh}", style="NOK")
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        console.print(f"Error Connecting : {errc}", style="NOK")
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        console.print(f"Timeout Error : {errt}", style="NOK")
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        console.print(
            f"Dunno what happend but something fucked up {err}", style="NOK")
        sys.exit(1)
    return r


def createDir(directoryName):
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)


def downloadSha(url, port, docker, sha256, username=None, password=None, token=None):
    createDir(docker)
    directory = f"./{docker}/"
    for sha in sha256:
        filenamesha = f"{sha}.tar.gz"
        geturl = f"{url}:{str(port)}/v2/{docker}/blobs/sha256:{sha}"
        r = tryReq(geturl, username, password, token)
        if r.status_code == 200:
            console.print(f"    [+] Downloading : {sha}", style="OK")
            with open(directory+filenamesha, 'wb') as out:
                for bits in r.iter_content():
                    out.write(bits)


def getBlob(docker, url, port, username=None, password=None, token=None):
    tags = f"{url}:{str(port)}/v2/{docker}/tags/list"
    rr = tryReq(tags, username, password, token)
    data = rr.json()
    image = data["tags"][0]
    url = f"{url}:{str(port)}/v2/{docker}/manifests/"+image+""
    r = tryReq(url, username, password, token)
    blobSum = []
    if r.status_code == 200:
        regex = re.compile('blobSum')
        for aa in r.text.splitlines():
            match = regex.search(aa)
            if match:
                blobSum.append(aa)
        if not blobSum:
            console.print(f"[-] No blobSum found", style="NOK")
            sys.exit(1)
        else:
            sha256 = []
            cpt = 1
            for sha in blobSum:
                console.print(f"[+] BlobSum found {cpt}", end='\r', style="OK")
                cpt += 1
                a = re.split(':|,', sha)
                sha256.append(a[2].strip("\""))
            print()
            return sha256


def enumList(url, port, username=None, password=None, token=None, checklist=None):
    url = f"{url}:{str(port)}/v2/_catalog"
    try:
        r = tryReq(url, username, password, token)
        if r.status_code == 200:
            catalog2 = re.split(':|,|\n ', r.text)
            catalog3 = []
            for docker in catalog2:
                dockername = docker.strip("[\'\"\n]}{")
                catalog3.append(dockername)
        printList(catalog3[1:])
        return catalog3
    except:
        exit()


def dump(args):
    sha256 = getBlob(args.dump, args.url, args.port,
                     args.username, args.password, args.token)
    console.print(f"[+] Dumping {args.dump}", style="OK")
    downloadSha(args.url, args.port, args.dump, sha256,
                args.username, args.password, args.token)


def dumpAll(args):
    dockerlist = enumList(args.url, args.port,
                          args.username, args.password, args.token)
    for docker in dockerlist[1:]:
        sha256 = getBlob(docker, args.url, args.port,
                         args.username, args.password, args.token)
        console.print(f"[+] Dumping {docker}", style="OK")
        downloadSha(args.url, args.port, docker, sha256,
                    args.username, args.password, args.token)


def options():
    args = manageArgs()
    if args.list:
        enumList(args.url, args.port, args.username, args.password, args.token)
    elif args.dump_all:
        dumpAll(args)
    elif args.dump:
        dump(args)


if __name__ == '__main__':
    print()
    urllib3.disable_warnings()
    console = Console(theme=custom_theme)
    options()
