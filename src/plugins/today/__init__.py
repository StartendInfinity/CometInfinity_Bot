from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup, Endswith
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)

from .data import fortune_manager
from .utils import drawing

import os
import base64

today = on_command("/today")


@today.handle()
async def _(event: Event, matcher: Matcher):
    uid: str = str(event.user_id)
    _, image_file_a = fortune_manager.divine(uid)
    #image_file_a = drawing(uid)
    with open(image_file_a, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            image_file_base64 = f'base64://{encoded_image}'
    
            msg = MessageSegment.image(image_file_base64)

    
    
    
    await today.finish(msg)

