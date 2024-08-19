# -*- coding: utf-8 -*-
from typing import Any
import math
import os
from io import BytesIO
from typing import Dict
from PIL import Image, ImageDraw, ImageFont
from .image import DrawText
from .music import total_list
from .tool import get_cover_len6_id, image_to_base64
from nonebot.adapters.onebot.v11 import MessageSegment
#from maimaidx_project import *

def split_text(font: ImageFont.FreeTypeFont, max_len: int, text_: str) -> list[str]:
    split_list = [text_, ]
    while font.getsize(split_list[-1])[0] >= max_len:
        point = len(split_list[-1])
        while font.getsize(split_list[-1][:point])[0] >= max_len:
            point -= 1
        split_list.append(split_list[-1][point:])
        split_list[-2] = split_list[-2][:point]
    return split_list

async def score_line(chart_id: str, level_index: int):
    sd_color = (30, 54, 99, 255)
    level_labels3 = ['0', '1', '2', '3', '4']
    music = total_list.by_id(chart_id)
    chart: Dict[Any] = music['charts'][level_index]
    tap = int(chart['notes'][0])
    slide = int(chart['notes'][2])
    hold = int(chart['notes'][1])
    touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
    brk = int(chart['notes'][-1])
    total_note = tap + slide + hold + brk + touch
    total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
    break_bonus = 0.01 / brk
    break_50_reduce = total_score * break_bonus / 4
    each_tap_g_minus = 10000 / total_score
    each_brk_50_minus = break_50_reduce / total_score * 100

    bg_path = os.path.join(
        f'./src/static/mai/pic/mai-accal-bud-{level_labels3[level_index]}.png')
    bg = Image.open(bg_path).resize((1440, 1870)).convert('RGBA')
    cover = Image.open(
        os.path.join(
            f'./src/static/mai/cover/UI_Jacket_{get_cover_len6_id(int(chart_id))}.png')).convert(
        'RGBA').resize((300, 300))
    print(music.type)
    type_path = os.path.join(
        f'./src/static/mai/pic/{music.type}.png')
    ty = Image.open(type_path).resize((90, 30)).convert('RGBA')

    bg.alpha_composite(cover, (130, 130))  # 封面坐标
    bg.alpha_composite(ty, (133, 400))  # 乐曲种类

    Font_path = rf"src\static\mai\pic\font"

    fot_eb = os.path.join(Font_path, 'FOT-RodinNTLGPro-EB.otf')
    f35 = os.path.join(Font_path, 'SourceHanSans_35.otf')
    han15 = os.path.join(Font_path, 'SourceHanSans_15.otf')
    han17 = os.path.join(Font_path, 'SourceHanSans_17.ttf')
    fot = os.path.join(Font_path, 'FOT-RodinNTLGPro-B.otf')

    fontd = ImageDraw.Draw(bg)
    no15 = DrawText(fontd, han15)
    no17 = DrawText(fontd, han17)
    #no37 = DrawText(fontd, han37)
    font_b = DrawText(fontd, fot)
    font_eb = DrawText(fontd, fot_eb)

    shs35_42 = ImageFont.truetype("src/static/mai/pic/font/SourceHanSans_35.otf", 42,
                                  encoding="utf-8")
    shs15_28 = ImageFont.truetype("src/static/mai/pic/font/SourceHanSans_15.otf", 28,
                                  encoding="utf-8")
    text_y_len = shs35_42.getsize(music.title)[1]
    for i, text_part in enumerate(split_text(shs35_42, 840, music.title)):
        ImageDraw.Draw(bg).text((460, i * text_y_len + 140), text_part, "#1E3663", font=shs35_42)  # 标题

    text_y_len = shs15_28.getsize(music.artist)[1]
    for i, text_part in enumerate(split_text(shs15_28, 840, music.artist)):
        ImageDraw.Draw(bg).text((460, i * text_y_len + 265), text_part, "#1E3663", font=shs15_28)  # 作曲家
    no17.draw(460, 395, 28, f'ID {music.id}          {music.genre}          BPM: {music.bpm} ',
              color=sd_color)

    level_value = music["level"][level_index]
    ds_value = music["ds"][level_index]
    if level_index != 4:
        font_b.draw(181, 668, 32, f"{level_value} ({ds_value:.1f})", (255, 255, 255, 255), anchor='ma')
    else:
        font_b.draw(181, 668, 32, f"{level_value} ({ds_value:.1f})", (195, 70, 231, 255), anchor='ma')
    if music.type == "标准":
        font_eb.draw(370, 655, 32, f"{total_note}", color=sd_color, anchor='ma')
        font_b.draw(550, 655, 32, f"{tap}", color=sd_color, anchor='ma')
        font_b.draw(730, 655, 32, f"{hold}", color=sd_color, anchor='ma')
        font_b.draw(910, 655, 32, f"{slide}", color=sd_color, anchor='ma')
        font_b.draw(1090, 655, 32, "-", color=sd_color, anchor='ma')
        font_b.draw(1270, 655, 32, f"{brk}", color=sd_color, anchor='ma')
    else:
        font_eb.draw(370, 655, 32, f"{total_note}", color=sd_color, anchor='ma')
        font_b.draw(550, 655, 32, f"{tap}", color=sd_color, anchor='ma')
        font_b.draw(730, 655, 32, f"{hold}", color=sd_color, anchor='ma')
        font_b.draw(910, 655, 32, f"{slide}", color=sd_color, anchor='ma')
        font_b.draw(1090, 655, 32, f"{touch}", color=sd_color, anchor='ma')
        font_b.draw(1270, 655, 32, f"{brk}", color=sd_color, anchor='ma')

    font_b.draw(375, 878, 24, f"-{each_tap_g_minus:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(625, 878, 24, f"-{each_tap_g_minus * 2.5:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(875, 878, 24, f"-{each_tap_g_minus * 5:.5f}%", color=sd_color, anchor='ma')

    font_b.draw(375, 938, 24, f"-{each_tap_g_minus * 2:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(625, 938, 24, f"-{each_tap_g_minus * 2.5 * 2:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(875, 938, 24, f"-{each_tap_g_minus * 5 * 2:.5f}%", color=sd_color, anchor='ma')

    font_b.draw(375, 998, 24, f"-{each_tap_g_minus * 3:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(625, 998, 24, f"-{each_tap_g_minus * 2.5 * 3:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(875, 998, 24, f"-{each_tap_g_minus * 5 * 3:.5f}%", color=sd_color, anchor='ma')

    if music.type == "标准":
        font_b.draw(375, 1058, 24, f"-", color=sd_color, anchor='ma')
        font_b.draw(625, 1058, 24, f"-", color=sd_color, anchor='ma')
        font_b.draw(875, 1058, 24, f"-", color=sd_color, anchor='ma')
    else:
        font_b.draw(375, 1058, 24, f"-{each_tap_g_minus:.5f}%", color=sd_color, anchor='ma')
        font_b.draw(625, 1058, 24, f"-{each_tap_g_minus * 2.5:.5f}%", color=sd_color, anchor='ma')
        font_b.draw(875, 1058, 24, f"-{each_tap_g_minus * 5:.5f}%", color=sd_color, anchor='ma')

    font_b.draw(414, 1118, 24, f"-{each_tap_g_minus * 5 + each_brk_50_minus * 2.4:.5f}%", color=sd_color,
                # 4.0
                anchor='ma')
    font_b.draw(414, 1178, 24, f"-{each_tap_g_minus * 10 + each_brk_50_minus * 2.4:.5f}%", color=sd_color,
    #1148
                # 3.0
                anchor='ma')
    font_b.draw(414, 1238, 24, f"-{each_tap_g_minus * 12.5 + each_brk_50_minus * 2.4:.5f}%", color=sd_color,
    #1178
                # 2.5
                anchor='ma')
    font_b.draw(625, 1148, 24, f"-{each_tap_g_minus * 15 + each_brk_50_minus * 2.8:.5f}%", color=sd_color,
                # good
                anchor='ma')
    font_b.draw(875, 1148, 24, f"-{each_tap_g_minus * 25 + each_brk_50_minus * 4:.5f}%", color=sd_color,
                # miss
                anchor='ma')

    font_b.draw(664, 1238, 24, f"-{each_brk_50_minus:.5f}%", color=sd_color, anchor='ma')
    font_b.draw(914, 1238, 24, f"-{each_brk_50_minus * 2:.5f}%", color=sd_color, anchor='ma')

    max_dx_score = total_note * 3

    font_b.draw(1260, 875, 32,
    #878
                f"{max_dx_score}",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 938, 24,
                f"{math.ceil(max_dx_score * 0.98)} (-{max_dx_score - math.ceil(max_dx_score * 0.98)})",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 998, 24,
                f"{math.ceil(max_dx_score * 0.97)} (-{max_dx_score - math.ceil(max_dx_score * 0.97)})",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 1058, 24,
                f"{math.ceil(max_dx_score * 0.95)} (-{max_dx_score - math.ceil(max_dx_score * 0.95)})",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 1118, 24,
                f"{math.ceil(max_dx_score * 0.93)} (-{max_dx_score - math.ceil(max_dx_score * 0.93)})",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 1178, 24,
                f"{math.ceil(max_dx_score * 0.90)} (-{max_dx_score - math.ceil(max_dx_score * 0.90)})",
                color=sd_color, anchor='ma')
    font_b.draw(1260, 1238, 24,
                f"{math.ceil(max_dx_score * 0.85)} (-{max_dx_score - math.ceil(max_dx_score * 0.85)})",
                color=sd_color, anchor='ma')

    font_b.draw(370, 1455, 30, f"{int(0.5 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    font_b.draw(550, 1455, 30, f"{int(1.0 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    font_b.draw(730, 1455, 30, f"{int(1.5 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    font_b.draw(910, 1455, 30, f"{int(2.0 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    font_b.draw(1090, 1455, 30, f"{int(3.0 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    font_b.draw(1270, 1455, 30, f"{int(4.0 / each_tap_g_minus)}", color=sd_color, anchor='ma')
    # font_b.draw(935, 1455, 21, f"{int(21.0 / each_tap_g_minus)}", color=sd_color, anchor='ma')

    font_b.draw(359, 1685, 30, f"{each_brk_50_minus / each_tap_g_minus:.3f}", color=sd_color, anchor='ma')
    font_b.draw(513, 1685, 30, f"{each_brk_50_minus * 2 / each_tap_g_minus:.3f}", color=sd_color,
                anchor='ma')
    font_b.draw(667, 1685, 30, f"{(each_tap_g_minus * 5 + each_brk_50_minus * 2.4) / each_tap_g_minus:.3f}",
                color=sd_color, anchor='ma')
    font_b.draw(821, 1685, 30, f"{(each_tap_g_minus * 10 + each_brk_50_minus * 2.4) / each_tap_g_minus:.3f}",
                color=sd_color, anchor='ma')
    font_b.draw(975, 1685, 30, f"{(each_tap_g_minus * 12.5 + each_brk_50_minus * 2.4) / each_tap_g_minus:.3f}",
                color=sd_color, anchor='ma')
    font_b.draw(1129, 1685, 30, f"{(each_tap_g_minus * 15 + each_brk_50_minus * 2.8) / each_tap_g_minus:.3f}",
                color=sd_color, anchor='ma')
    font_b.draw(1283, 1685, 30, f"{(each_tap_g_minus * 25 + each_brk_50_minus * 4) / each_tap_g_minus:.3f}",
                color=sd_color, anchor='ma')

    '''credit_path = os.path.join(
        f'./hoshino/modules/maimaiDX/static/mai/score_line/milk.png')
    credit = Image.open(credit_path).resize((560, 24)).convert('RGBA')
    bg.alpha_composite(credit, (250, 1350)'''
    #bg.show()
    buffer = BytesIO()
    bg.save(buffer, format='PNG')  
    byte_data = buffer.getvalue()
    msg = MessageSegment.image(image_to_base64(byte_data))
    #msg = MessageSegment.image(image_to_base64(bg))
    return msg
'''except:
    await bot.send(ev, '格式错误，输入“分数线 帮助”以查看帮助信息', at_sender=True)'''

