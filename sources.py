#!/usr/bin/env python3

import os
import os.path
import tarfile

import requests

try:
    import colorama
except ImportError:
    print('Lib colorama not find, installing...')
    os.system('pip3 install colorama')


class SourceCode:
    folder_source: str = 'source'
    git_url_mc_front: str = 'http://10.10.199.12:7990/scm/develop/managment-system-client.git'
    git_url_mc_back: str = 'http://10.10.199.12:7990/scm/develop/managment-system-server.git'
    git_url_server: str = 'http://10.10.199.12:7990/scm/develop/roschat-server.git'
    git_url_db: str = 'http://10.10.199.12:7990/scm/develop/db_server.git'
    git_url_sip: str = 'http://10.10.199.12:7990/scm/develop/sip_server.git'
    git_url_snmp: str = 'http://10.10.199.12:7990/scm/develop/managment-system-snmp.git'
    git_url_client: str = 'http://10.10.199.12:7990/scm/develop/roschat-client.git'
    git_url_services: str = 'http://10.10.199.12:7990/scm/develop/roschat-services.git'
    tar_file: str = None
    url_nexus_repo: str = 'http://10.10.199.217:8080/repository/roschat-sources'

    def __init__(self, auth, branch, repository, path):
        self.auth = auth
        self.branch = branch
        self.repository = repository
        self.path = path

    def create_source_directory(self):
        if not os.path.isdir(self.folder_source):
            os.mkdir(self.folder_source)

    def create_tarfile(self):
        self.tar_file = self.folder_source + '/' + self.repository + '.src.tar.gz'
        with tarfile.open(self.tar_file, 'w') as tarinfo:
            tarinfo.add(self.folder_source, arcname=os.path.basename(self.folder_source))
        tarinfo.close()

    def upload_source_code(self, url_nexus):
        self.create_tarfile()
        print('\r\nUpload source code to Nexus... ', sep="; ", end="")
        response = requests.put(url_nexus, data=open(self.tar_file, 'rb'), auth=self.auth)
        if response.status_code is 201:
            print(colorama.Fore.GREEN + 'SUCCESS')
        else:
            print(colorama.Fore.RED + 'FAILED')

    def upload_source_to_nexus(self):
        url_nexus: str = None
        os.system("rm -rf " + self.folder_source)
        self.create_source_directory()
        if self.repository == 'roschat-ms':
            os.system('git clone -b ' + self.branch + ' ' + self.git_url_mc_front + ' ' + self.folder_source)
            url_nexus = self.url_nexus_repo + '/roschat-ms-front/' + self.path + '/' + self.repository + '.src.tar.gz '
            self.upload_source_code(url_nexus)
            os.system("rm -rf " + self.folder_source)
            self.create_source_directory()
            os.system('git clone -b ' + self.branch + ' ' + self.git_url_mc_back + ' ' + self.folder_source)
            url_nexus = self.url_nexus_repo + '/roschat-ms-back/' + self.path + '/' + self.repository + '.src.tar.gz '
            self.upload_source_code(url_nexus)
        else:
            if self.repository == 'roschat-server':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_server + ' ' + self.folder_source)
            elif self.repository == 'roschat-snmp':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_snmp + ' ' + self.folder_source)
            elif self.repository == 'roschat-db':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_db + ' ' + self.folder_source)
            elif self.repository == 'roschat-sip':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_sip + ' ' + self.folder_source)
            elif self.repository == 'roschat-services':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_services + ' ' + self.folder_source)
            elif self.repository == 'roschat-web-client' or self.repository == 'roschat-client':
                os.system('git clone -b ' + self.branch + ' ' + self.git_url_client + ' ' + self.folder_source)
            url_nexus = self.url_nexus_repo + '/' + self.repository + '/' + self.path + '/' + self.repository + '.src.tar.gz '
            self.upload_source_code(url_nexus)
