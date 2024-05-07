from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
import json
import aiohttp
import requests

async def get_group_count():
    response = requests.get('http://127.0.0.1:10088/get_group_list')
    data = json.loads(response.text)
    group_count = len(data['data'])
    return group_count


check_in = on_command("/ping", priority=5)

@check_in.handle()
async def handle_check_in(bot: Bot, event: Event, state: T_State):
    group = await get_group_count()
    await check_in.finish(f"\n状态：200（OK）\n已加入群聊数：{group}")