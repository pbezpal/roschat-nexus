#!/usr/bin/env python3

import os,sys,requests
import tarfile

folder_source = 'source'

if not os.path.isdir(folder_source):
    os.mkdir(folder_source)

with tarfile.open('source/' + sys.argv[1] + '.src.tar.gz','w') as tarinfo:
    for name in os.listdir('./'):
        tarinfo.add(name, filter=lambda x: None if x.name.startswith('ormp_nexus') else x)
tarinfo.close()