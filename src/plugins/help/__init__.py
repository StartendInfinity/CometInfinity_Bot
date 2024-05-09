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
import base64
import json

HelpPic = rf"src/static/help/help.png"
B50PIC = rf"src/static/help/b50.png"
B30PIC = rf"src/static/help/b30.png"
AP50PIC = rf"src/static/help/ap50.png"

help = on_command("/help", priority=5)
@help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
        markdown_template = {
        "markdown": {
            "custom_template_id": "102096146_1713624398",
            "params": [
                {
                    "key": "title",
                    "values": ["使用帮助"]
                },{
                    "key": "content",
                    "values": ["你好，我是「彗星Infinity」。\r请点击下方按钮来查看相应内容。"]
                }
            ]
        }
    }

        button_template = {
            "keyboard": {
                "content": {
                    "rows": [
                        {
                            "buttons": [
                                {
                                    "id": "0",
                                    "render_data": {
                                        "label": "查看使用文档",
                                        "visited_label": "查看使用文档",
                                        "style": 1
                                    },
                                    "action": {
                                        "type": 0,
                                        "enter": True,
                                        "permission": {
                                            "type": 2
                                        },
                                        "data": "https://docs.qq.com/aio/p/scc3uu0rnyljokq"
                                    }
                                }]
                                
                        },
                        {
                            "buttons": [
                                {
                                    "id": "1",
                                    "render_data": {
                                        "label": "用户成绩使用指南",
                                        "visited_label": "用户成绩使用指南",
                                        "style": 1
                                    },
                                    "action": {
                                        "type": 0,
                                        "enter": True,
                                        "permission": {
                                            "type": 2
                                        },
                                        "data": "https://docs.qq.com/aio/p/scwb3supuxs96cx"
                                    }
                                }]
                                
                        },
                        {
                            "buttons": [
                                {
                                    "id": "2",
                                    "render_data": {
                                        "label": "添加至群聊",
                                        "visited_label": "添加至群聊",
                                        "style": 1
                                    },
                                    "action": {
                                        "type": 0,
                                        "enter": True,
                                        "permission": {
                                            "type": 2
                                        },
                                        "data": "https://qun.qq.com/qqweb/qunpro/jump?id=qun-robot-share&robot_appid=102096146&robot_uin=3889013808"
                                    }
                                }]
                                
                        },
                    ]
                }
            }
        }

        combined_template = {**markdown_template, **button_template}
        encoded_template = base64.b64encode(json.dumps(combined_template).encode()).decode()

        await help.send(f"[CQ:markdown,data=base64://{encoded_template}]")
        # with open(HelpPic, 'rb') as image_file:
        #     image_data = image_file.read()
        #     base64_data = base64.b64encode(image_data).decode('utf-8')
        # await help.send(f'[CQ:image,file=base64://{base64_data}]')


mai_help = on_command("/mai", priority=5)
@mai_help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      await mai_help.send(f'\n此指令可以查询「舞萌DX」相关信息。\n具体的使用说明请查看使用文档。')


chu_help = on_command("/chu", priority=5)
@chu_help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      await chu_help.send(f'\n此指令可以查询「中二节奏」相关信息。\n具体的使用说明请查看使用文档。')


chu_help = on_command("/data", priority=5)
@chu_help.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
      await chu_help.send(f'\n通过此命令可以切换玩家的数据查询来源。\n当前版本不支持切换，全部数据的默认来源为落雪咖啡屋。\n具体的使用说明请查看使用文档。')



#临时
b50 = on_command("/b50", priority=5)
@b50.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
        with open(B50PIC, 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        await b50.send(f'[CQ:image,file=base64://{base64_data}]')

# b30 = on_command("/b30", priority=5)
# @b30.handle()
# async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
#         with open(B30PIC, 'rb') as image_file:
#             image_data = image_file.read()
#             base64_data = base64.b64encode(image_data).decode('utf-8')
#         await b30.send(f'[CQ:image,file=base64://{base64_data}]')

ap50 = on_command("/ap50", priority=5)
@ap50.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
        with open(AP50PIC, 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        await ap50.send(f'[CQ:image,file=base64://{base64_data}]')


