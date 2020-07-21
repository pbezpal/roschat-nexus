#!/usr/bin/env python3

import os,sys,requests
import tarfile

with tarfile.open(sys.argv[1] + '.src.tar.gz','w') as tarinfo:
    for name in os.listdir('./'):
        tarinfo.add(name, filter=lambda x: None if x.name.startswith('ormp_nexus') else x)
tarinfo.close()