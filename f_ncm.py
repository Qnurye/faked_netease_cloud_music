#!/usr/bin/python
import re

from typing import Union

import requests

APIServer = 'http://localhost:3000'


def login(user_name: str, user_password: str) -> Union[bool, dict]:
    """Get a cloud music logged instance

    :param user_name: User account (email or phone number)
    :param user_password: User password
    :return: False if signing in failed, or logged instance if success
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


def get_playlists(uid: Union[int, str], cookies: str = '', limit: int = 30, offset: int = 0) -> Union[bool, dict]:
    """Get user's playlists

    :param uid: User id
    :param limit: Number of items per page
    :param offset: Page number
    :param cookies: Cookies
    :return: False if getting failed, or playlists if success
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
    :return: False if creating failed, or new playlist id if success
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
