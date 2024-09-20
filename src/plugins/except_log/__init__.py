import traceback
from pathlib import Path

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageSegment, Event, NetworkError
from nonebot.internal.matcher import Matcher
from nonebot.message import run_postprocessor


@run_postprocessor
async def _(event: Event, matcher: Matcher, exception: Exception | None):
    if not exception or isinstance(exception, NetworkError):
        return
    # bot = get_bot()
    traceback.print_exc()
    # traceback.print_exc()
    # msg = MessageSegment.text(
    #     f"{trace}{event.get_plaintext()}\n{event.get_session_id()}"
    # )
    # await bot.send_msg(group_id=236030263, message=msg)
    feedback = (
        MessageSegment.reply(event.message_id),
        MessageSegment.text("发生了错误，请重试或联系管理员。")
    )
    await matcher.send(feedback)
