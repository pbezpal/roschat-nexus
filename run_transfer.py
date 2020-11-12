#!/usr/bin/env python3

import os
import requests
import getpass
from transfer_assets import TransferAssets

try:
    import colorama
except ImportError:
    print('Lib colorama not find, installing...')
    os.system('pip3 install colorama')

repository: str = None
repos: list = []
assets: list = []
paths: list = []
rpms: list = []
urls: list = []
path: str = None
usrl: str = None
temp_dir: str = 'temp'
base_url: str = 'http://10.10.199.217:8080'
repo_response: requests = None
auth: list = None

colorama.init()

print('\r\nPlease, enter login and password for auth to nexus')
i = 0
while i < 3:
    login = input('\r\nLogin: ')
    password = getpass.getpass('Password: ')
    auth = (login, password)
    repo_response = requests.get(base_url + '/service/rest/v1/repositories', auth=auth)
    if repo_response.status_code == 401:
        print('\r\nWrong login or password, please try again')
    else:
        break
    i = i + 1
else:
    print('\r\nYou entered the wrong password 3 times. Permission denied.')
    exit(0)
json_repos = repo_response.json()
while True:
    i = 1
    print('\r\nList projects: \n')
    for item in json_repos:
        if not item['name'].find('pre-release') == -1:
            repo = item['name'].replace('.pre-release', '')
            if not repo == 'roschat':
                repos.append(repo)
                print(str(i) + '. ' + repo)
                i = i + 1

    print('q: Quit')
    project = input('\r\nSelect project (enter number): ')
    if project.isnumeric():
        repository = repos[int(project) - 1]
        break
    elif project == 'q':
        exit(0)

transfer = TransferAssets(base_url, repository, auth, temp_dir)

if os.path.exists(temp_dir):
    transfer.delete_temp_folder()

if not repository == 'roschat-client':
    transfer.menu_server()
else:
    transfer.menu_client()
