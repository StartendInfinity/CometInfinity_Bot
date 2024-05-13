from nonebot import on_command, on_regex, get_driver
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment



#内建模块
import math
import re
import os
import random
import base64

#加载工具组，以正确显示图片、获取曲目信息等
from .lib.tool import get_cover_len6_id, image_to_base64, is_pro_group, computeRaB50, get_cover_len4_id
from .lib.music import total_list, total_alias_list
from .lib.MusicPic import MusicCover, music_info_pic, MusicPic
from .lib.score_line import score_line

#依赖项
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
SUPERUSERS = get_driver().config.superusers

mai_regex = r'/mai\s*'


#-----s-maisong------START
music_song = on_regex(mai_regex + r"(song)\s*(\d+)(\s*-jp)?")

@music_song.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"(song)\s*(\d+)(\s*-jp)?"
    match = re.match(regex, str(message))
    groups = match.groups()
    mid = groups[1]


    #判断乐曲数据是否在CN里，若不在则遍历JP并使国服版本一行留空
    music = total_list.by_id(mid)
    #music_jp = total_list_JP.by_id(mid)
    from_text = music['basic_info']['from']



    #高级功能，是否遍历JP乐曲数据
    # if match.group(3) is not None:
    #     if is_pro_group(event.group_id):
    #         music = total_list_JP.by_id(mid)
    #     else:
    #         if str(event.get_user_id()) in SUPERUSERS:
    #             music = total_list_JP.by_id(mid)
    #         else:
    #             await music_song.finish("权限不足")
    # elif match.group(3) is None:
    #     pass


    try:

        #调整封面图片以正确显示
        #file_path = rf"src/static/mai/cover/UI_Jacket_{get_cover_len6_id(mid)}.png"
        file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid)}.png')

        if not os.path.exists(file_path):
            raise FileNotFoundError
        file = Image.open(file_path)
        buffer = BytesIO()
        file.save(buffer, format='PNG')  
        byte_data = buffer.getvalue()

        #判断版本开头是否为maimai 或 maimai でらっくす
        if from_text == "maimai PLUS":
            from_text = from_text
        elif from_text.startswith("舞萌"):
            from_text = from_text
        elif from_text.startswith("maimai "):
            from_text = from_text.split("maimai ", 1)[1]
        else:
            from_text = from_text  

        # from_text_jp = music_jp['basic_info']['from']
        # if from_text_jp == "maimai PLUS":
        #     from_text_jp = from_text_jp
        # elif from_text_jp.startswith("maimai でらっくす "):
        #     from_text_jp = from_text_jp.split("maimai でらっくす ", 1)[1]
        # elif from_text_jp.startswith("maimai "):
        #     from_text_jp = from_text_jp.split("maimai ", 1)[1]
        # else:
        #     from_text_jp = from_text_jp
            
        await music_song.send(Message(f"""[CQ:image,file={image_to_base64(byte_data)}]""" + 
                                      f"\n{music['id']}. {music['title']}\n" + 
                                      f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
谱面类型：{music['type']}
版本：{from_text}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}'''))
    except (FileNotFoundError, Exception) as e:
        print(e)
        await music_song.send("歌曲不存在哦！")
#-----s-maisong------END




#-----s-maichart------START
mai_chart = on_regex(mai_regex + r"(chart)\s*([绿黄红紫白]?)\s*(\d+)")

@mai_chart.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"(chart)\s*([绿黄红紫白]?)\s*(\d+)"
    match = re.match(regex, str(message))

    #判断表达式第二组是否在level_labels内，若不在则终止命令
    level_labels = ['绿', '黄', '红', '紫', '白']
    if match is None or match.group(2) not in level_labels:
        await mai_chart.finish("难度输入不对哦！")

    groups = match.groups()
    level_index = level_labels.index(groups[1])
    level_name = ['BASIC', 'ADVANCED', 'EXPERT', 'MASTER', 'Re:MASTER']
    mid = groups[2]


    #高级功能，是否遍历JP乐曲数据
    # if match.group(4) is not None:
    #     if is_pro_group(event.group_id):
    #         music = total_list_JP.by_id(mid)
    #     else:
    #         if str(event.get_user_id()) in SUPERUSERS:
    #             music = total_list_JP.by_id(mid)
    #         else:
    #             await music_song.finish("权限不足")
    # elif match.group(4) is None:
    #     pass

    try:

        file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid)}.png')

        if not os.path.exists(file_path):
            raise FileNotFoundError
        file = Image.open(file_path)

        #调整封面图片以正确显示
        buffer = BytesIO()
        file.save(buffer, format='PNG')  
        byte_data = buffer.getvalue()

        music = total_list.by_id(mid)
        chart = music['charts'][level_index]
        ds = music['ds'][level_index]
        level = music['level'][level_index]
        combo = sum(chart['notes'])

        #判断版本开头是否为maimai 或 maimai でらっくす
        from_text = music['basic_info']['from']
        if from_text == "maimai PLUS":
            from_text = from_text
        elif from_text.startswith("maimai でらっくす "):
            from_text = from_text.split("maimai でらっくす ", 1)[1]
        elif from_text.startswith("maimai "):
            from_text = from_text.split("maimai ", 1)[1]
        else:
            from_text = from_text 
        #开始列出数据，并判断note种类数
        if len(chart['notes']) == 4:
            note = f'''TAP：{chart['notes'][0]}
HOLD：{chart['notes'][1]}
SLIDE：{chart['notes'][2]}
BREAK：{chart['notes'][3]}
谱师：{chart['charter']}'''
        else:
            note = f'''TAP：{chart['notes'][0]}
HOLD：{chart['notes'][1]}
SLIDE：{chart['notes'][2]}
TOUCH：{chart['notes'][3]}
BREAK：{chart['notes'][4]}
谱师：{chart['charter']}'''
        await mai_chart.send(Message(f"""[CQ:image,file={image_to_base64(byte_data)}]""" +
                                       f"\n{music['id']}. {music['title']}\n" +
                                       f'''谱面类型：{music['type']}
BPM：{music['basic_info']['bpm']}
难度：{level_name[level_index]} {level} ({ds:.1f})
TOTAL：{combo}\n''' +
note
                                       ))
    except (FileNotFoundError, Exception) as e:
        print(e)
        await music_song.send("歌曲不存在哦！")
#-----s-maichart------END




#-----s-id------START
mai_id = on_regex(mai_regex + r"id\s*(\d+)")

@mai_id.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"id\s*(\d+)"
    match = re.match(regex, str(message))
    groups = match.groups()
    id = groups[0]
    #print(id)

    if not id:
        return
    if id.isdigit():       
        music = total_list.by_id(id)
        #music_jp = None

        #高级功能，是否遍历JP乐曲数据
        # if match.group(2) is not None:
        #     if is_pro_group(event.group_id):
        #         music_jp = total_list_JP.by_id(id)
        #     else:
        #         if str(event.get_user_id()) in SUPERUSERS:
        #             music_jp = total_list_JP.by_id(id)
        #         else:
        #             await music_song.finish("权限不足")
        # elif match.group(2) is None:
        #     pass
        #     music_jp = total_list.by_id(id)
        # if music is None and music_jp is None:
        #     await mai_id.finish('歌曲不存在哦！')
        #print(music)
        msg = await music_info_pic(music)           
        await mai_id.send(msg)
    else:
        await mai_id.send('歌曲不存在哦！')
#-----s-id------END




#-----s-search-----START
search_music = on_regex(mai_regex + r"(查歌|search|bpm查歌|BPM查歌|曲师查歌|定数查歌|等级查歌|物量查歌)\s*([绿黄红紫白]?)\s*(.+?)(?:\s*-p\s*(\d+))?$")

#定数查歌相关
def handle_ds_search(color, name, total_list):
    level_labels = ['绿', '黄', '红', '紫', '白']
    if color:
        level_index = level_labels.index(color)
        return total_list.filter(ds=float(name), level_search=level_labels[level_index])
    return total_list.filter(ds=float(name))

#等级查歌相关
def handle_level_search(color, name, total_list):
    level_labels = ['绿', '黄', '红', '紫', '白']
    if color:
        level_index = level_labels.index(color)
        return total_list.filter(level=name, level_search2=level_labels[level_index])
    return total_list.filter(level=name)

@search_music.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"(查歌|search|bpm查歌|BPM查歌|曲师查歌|定数查歌|等级查歌|物量查歌)\s*([绿黄红紫白]?)\s*(.+?)(?:\s*-p\s*(\d+))?$"
    match = re.match(regex, str(message)).groups()
    #name = re.match(regex, str(message)).groups()[0].strip()

    std, color, name, page = match
    page = int(page) if page else 1
    if name.strip() == "":
        return
    


    #高级功能，是否遍历JP乐曲数据
    # if match.group(2) is not None:
    #     if is_pro_group(event.group_id):
    #         res = total_list_JP.filter(title_search=name)
    #         print("1")
    #     else:
    #         if str(event.get_user_id()) in SUPERUSERS:
    #             res = total_list_JP.filter(title_search=name)
    #             print("2")
    #         else:
    #             await music_song.finish("权限不足")
    # elif match.group(2) is None:
    res = []
    if std in ['search', '查歌']:
        res = total_list.filter(title_search=name)
    elif std == '曲师查歌':
        res = total_list.filter(artist=name)
    elif std in ['bpm查歌', 'BPM查歌']:
        res = total_list.filter(bpm=float(name))
    elif std == '定数查歌':
        res = handle_ds_search(color, name, total_list)
    elif std == '等级查歌':
        res = handle_level_search(color, name, total_list)
    elif std == '物量查歌':
        res = total_list.filter(total=float(name))
        #print(res)

    if len(res) == 0:
        await search_music.send("\n没有搜索到任何结果。")
    elif len(res) == 1:
        music = total_list.by_id(res[0]['id'])
        msg = await music_info_pic(music)
        await mai_id.send(msg)
    elif len(res) <= 15:
        search_result = ""
        temp = None
        for music in sorted(res, key = lambda i: int(i['id'])):
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
            if not color and (std == '定数查歌' or std == '等级查歌' or std== '物量查歌'):
                difficulty_color = ''
                if std == '定数查歌':
                    # ds_index = music['ds'].index(float(name))
                    # difficulty_color = list(color_to_index.keys())[list(color_to_index.values()).index(ds_index)]
                    print(music['ds'])
                    for ds_index, ds_value in enumerate(music['ds']):
                        if ds_value == float(name):
                            # 使用 color_to_index 字典来获取难度颜色
                            difficulty_color = list(color_to_index.keys())[ds_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"
                elif std == '等级查歌':
                    for level_index, level_value in enumerate(music['level']):
                        if level_value == name:
                            difficulty_color = list(color_to_index.keys())[level_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"
                elif std == '物量查歌':
                    total_notes = []
                    for chart in music['charts']:
                        total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                    music["total_notes"] = total_notes
                    for total_index, total_value in enumerate(music["total_notes"]):
                        if total_value == float(name):
                            difficulty_color = list(color_to_index.keys())[total_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"


            else:
                search_result += f"{music['id']}. {music['title']}\n"
        await search_music.send(f"\n共找到 {len(res)} 条结果：\n"+ search_result.strip())
    else:
        per_page = 15
        total_pages = math.ceil(len(res) / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        search_result = ""
        temp = None
        for music in sorted(res[start:end], key = lambda i: int(i['id'])):
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
            #indexToLevel = {'0': "绿", '1': "黄", '2': "红", '3': "紫", '4': "白"}
            if not color and (std == '定数查歌' or std == '等级查歌' or std== '物量查歌'):
                difficulty_color = ''
                if std == '定数查歌':
                    for ds_index, ds_value in enumerate(music['ds']):
                        if ds_value == float(name):
                            # 使用 color_to_index 字典来获取难度颜色
                            difficulty_color = list(color_to_index.keys())[ds_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"
                elif std == '等级查歌':
                    for level_index, level_value in enumerate(music['level']):
                        if level_value == name:
                            difficulty_color = list(color_to_index.keys())[level_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"
                elif std == '物量查歌':
                    total_notes = []
                    for chart in music['charts']:
                        total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                    music["total_notes"] = total_notes
                    for total_index, total_value in enumerate(music["total_notes"]):
                        if total_value == float(name):
                            difficulty_color = list(color_to_index.keys())[total_index]
                            search_result += f"{music['id']}  {difficulty_color}  {music['title']}\n"
            else:
                search_result += f"{music['id']}. {music['title']}\n"
        #print(search_result)
        await search_music.send(f"\n共找到 {len(res)} 条，第 {page}/{total_pages} 页:\n"+ search_result.strip() + f"\n使用参数 -p [页码] 来翻页")
#-----s-search-----END




#-----s-random-----START
random_music = on_regex(mai_regex + r"(定数|等级)?\s*随歌\s*([绿黄红紫白])?\s*([0-9]+\.?[0-9]*[+]?)?\s*(-pic)?")



@random_music.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"(定数|等级)?\s*随歌\s*([绿黄红紫白])?\s*([0-9]+\.?[0-9]*[+]?)?\s*(-pic)?"
    match = re.search(regex, str(message)).groups()
    set, level, ds, pic = match
    try:
        if level == " ":
            level = None
        if set == '定数':
            music_ds = total_list.filter(ds=float(ds))
            if level:
                level_labels = ['绿', '黄', '红', '紫', '白']
                level_index = level_labels.index(level)
                music_l1 = total_list.filter(level_search=level_labels[level_index], ds=float(ds))
                music_ds_a = random.choice(music_l1)
            else:
                music_ds_a = random.choice(music_ds)
            mid = f"{music_ds_a['id']}"
            if pic:
                if level:
                    msg = await music_info_pic(music_l1.random())
                else:
                    msg = await music_info_pic(music_ds.random())
            else:
                file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid)}.png')

                if not os.path.exists(file_path):
                    raise FileNotFoundError
                file = Image.open(file_path)
                #调整封面图片以正确显示
                buffer = BytesIO()
                file.save(buffer, format='PNG')  
                byte_data = buffer.getvalue()
                msg = Message(f"""[CQ:image,file={image_to_base64(byte_data)}]""" + 
                                            f"\n{music_ds_a['id']}. {music_ds_a['title']}\n" + 
                                            f'''艺术家：{music_ds_a['basic_info']['artist']}
分类：{music_ds_a['basic_info']['genre']}
BPM：{music_ds_a['basic_info']['bpm']}
谱面类型：{music_ds_a['type']}
版本：{music_ds_a['basic_info']['from']}
等级：{', '.join(music_ds_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_ds_a['ds'])}''')
            await random_music.send(msg)
        if set == '等级':
            music_level = total_list.filter(level=ds)
            if level:
                level_labels2 = ['绿', '黄', '红', '紫', '白']
                level_index2 = level_labels2.index(level)
                music_l2 = total_list.filter(level_search2=level_labels2[level_index2], level=ds)
                music_level_a = random.choice(music_l2)
            else:
                music_level_a = random.choice(music_level)
            mid2 = f"{music_level_a['id']}"
            if pic:
                if level:
                    msg = await music_info_pic(music_l2.random())
                else:
                    msg = await music_info_pic(music_level.random())
            else:
                file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid2)}.png')

                if not os.path.exists(file_path):
                    raise FileNotFoundError
                file = Image.open(file_path)
                #调整封面图片以正确显示
                buffer = BytesIO()
                file.save(buffer, format='PNG')  
                byte_data = buffer.getvalue()
                msg = Message(f"""[CQ:image,file={image_to_base64(byte_data)}]""" + 
                                            f"\n{music_level_a['id']}. {music_level_a['title']}\n" + 
                                            f'''艺术家：{music_level_a['basic_info']['artist']}
分类：{music_level_a['basic_info']['genre']}
BPM：{music_level_a['basic_info']['bpm']}
谱面类型：{music_level_a['type']}
版本：{music_level_a['basic_info']['from']}
等级：{', '.join(music_level_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_level_a['ds'])}''')
            await random_music.send(msg)
        if pic:
            msg = await music_info_pic(total_list.random())
        else:
            music = total_list.random()
            mid3 = f"{music['id']}"
            file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid3)}.png')

            if not os.path.exists(file_path):
                raise FileNotFoundError
            file = Image.open(file_path)
            #调整封面图片以正确显示
            buffer = BytesIO()
            file.save(buffer, format='PNG')  
            byte_data = buffer.getvalue()
            msg = Message(f"""[CQ:image,file={image_to_base64(byte_data)}]""" + 
                                        f"\n{music['id']}. {music['title']}\n" + 
                                        f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
谱面类型：{music['type']}
版本：{music['basic_info']['from']}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}''')
    except Exception as e:
        await random_music.finish(f"\n指定的条件下没有任何歌曲。\n{e}")
    await random_music.send(msg)
#-----s-random-----END


#-----s-mai_plate-----START
mai_plate = on_regex(mai_regex + r"牌子条件")

@mai_plate.handle()
async def _(event: Event, message: Message = EventMessage()):
    plate_path = os.path.join(MusicPic, rf'plate_rule.png')
    with open(plate_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
    await mai_plate.send(f'[CQ:image,file=base64://{base64_data}]')
#-----s-mai_plate-----END
    
#-----s-rating_cal-----START
rating_cal = on_regex(mai_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?")

@rating_cal.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?"
    match = re.search(regex, str(message)).groups()
    ds, ach = match
    # if not ds and not ach:
    #     await rating_cal.send("\n异常\n请输入正确的定数与达成率！")
    if not (1.0 <= float(ds) <= 15.0):
        await rating_cal.finish("\n请输入正确的定数与达成率！")
    try:
        ra = computeRaB50(float(ds), float(ach))
        await rating_cal.send(f"\n定数 {float(ds)} \n在 {float(ach):.4f}% 的得分是 {ra}")
    except ValueError:
        await rating_cal.send("\n请输入正确的定数与达成率！")
    except TypeError:
        await rating_cal.send("\n请输入正确的定数与达成率！")
#-----s-rating_cal-----END

#-----s-alias-----START
alias_search = on_regex(mai_regex + r"找歌\s*(.+)")

@alias_search.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"找歌\s*(.+)"
    match_regex = re.match(regex, str(event.get_message())).groups()
    name = match_regex[0]
    data = total_alias_list.by_alias(name)
    print(data)
    #data_id = total_alias_list.by_id(name)
    #music = total_list.by_id(data.song_id)
    if not data:
        await alias_search.finish('\n没有搜索到任何结果。')
    if len(data) != 1:
        msg = f"\n共找到 {len(data)} 条结果：\n"
        for songs in data:
            #music = total_list.by_id(songs.song_id)
            print(songs)
            musics = total_list.by_id(str(songs.song_id))
            print(musics)
            if musics is not None:  # 检查歌曲是否存在
                title = musics['title']
                msg += f'{songs.song_id}. {title}\n'
            else:
                msg += f'{songs.song_id}：error\n'
        # await alias_search.finish(msg.strip())
        await alias_search.finish(msg)
    music = total_list.by_id(str(data[0].song_id))
    await alias_search.finish(await music_info_pic(music))
#-----s-alias-----END

#-----s-lookalia-----START
alias_look = on_regex(mai_regex + r"查看别名\s*(.+)")

@alias_look.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"查看别名\s*(.+)"
    match_regex = re.match(regex, str(event.get_message())).groups()
    mid = int(match_regex[0])
    data = total_alias_list.by_id(mid)
    if not data:
        await alias_search.finish('\n这首歌现在没有别名。\n您可以前往落雪咖啡屋的曲目别名投票申请创建曲目别名。')
    
    await alias_look.finish(f"\n这首歌的别名有: \n{data}\n别名数据来自Xray Bot。")
#-----s-lookalia-----END

#-----s-score_line-----START
score_x = on_regex(mai_regex + r"分数线\s*([绿黄红紫白])\s*(\d+)", priority=2, block=True)

@score_x.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"分数线\s*([绿黄红紫白])\s*(\d+)"
    match = re.match(regex, str(message)).groups()
    color, mid = match
    level_labels = ['绿', '黄', '红', '紫', '白']
    level_index = int(level_labels.index(color))
    print (level_index)
    img = await score_line(mid, level_index)

    await score_x.finish(img)


#-----s-score_line-----END