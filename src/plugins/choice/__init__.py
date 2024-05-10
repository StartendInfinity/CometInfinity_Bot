from nonebot import on_command, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg, EventMessage

import random
import re

choose_none = on_command("/做选择",priority=6)
@choose_none.handle()
async def _(event: Event, message: Message = EventMessage()):
    await choose.send(f"\n无法识别您的命令。\n请至少提供两个选项，用全角逗号隔开。")

zxz = "/做选择 "

choose = on_regex(zxz + ".+，.+")

@choose.handle()
async def _(event: Event, message: Message = EventMessage()):
    text = event.get_plaintext()
    fix_text = str(text)
    cho = re.match(zxz + "(.+)", fix_text).groups()[0]
    choices = cho.split("，")
    if len(choices) < 2 or all(not choice.strip() for choice in choices):
        await choose.finish("\n无法识别您的命令。\n请至少提供两个选项，用全角逗号隔开。")
    #options = re.findall(r'[^，]+', text)
    #regex = "/做选择" + r"(.+)，(.+)"
    #if not cho:
    #    await choose.finish("\n无法识别您的命令。\n请至少提供两个选项，用全角逗号隔开。")
    #match = re.match(regex, str(message)).groups()
    
    #choices = [left.strip(), right.strip()]
    rand_num = random.randint(-1, 5 * len(choices))
    
    if 0 <= int(rand_num / 5) < len(choices):
        await choose.send(f"\n建议您选择“{choices[int(rand_num / 5)]}”呢。")
    elif rand_num == -1:
        await choose.send( "\n建议您都不选呢。")
    else:
       await choose.send( "\n建议您全都要捏！")

