#!/usr/bin/python
import argparse
import getpass
import json
import re
import requests

from time import sleep
APIserver = 'http://localhost:3000'

# Parse Argument
description = '''
助你快速将网易云歌单中所有vip歌曲保存在另一个歌单中
'''
parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    '-u','--user' , metavar='user', type=str,
    help='网易云帐号（电话号码或邮箱）')
args = parser.parse_args()
if re.search(r'@', args.user):
    email = args.user
else:
    email = None
    phone = args.user

# Login
password = getpass.getpass('密码：')
print('登录...',end='\r')
if email:
    login_result = requests.post(f'{APIserver}/login/email', data={
            'email' : email,
            'password' : password
        })
elif re.match(r'^[0-9]+$', phone):
    login_result = requests.post(f'{APIserver}/login/cellphone', data={
            'phone' : phone,
            'password' : password
        })
else:
    raise ValueError('登录失败，重新试试！')
if not (login_result and login_result.status_code == 200):
    raise requests.ConnectionError('Oops! something wrong, try again later !')
user = login_result.json()
if user['code'] != 200:
    raise ValueError(user['msg'])
print('登录成功！')

cookies = {}
for cookie in user['cookie'].split(';'):
    name,value=cookie.strip().split('=',1)
    cookies[name]=value

# Show user playlists
user_playlists_result = requests.post(f'{APIserver}/user/playlist', data={
        'uid' : user['account']['id'],
        'limit' : 100
    }, cookies=cookies)
print('='*50)
print('|   Playlist id   |   Playlist Name\n' + '='*50)
for playlist in user_playlists_result.json()['playlist']:
    print(f'| {playlist["id"]: 15} | {playlist["name"]}')
    sleep(0.01)
print('='*50, end='\n\n')

# Get more information and create a new playlist
target_id = input('你想要管理哪个歌单？ (id): ')
save_name = input('vip 歌曲将保存歌单的名字: ')
is_privacy= input('要保存为隐私歌单吗？ (yes/no): ')
if is_privacy == 'yes':
    is_privacy = 10
else:
    is_privacy = 0

print('创建歌单中...',end='\r')
create_result = requests.post(f'{APIserver}/playlist/create', data={
        'name' : save_name,
        'privacy' : is_privacy
    }, cookies=cookies)
if create_result.status_code == 200:
    save_id = create_result.json()['playlist']['id']
else:
    raise requests.ConnectionError('Oops! something wrong, try again later !')
print('创建歌单成功！')

# Requests songs in playlist
print('请求目标歌单内容...',end='\r')
request_result = requests.post(f'{APIserver}/playlist/detail', data={
        'id' : target_id
    }, cookies=cookies)
song_ids = []
for tracks in request_result.json()['playlist']['trackIds']:
    song_ids.append(str(tracks['id']))
print('请求目标歌单内容成功！')
sleep(1)

# Judging is it a vip-only song
print('获取所有的vip歌曲...',end='\r')
VIP_song_ids = []
song_ids = ','.join(song_ids)
urls_result = requests.get(f'{APIserver}/song/url?id={song_ids}')
data = urls_result.json()['data']
for x in range(len(data)) :
    if data[x]['url'] == None:
        VIP_song_ids.append(str(data[x]['id']))
print('获取所有的vip歌曲成功！')
# 它这个提纯有点乱杀，算了凑合着用
# if input('但获取到的音乐可能有些没有版权，要提纯吗？(yes/no) : ') == 'yes':
#     VIP_song_ids_tmp = VIP_song_ids.copy()
#     for x in range(len(VIP_song_ids_tmp)):
#         response = requests.get(f'{APIserver}/check/music?id={VIP_song_ids_tmp[x]}')
#         if response.status_code == 404:
#             VIP_song_ids.remove(VIP_song_ids_tmp[x])
#         diff = len(VIP_song_ids_tmp) - len(VIP_song_ids)
#         complete_percent = int(x / len(VIP_song_ids_tmp) * 100)
#         print(f'已检查 {x:4} 首音乐，无版权音乐共 {diff} 首，已完成 {complete_percent}%',end='\r')
#     print('\n提纯完成！')

# Add to new playlist
print('将vip歌曲添加到新歌单...',end='\r')
VIP_song_ids = ','.join(VIP_song_ids)
adding_result = requests.get(f'{APIserver}/playlist/tracks',{
        'op' : 'add',
        'pid': save_id,
        'tracks' : VIP_song_ids
    },cookies = cookies)
print('将vip歌曲添加到新歌单成功！')

# end
print("""
歌曲添加已成功！请查收~~~
谢谢您的使用！
""")
