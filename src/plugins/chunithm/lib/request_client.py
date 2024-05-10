
import asyncio
import os
import math
from typing import Optional, Dict, List, Tuple
import json
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.plugins.chunithm.lib.chunithm_music import get_cover_len4_id, total_list
from src.lib.utils import timing_decorator,timing_decorator_async
import asyncio

LXNSAUTH = "pCx9K3Sta3034GljtbR6ykfQfbR12uZbnbYdePcQKGM="
HEADERS = {"Authorization": LXNSAUTH}

@timing_decorator_async
async def get_player_info_by_lx(user_id,friend_code=None):
    if friend_code:
        request_url = f"https://maimai.lxns.net/api/v0/chunithm/player/{friend_code}"
    else:
        request_url = f"https://maimai.lxns.net/api/v0/chunithm/player/qq/{user_id}"
    async with aiohttp.request('GET', request_url, headers = HEADERS) as resp:
        obj = await resp.json()
        print(obj)
        if obj['code'] == 200:
            return 200,obj['data']
        else:
            return obj['code'],obj.get('message',"unknow error message")
        
@timing_decorator_async
async def get_player_best_by_lx(player_info):
    request_url = f"https://maimai.lxns.net/api/v0/chunithm/player/{player_info['friend_code']}/bests"
    async with aiohttp.request('GET', request_url, headers = HEADERS) as resp:
        obj = await resp.json()
        if obj['code'] == 200:
            return 200,obj['data']
        else:
            return obj['code'],obj.get('message',"unknow error message")

@timing_decorator_async
async def generate_best_30_data_by_lx(user_id,friend_code=None):
    status_code, player_info = await get_player_info_by_lx(user_id,friend_code)
    if status_code == 200:
        status_code, player_best = await get_player_best_by_lx(player_info)
        if status_code == 200:
            player_data = {**player_info,**player_best}
            return 200,player_data
        else:
            return status_code, player_best
    else:
        return status_code,player_info
    
async def generate_best_30_data_by_df(params):
    request_url = f"https://www.diving-fish.com/api/chunithmprober/query/player"
    async with aiohttp.request('POST', request_url, json=params) as resp:
        obj = await resp.json()
        print(obj)
        if resp.status == 200:
            return 200,obj
        else:
            return resp.status,obj.get('message',"unknow error message")