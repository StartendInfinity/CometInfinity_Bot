import base64
from typing import Tuple
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from .. import *
from .chunithm_music import Music, get_cover_len4_id, Song
from .image import DrawText
from .tool import wrap_text, truncate_text
import os

MusicPic = rf"src/static/chu/pic"
Font_path = rf"src\static\chu\pic\font"
MusicCover = rf"src/static/chu/cover"
fEB = os.path.join(Font_path, 'FOT-RodinNTLGPro-EB.otf')
f35 = os.path.join(Font_path, 'SourceHanSans_35.otf')
f15 = os.path.join(Font_path, 'SourceHanSans_15.otf')
f17 = os.path.join(Font_path, 'SourceHanSans_17.ttf')
fB = os.path.join(Font_path, 'FOT-RodinNTLGPro-B.otf')

def image_to_base64(byte_data: bytes) -> str:
    base64_str = base64.b64encode(byte_data).decode()
    return 'base64://' + base64_str




async def music_info_pic(music: Song, from_ver: Music) -> str:
    if len(music.difficulties) == 5:
        im = Image.open(os.path.join(MusicPic, 'chu-id-lum-5.png')).convert('RGBA')
    else:
        im = Image.open(os.path.join(MusicPic, 'chu-id-lum-4.png')).convert('RGBA')
    dr = ImageDraw.Draw(im)

    #字体
    FEB = DrawText(dr, fEB)
    F35 = DrawText(dr, f35)
    F15 = DrawText(dr, f15)
    F17 = DrawText(dr, f17)
    FB = DrawText(dr, fB)
    FBp = ImageFont.truetype(fB, 32)
    FEBp = ImageFont.truetype(fEB, 42)
    FEBp32 = ImageFont.truetype(fEB, 32)
    F35p = ImageFont.truetype(f35, 42)
    F15p = ImageFont.truetype(f15, 24)
    F15p28 = ImageFont.truetype(f15, 28)
    F17p = ImageFont.truetype(f17, 28)
    
    #颜色
    default_color = (30, 54, 99, 255)
    white_color = (255, 255, 255, 255)
    rem_color = (195, 70, 231, 255)
    
    #粘贴歌曲封面等图片

    file_path = os.path.join(MusicCover, rf'CHU_UI_Jacket_{get_cover_len4_id(music.id)}.png')
    cover_paste = (Image.open(file_path).resize((300, 300)))
    im.paste(cover_paste, (130, 130))

    #版本获取

    from_text = from_ver['basic_info']['from']



    # type_path = os.path.join(MusicPic, rf'{music.type}.png')
    # type_paste = (Image.open(type_path).resize((90, 30))).convert('RGBA')
    # im.paste(type_paste, (133, 400), mask=type_paste)
    
    #标题获取以及对其换行操作
    title = music.title
    max_width = 840
    fix_title = wrap_text(title, F35p, max_width)
    y_text = 140 
    x_text = 460

    for line in fix_title:
        width, height = dr.textsize(line, font=F35p)
        
        dr.text((x_text, y_text), line, font=F35p, fill=default_color, anchor='lt')
        y_text += height   # 更新 y 坐标，以便下一行文本能够在下方显示




    #曲师获取以及对其换行操作
    artist = music.artist
    # chart = music['charts']
    fix_artist = wrap_text(artist,F15p, max_width)

    y_text_A = 265

    for line in fix_artist:
        width, height = dr.textsize(line, font=F15p)
        dr.text((x_text, y_text_A), line, font=F15p, fill=default_color, anchor='lt')
        y_text_A += height

    #ID BPM 歌曲分类
    F17.draw(460, 395, 28, f'ID {music.id}          {music.genre}          BPM: {music.bpm}', default_color)

    # 检测music.level为5的情况
    if len(music.difficulties) == 5:
        for num, difficulty in enumerate(music.difficulties): 
            color = white_color
            width, height = dr.textsize(from_text, font=F17p)
            dr.text((1180, 1221), from_text, font=F17p, fill=default_color, anchor='mt')
            if num < 4:
                FB.draw(181, 668 + 80 * num, 32, f'{difficulty["level"]} ({difficulty["level_value"]:.1f})', color, 'ma')
            elif num == 4:
                FB.draw(181, 1008, 32, f'{difficulty["level"]} ({difficulty["level_value"]:.1f})', color, 'ma')
            max_width_cha = 616
            #谱师
            charter_x = 300
            charter_y = 1128 + 30
            for i in music.difficulties[2:]:
                fix_charter = truncate_text(i["note_designer"],F15p28, max_width_cha)
                charter_size = F15p28.getsize(i["note_designer"])
                dr.text((charter_x, charter_y-(charter_size[1]//2)), fix_charter, font=F15p28, fill=default_color, anchor='lm')
                charter_y += 60

            notes = difficulty["notes"]

            for n, c in enumerate(notes):
                attributes = ['total', 'tap', 'hold', 'slide', 'air', 'flick']
                # total = c.total
                # tap = c.tap
                # hold = c.hold
                # slide = c.slide
                # air = c.air
                # flick = c.flick
                for i, attr in enumerate(attributes):
                    value = getattr(c, attr)
                    # 如果属性是 'flick' 并且其值为 0，则跳过这次绘制
                    if attr == 'total':
                        font_style = FEBp32
                    else:
                        font_style = FBp
                    if attr == 'flick' and value == 0:
                        continue
                    if num < 4:
                        dr.text((370 + 180 * i, 655 + 80 * num), str(value), font=font_style, fill=default_color, anchor='ma')
                    if num == 4:
                        dr.text((370 + 180 * i, 995), str(value), font=font_style, fill=default_color, anchor='ma')
            # else:
            #     notes.insert(3, "-")
            #     for n, c in enumerate(notes):
            #         if num < 4:
            #             FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')
            #     for n, c in enumerate(notes):
            #         if num == 4:
            #             FB.draw(550 + 180 * n, 995, 32, c, default_color, 'ma')
                    

    # 检测music.level为4的情况
    if len(music.difficulties) == 4:                
        for num, difficulty in enumerate(music.difficulties):
            
            color = white_color
            width, height = dr.textsize(from_text, font=F17p)
            dr.text((1180, 1091), from_text, font=F17p, fill=default_color, anchor='mt')
            FB.draw(181, 668 + 80 * num, 32, f'{difficulty["level"]} ({difficulty["level_value"]:.1f})', color, 'ma')
            max_width_cha = 616
            #谱师
            
            charter_x = 300
            charter_y = 1028 + 30
            for i in music.difficulties[2:]:
                fix_charter = truncate_text(i["note_designer"],F15p28, max_width_cha)
                charter_size = F15p28.getsize(i["note_designer"])
                dr.text((charter_x, charter_y-(charter_size[1]//2)), fix_charter, font=F15p28, fill=default_color, anchor='lm')
                charter_y += 60



            notes = difficulty["notes"]
            
            for n, c in enumerate(notes):
                attributes = ['total', 'tap', 'hold', 'slide', 'air', 'flick']
                # total = c.total
                # tap = c.tap
                # hold = c.hold
                # slide = c.slide
                # air = c.air
                # flick = c.flick
                for i, attr in enumerate(attributes):
                    value = getattr(c, attr)
                    # 如果属性是 'flick' 并且其值为 0，则跳过这次绘制
                    if attr == 'total':
                        font_style = FEBp32
                    else:
                        font_style = FBp
                    if attr == 'flick' and value == 0:
                        continue
                    dr.text((370 + 180 * i, 655 + 80 * num), str(value), font=font_style, fill=default_color, anchor='ma')
                        
            # else:
            #     notes.insert(3, "-")
            #     for n, c in enumerate(notes):
            #         FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')

    buffer = BytesIO()
    im.save(buffer, format='PNG')  
    byte_data = buffer.getvalue()
    msg = MessageSegment.image(image_to_base64(byte_data))
    return msg

