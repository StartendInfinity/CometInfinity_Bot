from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra
from typing import List, Dict, Union
from pathlib import Path
from datetime import datetime, date
import json

'''
    抽签主题对应表，第一键值为“抽签设置”或“主题列表”展示的主题名称
    Key-Value: 主题资源文件夹名-主题别名
'''


class PluginConfig(BaseModel, extra=Extra.ignore):
    fortune_path: Path = Path(__file__).parent / "resource"


class ThemesFlagConfig(BaseModel, extra=Extra.ignore):
    '''
        Switches of themes only valid in random divination.
        Make sure NOT ALL FALSE!
    '''
    touhou_flag: bool = True
    touhou_lostword_flag: bool = True
    touhou_old_flag: bool = True


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        return json.JSONEncoder.default(self, obj)