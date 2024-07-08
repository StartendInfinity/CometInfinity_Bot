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

import json

mai_bind = on_command("/bind", priority=5)

@mai_bind.handle()
async def maibind(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if len(args) != 2:
        await mai_bind.send("\n请使用正确的格式：/bind -lm 舞萌好友码 或 /bind -lc 中二好友码")
        return
    command, id = args
    if command not in ["-lm", "-lc"]:
        await mai_bind.send("\n请使用正确的格式：/bind -lm 舞萌好友码 或 /bind -lc 中二好友码")
        return
    try:
        with open("./data/bind_data.json", "r+", encoding="utf-8") as f:
            bind_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bind_data = {}
    user_id = str(event.user_id)
    if user_id not in bind_data:
        bind_data[user_id] = {"lm": "", "lc": ""}
    bind_data[user_id][command[1:]] = id
    with open("./data/bind_data.json", "w", encoding="utf-8") as f:
        json.dump(bind_data, f, ensure_ascii=False, indent=4)
    await mai_bind.send(f"\n绑定成功！您的{command[1:].upper()} 好友码 已更新为 {id}。")

mai_unbind = on_command('/bind -unbind', priority=1)

@mai_unbind.handle()
async def maiunbind(event: GroupMessageEvent, matcher: Matcher):
    user_id = str(event.user_id)
    try:
        with open("./data/bind_data.json", "r+", encoding="utf-8") as f:
            bind_data = json.load(f)
        if user_id in bind_data:
            del bind_data[user_id]
            with open("./data/bind_data.json", "w", encoding="utf-8") as f:
                json.dump(bind_data, f, ensure_ascii=False, indent=4)
            await mai_unbind.send(f"\n成功解绑。")
        else:
            await mai_unbind.send(f"\n您还没有绑定过任何用户信息。")
    except FileNotFoundError:
        await mai_unbind.send(f"\n目前还没有任何绑定信息。")
