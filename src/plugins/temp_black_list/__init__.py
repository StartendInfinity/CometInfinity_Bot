from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message ,MessageEvent,GroupMessageEvent,Bot
from nonebot.plugin import on_command
from nonebot.params import CommandArg
from .black_list_handle import admin
from nonebot.log import logger
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.rule import Rule

# 绝对超级管理员 管理黑白名单
BOT_DATA_STAFF = [2636464059, 1826356872]

def check_is_bot_data_staff():
    async def _checker(event: GroupMessageEvent) -> bool:
        if event.user_id in BOT_DATA_STAFF:
            return True
        else:
            return False
    return Rule(_checker)

add_group_white = on_command('开启群', rule=check_is_bot_data_staff(),priority=3)
delete_group_white = on_command('关闭群', rule=check_is_bot_data_staff(),priority=3)
add_user_black = on_command('拉黑', rule=check_is_bot_data_staff(),priority=3)
delete_user_black = on_command('解黑', rule=check_is_bot_data_staff(),priority=3)

def execut_event_message(event:MessageEvent):
    return
    # 下面是xray用来log的逻辑代码
    # data = event.message
    # msglist = []
    # for item in data:
    #     if item.type == 'text':
    #         msg = item.data['text']
    #         msglist.append(msg)
    #     else:
    #         msglist.append(f"【{item.type}】")
    # msg = ''.join(msglist)
    # log_data = {"type":"message_event"}
    # if isinstance(event,GroupMessageEvent):
    #     log_data["group_id"] = event.group_id
    # log_data['user_id'] = event.user_id
    # log_data['content'] = msg
    # c_logger.debug(log_data)
    

@event_preprocessor
def blacklist_processor(event: MessageEvent):
    is_block = 0
    if isinstance(event,GroupMessageEvent):
        if event.group_id in admin.get_groupid():
            is_block = 0
        else:
            is_block = 1
    if event.user_id in admin.get_userid():
        is_block = 1
    if event.user_id in BOT_DATA_STAFF:
        is_block = 0

    if is_block:
        logger.success(f'拒绝开启会话')
        raise IgnoredException('黑名单会话')
    else:
        execut_event_message(event)
        return

@add_group_white.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    groupid = int(str(args).strip())
    await add_group_white.send(admin.add_group(groupid))

@delete_group_white.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    groupid = int(str(args).strip())
    await delete_group_white.send(admin.del_group(groupid))

@add_user_black.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    userid = int(str(args).strip())
    await add_user_black.send(admin.add_user(userid))

@delete_user_black.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    userid = int(str(args).strip())
    await add_user_black.send(admin.del_user(userid))

# add_along_black = on_command('关闭龙图模式',rule=check_Along_admin(),priority=3)
# @add_along_black.handle()
# async def __(event: GroupMessageEvent):
#     await add_along_black.send(admin.add_along_black(event.group_id))

# del_along_black = on_command('开启龙图模式',rule=check_Along_admin(),priority=3)
# @del_along_black.handle()
# async def __(event: GroupMessageEvent):
#     await del_along_black.send(admin.del_along_black(event.group_id))