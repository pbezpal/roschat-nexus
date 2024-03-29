#!/usr/bin/env python3

import os, sys, requests

folders = []
auth = ('jenkins', 'Rosch@tBuild')

for result in os.walk(sys.argv[1]):
    folders.append(result)

for address, dirs, files in folders:
    for filename in files:
        if not sys.argv[2].find('client'):
            url = 'http://10.10.199.217:8080/repository/' + sys.argv[2] + '/' + sys.argv[3] + '/' + filename
            response = requests.put(url, data=open(address + '/' + filename, 'rb'), auth=auth)
        else:
            url = 'http://10.10.199.217:8080/repository/' + sys.argv[2] + '/' + sys.argv[3] + '/' + address.replace(
                sys.argv[1], '') + '/' + filename
            response = requests.put(url, data=open(address + '/' + filename, 'rb'), auth=auth)
