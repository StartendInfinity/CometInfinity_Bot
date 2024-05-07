from typing import Optional, Union, Tuple, List, Dict
from pathlib import Path
from datetime import datetime, date
import random
import json
from .config import DateTimeEncoder
from .utils import drawing
import base64

#path
today_path = rf"src/static/today/"
user_path = rf"src/static/today/user/"

class FortuneManager:

    def __init__(self):
        self._user_data: Dict[str, Dict[str, Union[str, int, date]]] = dict()
        self._user_data_file: Path = user_path + "fortune_data.json"

    def _multi_divine_check(self, uid: str, nowtime: date) -> bool:
        '''
            检测是否重复抽签
        '''
        self._load_data()

        # Means this is a new user
        if isinstance(self._user_data[uid]["last_sign_date"], int):
            return False

        last_sign_date: datetime = datetime.strptime(
            self._user_data[uid]["last_sign_date"], "%Y-%m-%d")

        return last_sign_date.date() == nowtime


    def divine(self, uid: str) -> Tuple[bool, Union[Path, None]]:
        '''
            今日运势抽签
        '''
        now_time: date = date.today()

        self._init_user_data(uid)


        if not self._multi_divine_check(uid, now_time):
            try:
                img_path = drawing(uid)
                with open(img_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                    image_file_base64 = f'base64://{encoded_image}'
                    self._user_data[uid]["image"] = image_file_base64
            except Exception:
                return True, None

            # Record the sign-in time
            self._end_data_handle(uid, now_time)
            return True, img_path
        else:
            img_path: Path = user_path + f"user_{uid}.png"
            return False, img_path

    def clean_out_pics(self) -> None:
        '''
            清空图片
        '''
        dirPath: Path = user_path
        for pic in dirPath.iterdir():
            pic.unlink()

    def _init_user_data(self, uid: str) -> None:
        '''
            用户不在抽签数据内，初始化
        '''
        self._load_data()

        if uid not in self._user_data:
            self._user_data[uid] = {
                "last_sign_date": 0 # Last sign-in date. YY-MM-DD
            }

        self._save_data()


    def _end_data_handle(self, uid: str, nowtime: date) -> None:
        '''
            结束数据保存
        '''
        self._load_data()

        self._user_data[uid]["last_sign_date"] = nowtime
        self._save_data()



    # ------------------------------ Utils ------------------------------ #
    def _load_data(self) -> None:
        '''
            读取抽签数据
        '''
        with open(self._user_data_file, "r", encoding="utf-8") as f:
            self._user_data = json.load(f)

    def _save_data(self) -> None:
        '''
            保存抽签数据
        '''
        with open(self._user_data_file, "w", encoding="utf-8") as f:
            json.dump(self._user_data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)



fortune_manager = FortuneManager()
