# -*- coding: utf-8 -*-
import sys
import io
from utils.log_utils import logger
# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from alist_file_tools import ALIST
import requests
import codecs
import configparser
class AUTO_refreash():
    def __init__(self,config):
        self.url = config['alistconfig']['alist_url']+"/api/fs/dirs"#alist获取文件夹的api /api/admin/storage/load_all
        self.list_url = config['alistconfig']['alist_url']+"/api/fs/list"
        self.alist_token = config['alistconfig']['alist_apikey']
        self.headers = {"Authorization": self.alist_token}#alisttoken
        self.emby_url = config['emby_config']['emby_url']  # 替换为你的 Emby 服务器地址
        self.api_key = config['emby_config']['api_key']  # 替换为你的 API 密钥
        self.libraries_url = config['emby_config']['emby_url']+"/emby/Library/VirtualFolders"#获取文件夹信息
        self.iyuu_token = config['emby_config']['iyuu_token']#iyuuu的token
        #需要监控的alist文件夹
        self.sync_anime_new = config['alistconfig']['sync_anime_new']
        self.sync_movie_new = config['alistconfig']['sync_movie_new']
        self.sync_series = config['alistconfig']['sync_series']
        #需要刷新的emby媒体库
        self.library_anime_new = config['emby_config']['library_anime_new']
        self.library_movie_new = config['emby_config']['library_movie_new']
        self.library_series = config['emby_config']['library_series']

        self.alist = ALIST(config)

    def get_files(self,path):
        return self.alist.get_folder_files(path)
    def get_files_with_modifieddate(self,path):
        names,allfiles = self.alist.get_folder_files(path,need_content=True)
        modified_dates = [item['modified'] for item in allfiles['data']['content']]

        names_with_modified_date = [(name, modified_date) for name, modified_date in zip(names, modified_dates)]

        return names_with_modified_date
    def send_iyuu_message(self, title,content=None):
        token = self.iyuu_token # 替换为你的 IYUU 令牌

        #############格言部分
        # result = self.fetch_data()
        # word = result['result']['word']
        # date = result['result']['date']
        #############


        # 构建请求的 URL
        url = f"https://iyuu.cn/{token}.send"
        # 构建请求体
        if content is not None:
            data = {"text": title,
                    "desp":f'{content}\n\n\n\n'
                           # f'❀✿❁❉❃✾❀✿❁❉❃✾❀✿❁❉\n'
                           # f'{word}\n'
                           # f'{date}\n'
                           # f'❉✿❁❀❃✾❉✿❁❀❃✾❉✿❁❀\n'
                    }
        else:
            data = {"text": title,
                    }

        # 发送 POST 请求
        response = requests.post(url, data=data)
        # 检查请求是否成功
        if response.status_code == 200:
            logger.info("✅消息发送成功！")
        else:
            logger.info(f"消息发送失败，状态码 message send fail,code: {response.status_code}")
    # def monitor_folder_signle(self,monitor_folder,mointor_file_path):
    # # def monitor_folder_signle(self,monitor_folder=self.sync_anime_new ,mointor_file_path='data/last_anime_files.txt'):
    #     def load_last_files(filename):
    #         try:
    #             with open(filename, 'r', encoding='utf-8') as f:
    #                 entries = set()
    #                 for line in f.read().splitlines():
    #                     if ',' in line:
    #                         name, mtime_str = line.split(',', 1)
    #                         try:
    #                             entries.add((name, mtime_str))
    #                         except ValueError:
    #                             logger.info(f"error:读取{filename}失败!")
    #                             continue
    #                 return entries
    #         except FileNotFoundError:
    #             return set()
    #     def save_current_files(filename, entries):
    #         with open(filename, 'w', encoding='utf-8') as f:
    #             for (name, mtime) in entries:
    #                 f.write(f"{name},{mtime}\n")
    #     def calculate_changes(current, last):
    #         # 文件名集合
    #         current_names = {name for (name, _) in current}
    #         last_names = {name for (name, _) in last}
    #         # 新增的文件名（全新文件）
    #         new_names = current_names - last_names
    #         # 删除的文件名（彻底消失的文件）
    #         deleted_names = last_names - current_names
    #         # 可能修改的文件名（存在于两次记录中的文件）
    #         common_names = current_names & last_names
    #         # 详细分析修改事件
    #         modified = set()
    #         for name in common_names:
    #             last_mtime = [mtime for (n, mtime) in last if n == name][0]
    #             current_mtime = [mtime for (n, mtime) in current if n == name][0]
    #             if current_mtime != last_mtime:
    #                 modified.add((name, current_mtime))
    #
    #         for name in modified:
    #             new_names.add(name[0])
    #             logger.info(f'发现修改文件夹：{name[0]},修改时间：{name[1]}')
    #         return new_names, deleted_names, modified
    #     # 读取上次记录的文件及其修改时间
    #     last_anime_files = load_last_files(mointor_file_path)
    #     # 获取当前文件列表及其修改时间
    #     current_anime_files = set(self.get_files_with_modifieddate(monitor_folder))
    #     # 计算各类型事件
    #     new_anime, deleted_anime, modified_anime = calculate_changes(current_anime_files, last_anime_files)
    #     new_anime_folders_with_path = [monitor_folder + '/' + folder for folder in new_anime]
    #     deleted_anime_folders_with_path = [monitor_folder + '/' + folder for folder in deleted_anime]
    #     # 保存当前状态
    #     save_current_files(mointor_file_path, current_anime_files)
    #     dict_files = {
    #                   'new_anime_folders_with_path': new_anime_folders_with_path,
    #                   'deleted_anime_folders_with_path': deleted_anime_folders_with_path,
    #                   'new_anime_files': new_anime,
    #                   'deleted_anime_files': deleted_anime,
    #                   }
    #     return dict_files

    # def mointor_folder_new(self):
    #     anime_monitor_folder = self.sync_anime_new
    #     movie_monitor_folder = self.sync_movie_new
    #     series_monitor_folder = self.sync_series
    #     anime_monitor_filepath = '../data/last_anime_files.txt'
    #     movie_monitor_filepath = '../data/last_movie_files.txt'
    #     series_monitor_filepath = '../data/last_series_files.txt'
    #     mointor_list = [anime_monitor_folder,movie_monitor_folder,series_monitor_folder]
    #     mointor_filepath = [anime_monitor_filepath,movie_monitor_filepath,series_monitor_filepath]
    #     data_dict= {}
    #     for mointor_folder,mointor_filepath in zip(mointor_list,mointor_filepath):
    #         data_dict.update(self.monitor_folder_signle(mointor_folder,mointor_filepath))


    def monitor_folder(self,need_all_filechanges=False):
        def load_last_files(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    entries = set()
                    for line in f.read().splitlines():
                        if ',' in line:
                            name, mtime_str = line.split(',', 1)
                            try:
                                entries.add((name, mtime_str))
                            except ValueError:
                                logger.info(f"error:读取{filename}失败!")
                                continue
                    return entries
            except FileNotFoundError:
                return set()
        def save_current_files(filename, entries):
            with open(filename, 'w', encoding='utf-8') as f:
                for (name, mtime) in entries:
                    f.write(f"{name},{mtime}\n")

        def calculate_changes(current, last):
            # 文件名集合
            current_names = {name for (name, _) in current}
            last_names = {name for (name, _) in last}

            # 新增的文件名（全新文件）
            new_names = current_names - last_names
            # 删除的文件名（彻底消失的文件）
            deleted_names = last_names - current_names
            # 可能修改的文件名（存在于两次记录中的文件）
            common_names = current_names & last_names
            # 详细分析修改事件
            modified = set()
            # new = set()
            # deleted = set()
            # for name in new_names:
            #     new.add((name, [mtime for (n, mtime) in current if n == name][0]))
            # for name in deleted_names:
            #     deleted.add((name, [mtime for (n, mtime) in last if n == name][0]))
            for name in common_names:
                last_mtime = [mtime for (n, mtime) in last if n == name][0]
                current_mtime = [mtime for (n, mtime) in current if n == name][0]
                if current_mtime != last_mtime:
                    modified.add((name, current_mtime))

            for name in modified:
                new_names.add(name[0])
                logger.info(f'😳发现修改文件夹：{name[0]},修改时间：{name[1]}')
            return new_names, deleted_names, modified

        # 读取上次记录的文件及其修改时间
        last_anime_files = load_last_files('data/last_anime_files.txt')
        last_movie_files = load_last_files('data/last_movie_files.txt')
        last_series_files = load_last_files('data/last_series_files.txt')
        # 获取当前文件列表及其修改时间
        current_anime_files = set(self.get_files_with_modifieddate(self.sync_anime_new))
        current_movie_files = set(self.get_files_with_modifieddate(self.sync_movie_new))
        current_series_files = set(self.get_files_with_modifieddate(self.sync_series))

        # 计算各类型事件
        new_anime, deleted_anime, modified_anime = calculate_changes(current_anime_files, last_anime_files)
        new_movie, deleted_movie, modified_movie = calculate_changes(current_movie_files, last_movie_files)
        new_series, deleted_series, modified_series = calculate_changes(current_series_files, last_series_files)

        new_anime_folders_with_path = [self.sync_anime_new + '/' + folder for folder in new_anime]
        new_movie_folders_with_path = [self.sync_movie_new + '/' + folder for folder in new_movie]
        new_series_folders_with_path = [self.sync_series + '/' + folder for folder in new_series]

        deleted_anime_folders_with_path = [self.sync_anime_new + '/' + folder for folder in deleted_anime]
        deleted_movie_folders_with_path = [self.sync_movie_new + '/' + folder for folder in deleted_movie]
        deleted_series_folders_with_path = [self.sync_series + '/' + folder for folder in deleted_series]
        # 保存当前状态
        if need_all_filechanges:
            save_current_files('data/last_anime_files.txt', current_anime_files)
            save_current_files('data/last_movie_files.txt', current_movie_files)
            save_current_files('data/last_series_files.txt', current_series_files)

        dict_files = {
                        'current_anime_files': current_anime_files,
                        'current_movie_files': current_movie_files,
                        'current_series_files': current_series_files,


                      'new_anime_folders_with_path': new_anime_folders_with_path,
                      'new_movie_folders_with_path': new_movie_folders_with_path,
                      'new_series_folders_with_path': new_series_folders_with_path,

                      'deleted_anime_folders_with_path': deleted_anime_folders_with_path,
                      'deleted_movie_folders_with_path': deleted_movie_folders_with_path,
                      'deleted_series_folders_with_path': deleted_series_folders_with_path,

                      'new_anime_files': new_anime,
                      'new_movie_files': new_movie,
                      'new_series_files': new_series,

                      'deleted_anime_files': deleted_anime,
                      'deleted_movie_files': deleted_movie,
                      'deleted_series_files': deleted_series
                      }
        return dict_files

    def fetch_data(self):
        url = "https://whyta.cn/api/tx/one?key=cc8cba0a7069"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()  # 解析JSON响应
            return data
        except requests.exceptions.RequestException as e:
            logger.info(f"❌请求失败: {e}")
            return None
    def emby_refresh_old(self,library_name,name):
        params = {"api_key": self.api_key}
        response = requests.get(self.libraries_url, params=params)
        libraries = response.json()
        library_id = None
        for library in libraries:
            if library["Name"] == library_name:
                library_id = library["ItemId"]
                break

        if library_id:
            # 刷新该媒体库
            refresh_url = f"{self.emby_url}/emby/Library/Refresh"
            data = {"LibraryItemId": library_id}
            refresh_response = requests.post(refresh_url, json=data, params=params)
            if refresh_response.status_code == 204:
                logger.info(f"✅媒体库 '{library_name}' 刷新成功")
                try:
                    self.send_iyuu_message('✅Emby更新提醒',f"[{','.join(name)}]刷新成功")
                except:
                    self.send_iyuu_message('✅Emby更新提醒',f"{name}刷新成功")
            else:
                logger.info(f"刷新失败，状态码: {refresh_response.status_code}")
                self.send_iyuu_message('❌Emby刷新失败',f"刷新失败，状态码: {refresh_response.status_code}")
        else:
            logger.info(f"未找到名为 '{library_name}' 的媒体库")
            self.send_iyuu_message('❌Emby刷新失败',f"未找到名为[{library_name}]的媒体库")
    def emby_refresh(self,library_name,name,status,notify=True):
        params = {"api_key": self.api_key}
        response = requests.get(self.libraries_url, params=params)
        libraries = response.json()
        library_id = None
        for library in libraries:
            if library["Name"] == library_name:
                library_id = library["ItemId"]
                break

        if library_id:
            # 刷新该媒体库
            refresh_url = f"{self.emby_url}/emby/Items/{library_id}/Refresh"
            refresh_params = {
                   'Recursive': 'true',
                   'ImageRefreshMode': 'Default',
                   'MetadataRefreshMode': 'Default',
                   'ReplaceAllImages': 'false',
                   'ReplaceAllMetadata': 'false',
                   'api_key': self.api_key
                    }
            refresh_response = requests.post(refresh_url, params=refresh_params)
            if refresh_response.status_code == 204:
                logger.info(f"✅媒体库 '{library_name}' 刷新成功")
                if notify:
                    try:
                        self.send_iyuu_message('✅Emby更新提醒',f"{status[0]}:[{','.join(name)}]{status[1]}成功")
                    except:
                        self.send_iyuu_message('✅Emby更新提醒',f"{status[0]}:{name}{status[1]}成功!")
            else:
                logger.info(f"刷新失败，状态码: {refresh_response.status_code}")
                self.send_iyuu_message('Emby刷新失败',f"刷新失败，状态码: {refresh_response.status_code}")
        else:
            logger.info(f"未找到名为 '{library_name}' 的媒体库")
            self.send_iyuu_message('Emby刷新失败',f"未找到名为[{library_name}]的媒体库")
def read_config(config_path):
    config = configparser.ConfigParser()
    with codecs.open(config_path, 'r', encoding='utf-8') as f:
        config.read_file(f)
    return config
if __name__ == "__main__":
    # pass
    config = read_config('../config/config.ini')
    auto_refreash = AUTO_refreash(config)
    # auto_refreash.monitor_folder()
    # auto_refreash.send_iyuu_message('测试','更新成功')
    # auto_refreash.refresh_files()
    # files = auto_refreash.get_files('/115_15TB/动漫New')
    # logger.info(files)
    # auto_refreash.emby_refresh('115动漫light','测试文件名')
    auto_refreash.monitor_folder_signle(auto_refreash.sync_anime_new,'../data/last_anime_files.txt')

