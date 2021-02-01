##### **本库依赖[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)**

---

# Intro

我这个月开了个网易云的音乐包，月底提醒我要到期了。

我还没下几首歌耶！淦。于是就有了此库。

本库是用来把网易云音乐中某歌单中所有VIP音乐导入到一个新建歌单中。

# Installation

### Linux

首先确保您正确安装并配置了 `git`, `nodejs`, `python`, `python-pip`, `npm`

```shell
cd ~
git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
npm install
cd ..
git clone https://github.com/Qnurye/faked_netease_cloud_music.git
cd faked_netease_cloud_music
pip install -r requirements.txt
```

### Windows

这边建议您用[Arch Linux](https://archlinux.org)呢～

### MacOS

与Linux类似

# Usage

```shell
cd ~
node NeteaseCloudMusicApi/app.js & sleep 5; python faked_netease_cloud_music
python faked_netease_cloud_music
```

或者自己写个脚本

```python
#!/usr/bin/python
from f_ncm import *

if __name__ == '__main__':
    # Login
    username = 'User name'
    password = 'Password'
    user = login(username, password)
    if not user:
        exit(1)
        
    target_id = 123456
    
    save_name = 'new playlist name'
    is_private = False
    save_id = create_playlist(user['cookies'], save_name, is_privacy)

    # Requests songs in playlist
    song_ids = get_songs(target_id, user['cookies'])
    if not song_ids:
        exit(1)

    # Judging is it a vip-only song
    VIP_song_ids = list()
    data = get_urls(song_ids)
    if not data:
        exit(1)
    for song_id in data:
        if data[song_id] is None:
            VIP_song_ids.append(song_id)
    if not add_songs(save_id, VIP_song_ids, user['cookies']):
        exit(1)
```

# How it works ?

根据向网易云官方api `https://music.163.com/api/song/enhance/player/url`请求歌曲 url，VIP歌曲会返回url为`null`。
