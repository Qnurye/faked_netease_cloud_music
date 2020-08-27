#!/usr/bin/python

import getpass

from time import sleep

from f_ncm import *

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
    target_id = input(f'你想要管理哪个歌单？ (id) (默认:{user_playlists[0]["id"]}): ')
    if not target_id:
        target_id = user_playlists[0]['id']

    # Create a new playlist
    save_name = input('vip 歌曲将保存歌单的名字: ')
    is_private = input('要保存为隐私歌单吗？ (yes/no) (默认: no): ')
    if is_private == 'yes':
        is_private = True
    else:
        is_private = False
    print('创建歌单...', end='\r')
    save_id = create_playlist(user['cookies'], save_name, is_private)
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
