import json
import os
import difflib
import re
import traceback
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO


def load_songs(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def find_song_id(song_title):
    filename = 'src/static/chu/data/sdvxin_chuni.json'
    songs = load_songs(filename)

    # 尝试直接匹配
    if song_title in songs:
        return songs[song_title]

    # 尝试模糊匹配
    close_matches = difflib.get_close_matches(song_title, songs.keys(), n=1, cutoff=0.8)
    if close_matches:
        return songs[close_matches[0]]

    # 正则表达式，用于删除特定的后缀
    pattern = re.compile(r' -.*?-|～.*?～')
    
    # 移除特定的后缀并再次尝试模糊匹配
    cleaned_title = pattern.sub('', song_title).strip()
    close_matches = difflib.get_close_matches(cleaned_title, songs.keys(), n=1, cutoff=0.9)
    if close_matches:
        return songs[close_matches[0]]

    # 尝试匹配标题中的一部分
    parts = re.split(r' -|- |～| ～', song_title)
    for part in parts:
        if part in songs:
            return songs[part]

    return None # 没有找到匹配项


def official_id_to_sdvx_id(official_id):
    # 从music.json文件加载歌曲
    json_filename = "src/static/chu/data/music.json"
    with open(json_filename, 'r', encoding='utf-8') as file:
        json_songs = json.load(file)

    song_title = None
    # 从music.json中使用ID找到对应的曲目标题
    for song in json_songs:
        if str(song["id"]) == str(official_id):
            song_title = song["title"]
            break

    if song_title is None:
        return None

    # 使用之前定义的查找方法找到对应的sdvxin_chuni.json中的ID
    return find_song_id(song_title)


# setup proxy
#PROXY = {'http': 'http://localhost:7890', 'https': 'http://localhost:7890'}
proxy_url = 'http://localhost:7895'


async def download_and_merge_images(musicid, sdvxid, difficulty):
    # 构建URL
    prefix = sdvxid[:2]
    
    base_url = f"https://sdvx.in/chunithm/{prefix}/bg/{sdvxid}bg.png"
    if difficulty == 'master':
        obj_url = f"https://sdvx.in/chunithm/{prefix}/obj/data{sdvxid}mst.png"
    else:
        obj_url = f"https://sdvx.in/chunithm/{prefix}/obj/data{sdvxid}{difficulty[:3]}.png"
    bar_url = f"https://sdvx.in/chunithm/{prefix}/bg/{sdvxid}bar.png"

    # 下载图像
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, proxy=proxy_url) as response:
            base_image = Image.open(BytesIO(await response.read()))
        async with session.get(obj_url, proxy=proxy_url) as response:
            obj_image = Image.open(BytesIO(await response.read()))
        async with session.get(bar_url, proxy=proxy_url) as response:
            bar_image = Image.open(BytesIO(await response.read()))

    # 创建纯黑背景
    black_image = Image.new("RGBA", base_image.size, (0, 0, 0, 255))

    # 检查图像模式
    if obj_image.mode != black_image.mode:
        print("警告：图像模式不匹配")
        obj_image = obj_image.convert("RGBA")
        bar_image = bar_image.convert("RGBA")
        base_image = base_image.convert("RGBA")

    # 检查图像大小
    if black_image.size != obj_image.size:
        print("警告：图像大小不匹配")
        obj_image = obj_image.resize(base_image.size)
        bar_image = bar_image.resize(base_image.size)

    print(f"base_image size: {base_image.size}, mode: {base_image.mode}")
    print(f"obj_image size: {obj_image.size}, mode: {obj_image.mode}")
    print(f"bar_image size: {bar_image.size}, mode: {bar_image.mode}")
    print(f"black_image size: {black_image.size}, mode: {black_image.mode}")

    # 合并图像
    merged_image = Image.alpha_composite(black_image, base_image)
    merged_image = Image.alpha_composite(merged_image, obj_image)
    merged_image = Image.alpha_composite(merged_image, bar_image)

    # 保存图像
    directory = os.path.join("charts", "chunithm", str(musicid))
    os.makedirs(directory, exist_ok=True)
    output_path = os.path.join(directory, f"{difficulty}.jpg")
    # 保存图像为JPEG格式，并选择一个质量设置
    merged_image = merged_image.convert('RGB') # 将图像转换为RGB，因为JPEG不支持透明度
    merged_image.save(output_path, 'JPEG', quality=60) # 你可以调整质量参数来达到所需的文件大小
    
    print(f"图像已保存到 {output_path}")
    return output_path


async def get_chunithm_chart(musicid, difficulty):
    print(musicid, difficulty)
    local_path = os.path.join("charts", "chunithm", str(musicid), f"{difficulty}.jpg")
    
    if os.path.exists(local_path):
        return get_song_info(musicid) + (local_path,)

    try:
        sdvxid = official_id_to_sdvx_id(musicid)
        if sdvxid is not None:
            await download_and_merge_images(musicid, sdvxid, difficulty)
            return get_song_info(musicid) + (local_path,)
    except Exception as e:
        print(f"处理过程中出现错误：{e}")
        traceback.print_exc()

    return None

def get_song_info(musicid):
    with open("src/static/chu/data/music.json", 'r', encoding='utf-8') as file:
        songs = json.load(file)
        for song in songs:
            if song["id"] == str(musicid):
                return (song["title"],)
    return ("未知歌曲",)


if __name__ == '__main__':
    asyncio.run(get_chunithm_chart('musicid', 'difficulty'))
    #pass

