import json
import os
import requests
from loguru import logger
#import logging

# 定义版本号到版本代号的映射
version_mapping = {
    "v1 1.00.00": "CHUNITHM",
    "v1 1.05.00": "CHUNITHM PLUS",
    "v1 1.10.00": "AIR",
    "v1 1.15.00": "AIR PLUS",
    "v1 1.20.00": "STAR",
    "v1 1.25.00": "STAR PLUS",
    "v1 1.30.00": "AMAZON",
    "v1 1.35.00": "AMAZON PLUS",
    "v1 1.40.00": "CRYSTAL",
    "v1 1.45.00": "CRYSTAL PLUS",
    "v1 1.50.00": "PARADISE",
    "v1 1.55.00": "PARADISE LOST",
    "v2 2.00.00": "NEW",
    "v2 2.05.00": "NEW PLUS",
    "v2 2.10.00": "SUN",
    "v2 2.15.00": "SUN PLUS",
    "v2 2.20.00": "LUMINOUS"
}


# upload
try:
    response = requests.get("https://maimai.lxns.net/api/v0/chunithm/song/list")
    old_json = response.json()

    # 读取from.json文件
    with open("src/plugins/chunithm/music_data/from.json", "r", encoding="utf-8") as f:
        from_data = json.load(f)

    from_data_dict = {song["id"]: song for song in from_data}

    # reload
    new_json = []

    for song in old_json["songs"]:
        new_song = {
            "id": song["id"],
            "title": song["title"],
            "basic_info": {
                "title": song["title"],
                "artist": song["artist"],
                "genre": song["genre"],
                "bpm": song["bpm"],
                "from": "CHUNITHM"
            },
            "ds": [],
            "level": [],
            "cids": [],
            "charts": []
        }

        for i, difficulty in enumerate(song["difficulties"]):
            new_song["ds"].append(difficulty["level_value"])
            new_song["level"].append(difficulty["level"])
            new_song["cids"].append(i + 1)
            new_song["charts"].append({
                "combo": 0,  # 并没有包含"combo"这个字段
                "charter": difficulty["note_designer"]
            })

        new_json.append(new_song)

    for song in new_json:
        # 如果歌曲ID在from.json中存在
        if song["id"] in from_data_dict:
            # 更新新的json数据中的combo和charter
            for i in range(len(song["charts"])):
                song["charts"][i]["combo"] = from_data_dict[song["id"]]["charts"][i]["combo"]
                song["charts"][i]["charter"] = from_data_dict[song["id"]]["charts"][i]["charter"]
            
            # 更新新的json数据中的from字段
            version_number = from_data_dict[song["id"]]["basic_info"]["from"]
            if version_number in version_mapping:
                song["basic_info"]["from"] = version_mapping[version_number]
            else:
                song["basic_info"]["from"] = version_number
            # song["basic_info"]["from"] = from_data_dict[song["id"]]["basic_info"]["from"]


    # if not os.path.exists("music_data"):
    #     os.makedirs("music_data")

    with open("src/plugins/chunithm/music_data/music_data.json", "w", encoding="utf-8") as f:
        json.dump(new_json, f, ensure_ascii=False, indent=4)
    logger.info("json数据已成功更新，保存到music_data文件夹中。")
except Exception as e:
    logger.error(f"更新json数据时发生错误：{e}")
