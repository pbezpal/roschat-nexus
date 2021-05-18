#!/usr/bin/env python3

import os
import sys
import requests
import shutil
from sources import SourceCode

try:
    import colorama
except ImportError:
    print('Lib colorama not find, installing...')
    os.system('pip3 install colorama')

try:
    import wget
except ImportError:
    print('Lib wget not find, installing...')
    os.system('pip3 install wget')


def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


class TransferAssets:
    url_list: list = []
    rpm_list: list = []
    path_list: list = []
    node_list: list = []
    client_rpm_list: list = []
    client_deb_list: list = []
    client_win_32_list: list = []
    client_win_64_list: list = []
    client_mac_list: list = []
    select_rpm: str = None
    select_node_rpm: str = None
    select_path: str = None
    select_url: str = None
    continuationToken: str = ""
    branch: str = None
    folder_source: str = 'source'
    git_url: str = 'http://10.10.199.12:7990/scm/develop/'
    source_code: SourceCode = None

    def __init__(self, base_url, repository, type, auth, temp_dir):
        self.base_url = base_url
        self.repository = repository
        self.type = type
        self.auth = auth
        self.temp_dir = temp_dir

    def delete_temp_folder(self):
        try:
            shutil.rmtree(self.temp_dir)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def delete_asset(self, url: str, status: int):
        del_response = requests.delete(url, auth=self.auth)
        if del_response.status_code == status:
            print(colorama.Fore.GREEN + 'Success\r\n')
        else:
            print(colorama.Fore.GREEN + 'FAILED\r\n')
            exit(0)

    def get_assets(self, token):
        if token == "":
            data_response = requests.get(
                self.base_url + '/service/rest/v1/assets?repository=' + self.repository + self.type,
                auth=self.auth)
            if data_response.status_code == 200:
                json_data = data_response.json()
                self.continuationToken = json_data['continuationToken']
                return json_data
            else:
                print(colorama.Fore.RED + 'Can\'t get data from repository ' + self.repository + self.type)
                exit(0)
        else:
            data_response = requests.get(
                self.base_url + '/service/rest/v1/assets?repository=' + self.repository + self.type + '&continuationToken=' + token,
                auth=self.auth)
            if data_response.status_code == 200:
                json_data = data_response.json()
                self.continuationToken = json_data['continuationToken']
                return json_data
            else:
                print(colorama.Fore.RED + 'Can\'t get data from repository ' + self.repository + self.type)
                exit(0)

    @staticmethod
    def get_asset(data_name, url, folder):
        print('\r\nDownload ' + data_name + ' from repository... ', sep="; ", end="")
        if not os.path.exists(folder):
            os.makedirs(folder)
        data = wget.download(url, out=folder, bar=bar_progress)
        if not data is None:
            print(colorama.Fore.GREEN + 'SUCCESS\r\n')
        else:
            print(colorama.Fore.RED + 'FAILED\r\n')
            exit(0)

    def upload_assets_to_release(self):
        dir_name: list = []

        if self.repository == 'roschat-client':
            for data in os.walk(self.temp_dir):
                dir_name.append(data)

            for address, dirs, files in dir_name:
                for filename in files:
                    print(
                        '\r\nStart transfer ' + filename + ' from '
                                                           '' + self.repository + self.type + ' to ' + self.repository + '.release... ', sep="; ", end="")
                    url_release: str = self.base_url + '/repository/' \
                                                       '' + self.repository + '.release/' + self.select_path + '' \
                                                                                                               '' + address.replace(
                        self.temp_dir, '') + '/' + filename
                    url_delete: str = self.base_url + '/repository/' \
                                                      '' + self.repository + self.type + '/' + self.select_path + '' \
                                                                                                                  '' + address.replace(
                        self.temp_dir, '') + '/' + filename
                    push_response = requests.put(url_release, data=open(address + '/' + filename, 'rb'), auth=self.auth)

                    if push_response.status_code == 201:
                        print(colorama.Fore.GREEN + 'Success\r\n')
                        print('\r\nDelete ' + filename + ' from ' + self.repository + self.type + '...')
                        self.delete_asset(url_delete, 204)
                    else:
                        print(colorama.Fore.RED + 'FAILED\r\n')
                        self.delete_temp_folder()
                        exit(0)
        else:
            for data in os.listdir(self.temp_dir):
                print('\r\nStart transfer ' + data + ' from ' + self.repository + self.type + ' to '
                                                                                              '' + self.repository + '.release... ', sep="; ", end="")
                url_release: str = self.base_url + '/repository/' \
                                                   '' + self.repository + '.release/' \
                                                                          '' + self.select_path + '/' + data
                url_delete: str = self.base_url + '/repository/' \
                                                  '' + self.repository + self.type + '/' \
                                                                                     '' + self.select_path + '/' + data
                push_response = requests.put(url_release,
                                             data=open(self.temp_dir + '/' + data, 'rb'),
                                             auth=self.auth)
                if push_response.status_code == 200:
                    print(colorama.Fore.GREEN + 'Success\r\n')
                    print('\r\nDelete ' + data + ' from ' + self.repository + self.type + '... \r\n')
                    self.delete_asset(url_delete, 200)
                else:
                    print(colorama.Fore.RED + 'FAILED\r\n')
                    self.delete_temp_folder()
                    exit(0)

        self.delete_temp_folder()

    def server_menu(self, i, items):
        for item in items['items']:
            if not item['path'].find('rpm') == -1:
                if item['path'].find('node-modules') == -1:
                    self.path_list.append(item['path'].partition('/')[0])
                    self.url_list.append(item['downloadUrl'])
                    index = item['path'].find('/')
                    rpm = item['path'][index:]
                    rpm = rpm[1:]
                    self.rpm_list.append(rpm)
                    print(str(i) + '. ' + rpm.replace(self.repository + '-', '').replace('.x86_64.rpm', ''))
                    i = i + 1

        if len(self.rpm_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        return i

    def menu_server(self):
        while True:
            i = 1
            print('\r\nList version: \n')
            while not self.continuationToken is None:
                i = self.server_menu(i, self.get_assets(self.continuationToken))

            print('q: Quit')

            ver = input('\r\nSelect version (enter number): ')
            if ver.isnumeric():
                if 0 < int(ver) <= i:
                    ver = int(ver) - 1
                    break
            elif ver == 'q':
                exit(0)

        self.select_rpm = self.rpm_list[ver]
        self.select_path = self.path_list[ver]
        self.select_url = self.url_list[ver]
        self.branch = self.select_rpm.replace(self.repository + "-", "").replace('.x86_64.rpm', '').rpartition('-')[0]
        self.source_code = SourceCode(self.auth, self.branch, self.repository, self.select_path)
        self.source_code.upload_source_to_nexus()

        self.get_asset(self.select_rpm, self.select_url, self.temp_dir)
        if self.repository == 'roschat-server':
            self.select_node_rpm = self.select_rpm.replace(self.repository, 'roschat-node-modules')
            self.get_asset(self.select_node_rpm,
                           self.select_url.replace(self.select_rpm, self.select_node_rpm),
                           self.temp_dir)
        self.upload_assets_to_release()

    def client_menu(self, i, items):
        for item in items['items']:
            index = item['path'].rfind('/')
            if not item['path'].find('deb') == -1:
                client = item['path'][index:].replace('/', '').replace('roschat_', '').replace('_amd64.deb', '')
                self.path_list.append(item['path'].partition('/')[0])
                print(str(i) + '. ' + client)
                self.client_deb_list.append(item['path'][index:].replace('/', ''))
                self.client_deb_list.append(item['downloadUrl'])
                i = i + 1
            elif not item['path'].find('rpm') == -1:
                self.client_rpm_list.append(item['path'][index:].replace('/', ''))
                self.client_rpm_list.append(item['downloadUrl'])
            elif not item['path'].find('ia32.exe') == -1:
                self.client_win_32_list.append(item['path'][index:].replace('/', ''))
                self.client_win_32_list.append(item['downloadUrl'])
            elif not item['path'].find('x64.exe') == -1:
                self.client_win_64_list.append(item['path'][index:].replace('/', ''))
                self.client_win_64_list.append(item['downloadUrl'])
            elif not item['path'].find('dmg') == -1:
                self.client_mac_list.append(item['path'][index:].replace('/', ''))
                self.client_mac_list.append(item['downloadUrl'])

        if len(self.client_deb_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        elif len(self.client_rpm_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        elif len(self.client_win_32_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        elif len(self.client_win_64_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        elif len(self.client_mac_list) == 0:
            print(colorama.Fore.RED + 'No data for transfer')
            exit(0)
        return i

    def menu_client(self):
        linux_dir: str = self.temp_dir + '/linux'
        win_32_dir: str = self.temp_dir + '/windows/ia32/'
        win_64_dir: str = self.temp_dir + '/windows/x64/'
        mac_dir = self.temp_dir + '/macos/x64/'

        while True:
            i = 1
            print('\r\nList version:\r\n')
            while not self.continuationToken is None:
                i = self.client_menu(i, self.get_assets(self.continuationToken))

            print('q: Quit')
            ver = input('\r\nSelect version (enter number): ')
            if ver.isnumeric():
                if 0 < int(ver) <= i:
                    ver = int(ver) - 1
                    break
            elif ver == 'q':
                exit(0)

        self.select_path = self.path_list[ver]

        if ver > 1:
            ver = ver + 3

        self.branch = \
        self.client_deb_list[ver].replace('/', '').replace('roschat_', '').replace('_amd64.deb', '').rpartition('.')[0]
        self.select_path = self.path_list[ver]
        self.source_code = SourceCode(self.auth, self.branch, self.repository, self.select_path)
        self.source_code.upload_source_to_nexus()

        self.get_asset(self.client_deb_list[ver],
                       self.client_deb_list[ver + 1],
                       linux_dir)
        self.get_asset(self.client_rpm_list[ver],
                       self.client_rpm_list[ver + 1],
                       linux_dir)
        self.get_asset(self.client_win_32_list[ver],
                       self.client_win_32_list[ver + 1],
                       win_32_dir)
        self.get_asset(self.client_win_64_list[ver],
                       self.client_win_64_list[ver + 1],
                       win_64_dir)
        self.get_asset(self.client_mac_list[ver],
                       self.client_mac_list[ver + 1],
                       mac_dir)

        self.upload_assets_to_release()
