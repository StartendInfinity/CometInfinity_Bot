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
    try:
        with open("./data/bind_data.json", "r", encoding="utf-8") as f:
            bind_data = json.load(f)
    except UnicodeDecodeError:
        with open("./data/bind_data.json", "r", encoding="utf-8-sig") as f:
            bind_data = json.load(f)
    except FileNotFoundError:
            bind_data = {}
    username = arg.extract_plain_text().strip()
    if not username:
        await mai_bind.send("\n请在指令后输入您的好友码。")
        return
    # if not username.isdigit() or len(username) > 10:
    #     await mai_bind.send("\n请输入正确的 QQ 号码！")
    #     return
    #load_maibind_data()
    user_id = str(event.user_id) # 获取用户 ID
    if user_id not in bind_data: # 如果该用户还没有绑定过任何用户名
        bind_data[user_id] = username # 将用户名绑定到该用户
        try:
            with open("./data/bind_data.json", "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.update(bind_data)
                f.seek(0)
                f.truncate()
                json.dump(data, f, ensure_ascii=False, indent=4)
                #json.dump(maibind_data, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            bind_data = {}
        await mai_bind.send(f"\n绑定成功！")
    else: # 如果该用户已经绑定过一个用户名
        await mai_bind.send(f"\n您已经绑定过用户信息。\n使用 -unbind 参数来解除绑定。")

mai_unbind = on_command('/bind -unbind',priority=1)

@mai_unbind.handle()
async def maiunbind(event: GroupMessageEvent, matcher: Matcher):
    try:
        with open("./data/bind_data.json", "r", encoding="utf-8") as f:
            bind_data = json.load(f)
    except UnicodeDecodeError:
        with open("./data/bind_data.json", "r", encoding="utf-8-sig") as f:
            bind_data = json.load(f)
    user_id = str(event.user_id) # 获取用户 ID
    if user_id in bind_data: # 如果该用户已经绑定过一个用户名
        #username = maibind_data[user_id] # 获取绑定的用户名
        del bind_data[user_id] # 从数据中删除该用户
        try:
            with open("./data/bind_data.json", "w", encoding="utf-8") as f:
                json.dump(bind_data, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            bind_data = {}
        await mai_unbind.send(f"\n成功解绑。")
    else: # 如果该用户还没有绑定过任何用户名
        await mai_unbind.send(f"\n您还没有绑定过任何用户信息。")