
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from .. import *
from .music import Music
from .image import DrawText
from .tool import wrap_text, truncate_text


MusicPic = rf"src/static/mai/pic"
Font_path = rf"src\static\mai\pic\font"
MusicCover = rf"src/static/mai/cover"
fEB = os.path.join(Font_path, 'FOT-RodinNTLGPro-EB.otf')
f35 = os.path.join(Font_path, 'SourceHanSans_35.otf')
f15 = os.path.join(Font_path, 'SourceHanSans_15.otf')
f17 = os.path.join(Font_path, 'SourceHanSans_17.ttf')
fB = os.path.join(Font_path, 'FOT-RodinNTLGPro-B.otf')




async def music_info_pic(music: Music) -> str:
    if len(music.level) == 5:
        im = Image.open(os.path.join(MusicPic, 'mai-id-bud-5.png')).convert('RGBA')
    else:
        im = Image.open(os.path.join(MusicPic, 'mai-id-bud-4.png')).convert('RGBA')
    dr = ImageDraw.Draw(im)

    #字体
    FEB = DrawText(dr, fEB)
    F35 = DrawText(dr, f35)
    F15 = DrawText(dr, f15)
    F17 = DrawText(dr, f17)
    FB = DrawText(dr, fB)
    FEBp = ImageFont.truetype(fEB, 42)
    F35p = ImageFont.truetype(f35, 42)
    F15p = ImageFont.truetype(f15, 24)
    F15p28 = ImageFont.truetype(f15, 28)
    F17p = ImageFont.truetype(f17, 28)
    
    #颜色
    default_color = (30, 54, 99, 255)
    white_color = (255, 255, 255, 255)
    rem_color = (195, 70, 231, 255)
    
    #粘贴歌曲封面等图片

    # if music_jp is None:
    #     file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(music.id)}.png')
    # else:
    #     file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(music_jp.id)}.png')
    file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(music.id)}.png')
    cover_paste = (Image.open(file_path).resize((300, 300)))
    im.paste(cover_paste, (130, 130))

    #版本获取

    # if music is None:
    #     from_text = ''
    # else:
    #     from_text = music['basic_info']['from']
    from_text = music['basic_info']['from']

    if from_text == "maimai PLUS":
        from_text = from_text
    elif from_text.startswith("maimai "):
        from_text = from_text.split("maimai ", 1)[1]
    else:
        from_text = from_text  

    #music_jpv = total_list_JP.by_id(music_jp.id)
    #from_text_jp = music_jpv['basic_info']['from']
    # if from_text_jp == "maimai PLUS":
    #     from_text_jp = from_text_jp
    # elif from_text_jp.startswith("maimai でらっくす "):
    #     from_text_jp = from_text_jp.split("maimai でらっくす ", 1)[1]
    # elif from_text_jp.startswith("maimai "):
    #     from_text_jp = from_text_jp.split("maimai ", 1)[1]
    # else:
    #     from_text_jp = from_text_jp



    # F17.draw(864, 793, 24, from_text_jp, default_color, 'ma')

    # if music_jp is not None:
    #     music = music_jp

    type_path = os.path.join(MusicPic, rf'{music.type}.png')
    type_paste = (Image.open(type_path).resize((90, 30))).convert('RGBA')
    im.paste(type_paste, (133, 400), mask=type_paste)
    
    #标题获取以及对其换行操作
    title = music.title
    max_width = 840
    fix_title = wrap_text(title, F35p, max_width)
    # t1 = F35p.getbbox(title)
    # lt1, ut1, rt1, lot1 = t1
    # t1h = abs(lot1 - ut1)
    #ascent, descent = F35p.getmetrics()
    y_text = 140 
    x_text = 460

    for line in fix_title:
        width, height = dr.textsize(line, font=F35p)
        
        #y_text -= ascent
        # y_text -= height
        dr.text((x_text, y_text), line, font=F35p, fill=default_color, anchor='lt')
        y_text += height   # 更新 y 坐标，以便下一行文本能够在下方显示




    #曲师获取以及对其换行操作
    artist = music.artist
    chart = music['charts']
    fix_artist = wrap_text(artist,F15p, max_width)

    y_text_A = 265

    for line in fix_artist:
        width, height = dr.textsize(line, font=F15p)
        #x_text = 460
        #y_text = 140
        dr.text((x_text, y_text_A), line, font=F15p, fill=default_color, anchor='lt')
        y_text_A += height
    # for line in fix_artist:
    #    width, height = dr.textsize(line, font=F35p)
    #    y_text = 265
    #    dr.text(((460 - width)/2, y_text), line, font=F15p, fill=default_color)
    #    y_text += height

    #F15.draw(460, 265, 28, fix_artist, default_color)

    #ID BPM 歌曲分类
    F17.draw(460, 395, 28, f'ID {music.id}          {music.genre}          BPM: {music.bpm}', default_color)

    #判断难度数量，确定是否用rem_color绘制歌曲信息
    # for num, chart_item in enumerate(music.level):
    #     color = white_color
    #     if len(music.level) == 5:           
    #         F17.draw(1180, 1218, 28, from_text, default_color, 'ma')
    #         FB.draw(181, 668 + 80 * num, 32, f'{music.level[num]} ({music.ds[num]:.1f})', color, 'ma')
    #         FB.draw(181, 1008, 32, f'{music.level[4]} ({music.ds[4]:.1f})', rem_color, 'ma')
    #         pass
    #     else:                   
    #         F17.draw(1180, 1088, 28, from_text, default_color, 'ma')
    #         FB.draw(181, 668 + 80 * num, 32, f'{music.level[num]} ({music.ds[num]:.1f})', color, 'ma')

    #     #谱师
 
    #   #  print(f"Type of chart: {type(chart)}")
    #     max_width_cha = 616
    #     charter = music.charts[num]['charter']
    #     if len(charter) > max_width_cha:
    #             charter = charter[:max_width_cha-3] + '...'
    #     if len(music.level) == 5: 
    #         F15.draw(300, 1128 + 60 * (num - 2), 28, charter, default_color)
    #     else:
    #         F15.draw(300, 1028 + 60 * (num - 2), 28, charter, default_color)
        
    #     #音符
    #    # print(f"Type of chart: {type(chart)}")
    #     notes = music.charts[num]['notes']
    #     total = sum(notes)
    #     FEB.draw(370, 655 + 80 * num, 32, total, default_color, 'ma')
    #     if len(notes) == 4:
    #         notes.insert(3, "-")
    #         for n, c in enumerate(notes):
    #             FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')
    #     else:
    #         notes_rem = music.charts[4]['notes']
    #         for n, c in enumerate(notes_rem):
    #             FB.draw(370 + 180 * n, 995, 32, c, default_color, 'ma')
    #         for n, c in enumerate(notes):
    #             if num == 4:
    #                 continue
    #             FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')

    # 检测music.level为5的情况
    if len(music.level) == 5:
        for num, chart_item in enumerate(music.level):           
            color = white_color
            # fromtext_fix = F17p.getbbox(from_text)
            # t1, t2, t3, t4 = fromtext_fix
            # th = abs(t4 -t2)
            # F17.draw(1180, 1218 + th, 28, from_text, default_color, 'mt')
            width, height = dr.textsize(from_text, font=F17p)
            dr.text((1180, 1221), from_text, font=F17p, fill=default_color, anchor='mt')
            if num < 4:
                FB.draw(181, 668 + 80 * num, 32, f'{music.level[num]} ({music.ds[num]:.1f})', color, 'ma')
            FB.draw(181, 1008, 32, f'{music.level[4]} ({music.ds[4]:.1f})', rem_color, 'ma')
            max_width_cha = 616
            #谱师
            charter_x = 300
            charter_y = 1128 + 30
            for i in music['charts'][2:]:
                fix_charter = truncate_text(i["charter"],F15p28, max_width_cha)
                charter_size = F15p28.getsize(i['charter'])
                dr.text((charter_x, charter_y-(charter_size[1]//2)), fix_charter, font=F15p28, fill=default_color, anchor='lm')
                charter_y += 60
            # charter1 = music.charts[2].charter
            # ps1 = F15p.getbbox(charter1)
            # left, upper, right, lower = ps1
            # ps1h = lower - upper
            
            # charter2 = music.charts[3].charter
            # ps2 = F15p.getbbox(charter2)
            # l2 ,u2 ,r2 ,lo2 = ps2
            # ps2h = lo2 - u2

            # ps2r = abs(ps2h - ps1h)

            # charter3 = music.charts[4].charter
            # ps3 = F15p.getbbox(charter3)
            # l3 ,u3 ,r3 ,lo3 = ps3
            # ps3h = lo3 - u3

            # ps3r = abs(ps3h - ps2h)

            # if ps3r == 0:
            #     ps3rr = ps2r
            # else:
            #     ps3rr = ps3r
            # print(ps2r)
            # print(ps3rr)
            # fix_charter1 = truncate_text(charter1,F15p, max_width_cha)
            # fix_charter2 = truncate_text(charter2,F15p, max_width_cha)
            # fix_charter3 = truncate_text(charter3,F15p, max_width_cha)


            # F15.draw(300, 1128, 28, fix_charter1, default_color, 'lt')
            # F15.draw(300, 1128 + 60 +ps2r, 28, fix_charter2, default_color, 'lt')
            # F15.draw(300, 1128 + 60 * 2+ps3rr, 28, fix_charter3, default_color, 'lt')
                
            notes = music.charts[num]['notes']
            #total = sum(notes)
            #total = sum(int(note) for note in notes)
            total = sum(int(note) if isinstance(note, str) and note.isdigit() else note for note in notes if isinstance(note, int) or (isinstance(note, str) and note.isdigit()))
            if num < 4:
                FEB.draw(370, 655 + 80 * num, 32, total, default_color, 'ma')
            if num == 4:
                FEB.draw(370, 995, 32, total, default_color, 'ma')
            if len(notes) == 5:
                for n, c in enumerate(notes):
                    if num < 4:
                        FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')
                    if num == 4:
                        FB.draw(550 + 180 * n, 995, 32, c, default_color, 'ma')
            else:
                notes.insert(3, "-")
                for n, c in enumerate(notes):
                    if num < 4:
                        FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')
                for n, c in enumerate(notes):
                    if num == 4:
                        FB.draw(550 + 180 * n, 995, 32, c, default_color, 'ma')
                    

    # 检测music.level为4的情况
    if len(music.level) == 4:                
        for num, chart_item in enumerate(music.level):
            
            color = white_color
            width, height = dr.textsize(from_text, font=F17p)
            dr.text((1180, 1089), from_text, font=F17p, fill=default_color, anchor='mt')
            #F17.draw(1180, 1088, 28, from_text, default_color, 'ma')
            FB.draw(181, 668 + 80 * num, 32, f'{music.level[num]} ({music.ds[num]:.1f})', color, 'ma')
            max_width_cha = 616
            #谱师
            charter_x = 300
            charter_y = 1028 + 30
            for i in music['charts'][2:]:
                fix_charter = truncate_text(i["charter"],F15p28, max_width_cha)
                charter_size = F15p28.getsize(i['charter'])
                dr.text((charter_x, charter_y-(charter_size[1]//2)), fix_charter, font=F15p28, fill=default_color, anchor='lm')
                charter_y += 60


            # charter1 = music.charts[2].charter
            # ps1 = F15p.getbbox(charter1)
            # left, upper, right, lower = ps1
            # ps1h = lower - upper
            
            # charter2 = music.charts[3].charter
            # ps2 = F15p.getbbox(charter2)
            # l2 ,u2 ,r2 ,lo2 = ps2
            # ps2h = lo2 - u2

            # ps2r = abs(ps2h - ps1h)

            # fix_charter1 = truncate_text(charter1,F15p, max_width_cha)
            # fix_charter2 = truncate_text(charter2,F15p, max_width_cha)

            # # if len(charter1) > max_width_cha:
            # #     charter1 = charter1[:max_width_cha-3] + '...'
            # # if len(charter2) > max_width_cha:
            # #     charter2 = charter2[:max_width_cha-3] + '...'

            # F15.draw(300, 1028, 28, fix_charter1, default_color, 'lt')
            # F15.draw(300, 1028 + 60 +ps2r, 28, fix_charter2, default_color, 'lt')

            notes = music.charts[num]['notes']
            
            #total = sum(notes)
            #total = sum(int(note) for note in notes)
            #total = sum(int(note) for note in notes if note.isdigit())
            #total = sum(int(note) if isinstance(note, str) and note.isdigit() else note for note in notes)
            total = sum(int(note) if isinstance(note, str) and note.isdigit() else note for note in notes if isinstance(note, int) or (isinstance(note, str) and note.isdigit()))
            FEB.draw(370, 655 + 80 * num, 32, total, default_color, 'ma')
            if len(notes) == 5:
                for n, c in enumerate(notes):
                    FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma') 
                        
            else:
                notes.insert(3, "-")
                for n, c in enumerate(notes):
                    FB.draw(550 + 180 * n, 655 + 80 * num, 32, c, default_color, 'ma')

    buffer = BytesIO()
    im.save(buffer, format='PNG')  
    byte_data = buffer.getvalue()
    msg = MessageSegment.image(image_to_base64(byte_data))
    return msg

