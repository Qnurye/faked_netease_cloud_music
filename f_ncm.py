#!/usr/bin/python
import getpass
import re
from typing import Union

import requests

from time import sleep

APIServer = 'http://localhost:3000'


def login(user_name: str, user_password: str) -> Union[bool, dict]:
    """Get a cloud music logged instance

    :param user_name: User account (email or phone number)
    :param user_password: User password
    :return: False if sign in failed, or logged instance if success
    """
    if re.search(r'@', user_name):
        # This will login via email
        login_result = requests.post(f'{APIServer}/login/email', data=dict(email=user_name, password=user_password))
    elif re.match(r'^[0-9]+$', user_name):
        login_result = requests.post(f'{APIServer}/login/cellphone', data=dict(phone=user_name, password=user_password))
    else:
        return False

    if not (login_result and login_result.status_code == 200):
        return False

    login_result = login_result.json()
    if login_result['code'] != 200:
        return False

    login_result['cookies'] = dict()
    for cookie in login_result['cookie'].split(';'):
        name, value = cookie.strip().split('=', 1)
        login_result['cookies'][name] = value
    login_result['uid'] = login_result['account']['id']

    return login_result


def get_playlists(uid: int, cookies: str = '', limit: int = 30, offset: int = 0) -> Union[bool, dict]:
    """Get user's playlists

    :param uid: User id
    :param limit: Number of items per page
    :param offset: Page number
    :param cookies: Cookies
    :return: False if get failed, or playlists if success
    """
    response = requests.post(f'{APIServer}/user/playlist', data={
        'uid': uid,
        'limit': limit,
        'offset': offset
    }, cookies=cookies)
    if not (response and response.status_code == 200 and response.json()['playlist']):
        return False
    return response.json()['playlist']


def create_playlist(cookies: str, playlist_name: str = 'Untitled playlist', private: bool = False) -> Union[bool, int]:
    """Create a new playlist

    :param cookies: Logged cookies
    :param playlist_name: New playlist name
    :param private: Is new playlist private or not
    :return: False if create failed, or new playlist id if success
    """
    if private:
        private = 10
    else:
        private = 0
    create_result = requests.post(f'{APIServer}/playlist/create', data={
        'name': playlist_name,
        'privacy': private
    }, cookies=cookies)
    if create_result.status_code == 200:
        return create_result.json()['playlist']['id']
    else:
        return False


def get_songs(playlist_id: int, cookies: str = '') -> Union[bool, list]:
    """Get songs from a playlist

    :param playlist_id: playlist id
    :param cookies: cookies
    :return: False if failed, or a list of song ids if success
    """
    response = requests.post(f'{APIServer}/playlist/detail', data={
        'id': playlist_id
    }, cookies=cookies)
    if not (response and response.status_code == 200):
        return False
    ids = []
    for tracks in response.json()['playlist']['trackIds']:
        ids.append(str(tracks['id']))
    return ids


def get_urls(ids: list) -> Union[bool, dict]:
    """Get urls from a list of song ids

    :param ids: A list of song ids
    :return: False if failed, or a dict like {song_id: song_url}
    """
    ids = ','.join(ids)
    response = requests.get(f'{APIServer}/song/url?id={ids}')
    if not (response and response.status_code == 200):
        return False
    urls_result = dict()
    response = response.json()['data']
    for song in response:
        urls_result[song['id']] = song['url']
    return urls_result


def add_songs(playlist_id: int, ids: list, cookies: str) -> bool:
    for _x in range(len(ids)):
        ids[_x] = str(ids[_x])
    ids = ','.join(ids)
    adding_result = requests.get(f'{APIServer}/playlist/tracks', {
        'op': 'add',
        'pid': playlist_id,
        'tracks': ids
    }, cookies=cookies)
    if not (adding_result and adding_result.status_code == 200):
        return False
    return adding_result.json()['body']['trackIds']


if __name__ == '__main__':
    # Login
    username = input('用户名（邮箱或手机号）：')
    password = getpass.getpass('密码：')
    print('登录...', end='\r')
    user = login(username, password)
    if not user:
        print('登录失败！')
        exit(1)
    print('登录成功！')

    # Show user playlists
    user_playlists = get_playlists(user['uid'], user['cookies'], 50)
    if not user_playlists:
        print('获取用户歌单失败')
    print('=' * 50)
    print('|   Playlist id   |   Playlist Name\n' + '=' * 50)
    for playlist in user_playlists:
        print(f'| {playlist["id"]: 15} | {playlist["name"]}')
        sleep(0.01)
    print('=' * 50, end='\n\n')
    target_id = int(input('你想要管理哪个歌单？ (id): '))

    # Create a new playlist
    save_name = input('vip 歌曲将保存歌单的名字: ')
    is_privacy = input('要保存为隐私歌单吗？ (yes/no): ')
    if is_privacy == 'yes':
        is_privacy = True
    else:
        is_privacy = False
    print('创建歌单...', end='\r')
    save_id = create_playlist(user['cookies'], save_name, is_privacy)
    if not save_id:
        print('创建歌单失败！')
        exit(1)
    print('创建歌单成功！')

    # Requests songs in playlist
    print('请求目标歌单内容...', end='\r')
    song_ids = get_songs(target_id, user['cookies'])
    if not song_ids:
        print('请求目标歌单内容失败！')
        exit(1)
    print('请求目标歌单内容成功！')
    sleep(1)

    # Judging is it a vip-only song
    print('获取所有的vip歌曲...', end='\r')
    VIP_song_ids = list()
    data = get_urls(song_ids)
    if not data:
        print('获取所有的vip歌曲失败！')
        exit(1)
    for song_id in data:
        if data[song_id] is None:
            VIP_song_ids.append(song_id)
    print('获取所有的vip歌曲成功！')

    # Add to new playlist
    print('将vip歌曲添加到新歌单...', end='\r')
    if not add_songs(save_id, VIP_song_ids, user['cookies']):
        print('将vip歌曲添加到新歌单失败！')
        exit(1)
    print('将vip歌曲添加到新歌单成功！')

    # end
    print("""
    歌曲添加已成功！请查收~~~
    谢谢您的使用！
    """)
