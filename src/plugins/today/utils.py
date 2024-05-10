from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List
from pathlib import Path
import random
import json
import os

from datetime import datetime
import time
from zhdate import ZhDate

from .music.mai import total_list
from .music.chu import total_list_chu, get_cover_len4_id

#素材载入
cover = rf"src/static/today/"
Font_path = rf"src/static/today/font/"
cover_user = rf"src/static/today/user/"

#字体
f12 = os.path.join(Font_path, 'SourceHanSerif_12.ttf')
f14 = os.path.join(Font_path, 'SourceHanSerif_14.ttf')
f16 = os.path.join(Font_path, 'SourceHanSerif_16.ttf')
f18 = os.path.join(Font_path, 'SourceHanSerif_18.ttf')

def drawing(uid: str) -> Path:
    #随机数
    def hash_to(qq: int):
        days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
            time.strftime("%m", time.localtime(time.time()))) + 77
        return (days * qq) >> 8
    h = hash_to(int(uid))
    special_numbers = {9: "today-bg-9", 24: "today-bg-24", 39: "today-bg-39"}
    random_number = random.randint(0, 99)

    #图片加载
    bg_image_name = special_numbers.get(random_number, "today-bg")
    bg_image_path = os.path.join(cover, f"{bg_image_name}.png")
    im = Image.open(bg_image_path).convert('RGBA')
    dr = ImageDraw.Draw(im)

    #字体格式化
    F12wmy = ImageFont.truetype(f12, 36)
    F14d1 = ImageFont.truetype(f14, 72)
    F14rq = ImageFont.truetype(f14, 48)
    F14wmg = ImageFont.truetype(f14, 36)
    F16wmt = ImageFont.truetype(f16, 60)  
    F18dsz = ImageFont.truetype(f18, 240)
    F18yj = ImageFont.truetype(f18, 72)

    #时间获取
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")
    lnow = ZhDate.today()
    znow = time.localtime()
    weekday = ["一", "二", "三", "四", "五", "六", "日"]
    chinese_date = lnow.chinese()
    # 获取天干地支的年份
    lyear = chinese_date.split(" ")[1]

    # 获取农历的月和日
    lday = chinese_date.split(" ")[0].split("年")[1]

    # 重新组合农历日期
    nlnow = lyear + lday

    #干什么
    title_y = "宜"
    title_j = "忌"
    y_list = ["干饭", "出勤", "理论", "女装", "水群", "卖弱", "复读", "下埋", "越级"]
    random_y = random.sample(y_list, 3)
    j_list = ["抽卡", "卖瓜", "梆人", "饮茶", "唱打", "蹦迪", "去超商", "打麻将"]
    random_j = random.sample(j_list, 3)

    def get_cover_len6_id(mid: str) -> str:
        mid = int(mid)
        if mid > 10000:
            mid -= 10000
        return f'{mid:06d}'

    def draw_and_save(title_y, title_j, random_y, random_j):
        #Draw
        color = "#B79D73"

        Tdate = f'{formatted_date}  星期{weekday[znow.tm_wday]}  {nlnow}'
        Tluck = f'{random_number}'
        text_width, text_height = dr.textsize(Tluck, font=F18dsz)
        start_x = 270
        start_y = 289 - (text_height // 5)
        dr.text((720, 245), Tdate, font=F14rq, fill=color, anchor='mt')
        dr.text((start_x, start_y), Tluck, font=F18dsz, fill=color, anchor='ma')
        dr.text((570, 332), title_y, font=F18yj, fill=color, anchor='lt')
        dr.text((570, 442), title_j, font=F18yj, fill=color, anchor='lt')
        dr.text((690, 332), "  ".join(random_y), font=F14d1, fill=color, anchor='lt')
        dr.text((690, 442), "  ".join(random_j), font=F14d1, fill=color, anchor='lt')

        #################Music##################

        #Mai
        total_list_mai = total_list
        mai_songs = h % len(total_list_mai)
        mai_music = total_list[mai_songs]
        try:
            cover = Image.open(rf"src\static\mai\cover\UI_Jacket_{get_cover_len6_id(mai_music.id)}.png").convert("RGBA")
        except:
            cover = Image.open(rf"src\static\mai\cover\UI_Jacket_0000.png")
        cover_resize = cover.resize((180,180))
        im.paste(cover_resize,(120,820))
        flag = 0
        title_v = f'{mai_music.title}'
        #215
        if ((F16wmt.getsize(title_v))[0] > 970):
            flag = 1
        limit = lambda text: text if F16wmt.getsize(text)[0] <= 970 else limit(text[:-1])
        title_v = limit(title_v)
        if (flag == 1):
            title_v += '...'
        flbg = 0
        title_a = f'{mai_music.artist}'
        #215
        if ((F12wmy.getsize(title_a))[0] > 970):
            flbg = 1
        limit = lambda text: text if F12wmy.getsize(text)[0] <= 970 else limit(text[:-1])
        title_a = limit(title_a)
        if (flbg == 1):
            title_a += '...'
        dr.text((350,820), f'{title_v}', font=F16wmt, fill=color, anchor='lt')
        dr.text((350,900), f'{title_a}', font=F12wmy, fill=color, anchor='lt')
        dr.text((350,965), f'舞萌DX  {mai_music.genre}', font=F14wmg, fill=color, anchor='lt')


        #Chu
        chu_songs = h % len(total_list_chu)
        chu_music = total_list_chu[chu_songs]
        mchu = chu_music['basic_info']
        try:
            cover = Image.open(rf"src\static\chu\cover\CHU_UI_Jacket_{get_cover_len4_id(chu_music.id)}.png").convert("RGBA")
        except:
            cover = Image.open(rf"src\static\chu\cover\CHU_UI_Jacket_0000.png")
        cover_resize = cover.resize((180,180))
        im.paste(cover_resize,(120,1060))
        flag = 0
        title_v = chu_music.title
        #215
        if ((F16wmt.getsize(title_v))[0] > 970):
            flag = 1
        limit = lambda text: text if F16wmt.getsize(text)[0] <= 970 else limit(text[:-1])
        title_v = limit(title_v)
        if (flag == 1):
            title_v += '...'
        flbg = 0
        title_a = mchu['artist']
        #215
        if ((F12wmy.getsize(title_a))[0] > 970):
            flbg = 1
        limit = lambda text: text if F12wmy.getsize(text)[0] <= 970 else limit(text[:-1])
        title_a = limit(title_a)
        if (flbg == 1):
            title_a += '...'
        dr.text((350,1060), f'{title_v}', font=F16wmt, fill=color, anchor='lt')
        dr.text((350,1140), f'{title_a}', font=F12wmy, fill=color, anchor='lt')
        dr.text((350,1205), f"中二节奏  {mchu['genre']}", font=F14wmg, fill=color, anchor='lt')



        # Save
        outDir= Path(cover_user)
        if not outDir.exists():
            outDir.mkdir(exist_ok=True, parents=True)

        outPath= Path(cover_user + "user" + f"_{uid}.png")
        im_rgb = im.convert('RGB')
        new_width = 720  # 新的宽度
        new_height = int(new_width * im_rgb.height / im_rgb.width)  # 保持原始宽高比
        tImg_resized = im_rgb.resize((new_width, new_height))
        tImg_resized.save(outPath)
        return outPath

    #随机数
    if random_number in special_numbers:
        if random_number == 9:
            title_y = ""
            title_j = ""
            random_y = ""
            random_j = ""
        elif random_number == 24:
            title_y = ""
            title_j = ""
            random_y = ""
            random_j = ""
        elif random_number == 39:
            title_y = ""
            title_j = ""
            random_y = ""
            random_j = ""
        return draw_and_save(title_y, title_j, random_y, random_j)
    else:
        # 使用默认文字内容
        return draw_and_save(title_y="宜", title_j="忌",
                      random_y=random.sample(y_list, 3),
                      random_j=random.sample(j_list, 3))
    
    


def decrement(text: str) -> Tuple[int, List[str]]:
    '''
        Split the text, return the number of columns and text list
        TODO: Now, it ONLY fit with 2 columns of text
    '''
    length: int = len(text)
    result: List[str] = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception

    col_num: int = 1
    while length > cardinality:
        col_num += 1
        length -= cardinality

    # Optimize for two columns
    space = " "
    length = len(text)  # Value of length is changed!

    if col_num == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return col_num, [text[: int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return col_num, [text[: int((length + 1) / 2)] + fillIn, fillIn + space + text[int((length + 1) / 2):]]

    for i in range(col_num):
        if i == col_num - 1 or col_num == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality: (i + 1) * cardinality])

    return col_num, result


