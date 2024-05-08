
import asyncio
import os
import math
from typing import Optional, Dict, List, Tuple
import json
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.plugins.chunithm.lib.chunithm_music import get_cover_len4_id, total_list
from src.plugins.chunithm.lib.chunithm_best_30 import BestList,ChartInfo
import asyncio

LXNSAUTH = "pCx9K3Sta3034GljtbR6ykfQfbR12uZbnbYdePcQKGM="
HEADERS = {"Authorization": LXNSAUTH}

async def get_player_info(user_id):
    request_url = f"https://maimai.lxns.net/api/v0/chunithm/player/qq/{user_id}"
    async with aiohttp.request('GET', request_url, headers = HEADERS) as resp:
        obj = await resp.json()
        if obj['code'] == 200:
            return 200,obj['data']
        else:
            return obj['code'],obj.get('message',"unknow error message")

async def get_player_best(player_info):
    request_url = f"https://maimai.lxns.net/api/v0/chunithm/player/{player_info['friend_code']}/bests"
    async with aiohttp.request('GET', request_url, headers = HEADERS) as resp:
        obj = await resp.json()
        if obj['code'] == 200:
            return 200,obj['data']
        else:
            return obj['code'],obj.get('message',"unknow error message")

        
async def generate_best_30_data(user_id):
    status_code, player_info = await get_player_info(user_id)
    if status_code == 200:
        status_code, player_best = await get_player_best(player_info)
        player_data = {**player_info,**player_best}
        return 200,player_data
    else:
        return status_code,player_info
    


async def generate(payload: Dict) -> Tuple[Optional[Image.Image], bool]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/chunithmprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        b30_best = BestList(30)
        r10_best = BestList(10)
        obj = await resp.json()
        b30: List[Dict] = obj["records"]["b30"]
        r10: List[Dict] = obj["records"]["r10"]
        for c in b30:
            b30_best.push(ChartInfo.from_json(c))
        for c in r10:
            r10_best.push(ChartInfo.from_json(c))
        print(obj)
        pic = DrawBest(b30_best, r10_best, obj["nickname"], obj["rating"], obj["rating"]).getDir()
        # pic.show()
        # return pic, 0
