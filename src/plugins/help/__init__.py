from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event
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
import base64
import json

help = on_command("/help", priority=5)
@help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      with open("./src/static/mai/pic/help-infinity.png", 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
      await help.send(MessageSegment.image(f"base64://{base64_data}"), reply_message = True)

mai_help = on_command("/mai", priority=5)
@mai_help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      await mai_help.send(f'此指令可以查询「舞萌DX」相关信息。\n具体的使用说明请查看使用文档。', reply_message = True)


chu_help = on_command("/chu", priority=5)
@chu_help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      await chu_help.send(f'此指令可以查询「中二节奏」相关信息。\n具体的使用说明请查看使用文档。', reply_message = True)

#由于确认短时间内不会再次兼容落雪，故此处代码被删除 -- XiaoYan