from nonebot import on_command, on_regex, get_driver
from nonebot.params import CommandArg, RegexGroup, Endswith, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
import requests

#内建模块
import math
import re
import os
import random
import base64
import json
import aiofiles

#加载工具组，以正确显示图片、获取曲目信息等
from .lib.tool import get_cover_len6_id, image_to_base64, is_pro_group, computeRaB50, get_cover_len4_id
#image_to_base64函数已不再使用，请择期删除相应代码 -- XiaoYan
from .lib.music import total_list, total_alias_list, plate_to_version, levelList, scoreRank , comboRank, syncRank, level_process_data, plate_process_xray
from .lib.MusicPic import MusicCover, music_info_pic, MusicPic
from .lib.score_line import score_line
from .lib.request_client import fetch_mai_best50_lxns, get_player_records, DIVING_AUTH
from .lib.mai_best_50 import mai_best50
from .lib.mai_score import mai_score, generate_tool
from .lib.mai_lv_score import song_data_filter, draw_mai_lv
from .lib.plate_map import VERSION_DF_MAP, NOW_VERSION

#依赖项
from typing import Tuple, Optional
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

    try:

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

    #try:
    #临时移上去了，不然没法捕捉到错误 -- XiaoYan

        #调整封面图片以正确显示
        #file_path = rf"src/static/mai/cover/UI_Jacket_{get_cover_len6_id(mid)}.png"
        file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid)}.png')

        if not os.path.exists(file_path):
            raise FileNotFoundError
        
        with open(file_path, "rb") as img_f:
            img_str = str(base64.b64encode(img_f.read()))
        img_ba64 = img_str[2: len(img_str) - 1]
        #由于无法正常构建图片的Base64信息，故此处代码被我重写以修复功能 -- XiaoYan

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
        
        await music_song.send(Message(f"""[CQ:image,file=base64://{img_ba64}]""" + 
                                      f"{music['id']}. {music['title']}\n" + 
                                      f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
谱面类型：{music['type']}
版本：{from_text}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}'''), reply_message = True)
    except (FileNotFoundError, Exception) as e:
        print(e)
        await music_song.send("歌曲不存在哦！", reply_message = True)
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
        await mai_chart.finish("难度输入不对哦！", reply_message = True)

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

        with open(file_path, "rb") as img_f:
            img_str = str(base64.b64encode(img_f.read()))
        img_ba64 = img_str[2: len(img_str) - 1]


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
        await mai_chart.send(Message(f"""[CQ:image,file=[CQ:image,file=base64://{img_ba64}]""" +
                                       f"{music['id']}. {music['title']}\n" +
                                       f'''谱面类型：{music['type']}
BPM：{music['basic_info']['bpm']}
难度：{level_name[level_index]} {level} ({ds:.1f})
TOTAL：{combo}\n''' +
note
                                       ), reply_message = True)
    except (FileNotFoundError, Exception) as e:
        print(e)
        await music_song.send("歌曲不存在哦！", reply_message = True)
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
        if music is None:
            await mai_id.finish('歌曲不存在哦！')
        print(music)
        msg = await music_info_pic(music)           
        await mai_id.send(msg, reply_message = True)
    else:
        await mai_id.send('歌曲不存在哦！', reply_message = True)
#-----s-id------END




#-----s-search-----START
search_music = on_regex(mai_regex + r"(查歌|search|bpm查歌|BPM查歌|曲师查歌|定数查歌|等级查歌|物量查歌)\s*([绿黄红紫白]?)\s*(.+?)(?:\s*-p\s*(\d+))?$")

#定数查歌相关
def handle_ds_search(color, name):
    level_labels = ['绿', '黄', '红', '紫', '白']
    return_list = []
    with open('src/plugins/maimai/music_data/maidxCN.json', 'r', encoding='utf-8') as f:
        json_info = json.load(f)
    if color:
        level_index = level_labels.index(color)
        for info in json_info:
            try:
                if info["ds"][level_index] == float(name):
                    return_list.append(info)
            except:
                continue
        return return_list
        #尝试查询用户指定难度，若没有跳过此首歌，有则循环(宴没DS字段所以必须要Try一下)
    for info in json_info:
        try:
            for level_info in info["ds"]:
                if level_info == float(name):
                    return_list.append(info)
        except:
            continue
    return return_list

    # if color:
    #     level_index = level_labels.index(color)
    #     return total_list.filter(ds=float(name), level_search=level_labels[level_index])
    # return total_list.filter(ds=float(name))

#等级查歌相关
def handle_level_search(color, name, total_list):
    level_labels = ['绿', '黄', '红', '紫', '白']
    if color:
        level_index = level_labels.index(color)
        return total_list.filter(level=name, level_search2=level_labels[level_index])
    return total_list.filter(level=name)

def return_true_num(res:list, mode:str, user_input:float|int|str) -> int:
    ture_num = 0
    if mode in ["search", "查歌", "曲师查歌", "BPM查歌", "bpm查歌"]:
        return len(res)
    elif mode == "定数查歌":
        for info in res:
            for ds_info in info["ds"]:
                if ds_info == float(user_input):
                    ture_num = ture_num + 1
        return ture_num
    elif mode == "等级查歌":
        for info in res:
            for level_info in info["level"]:
                if level_info == user_input:
                    ture_num = ture_num + 1
        return ture_num
    elif mode == "物量查歌":
        for info in res:
            for charts_info in info["charts"]:
                total_notes_temp = 0
                for notes_info in charts_info["notes"]:
                    total_notes_temp = total_notes_temp + notes_info
                if total_notes_temp == int(user_input):
                    ture_num = ture_num + 1
        return ture_num

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
        res = handle_ds_search(color, name)
    elif std == '等级查歌':
        res = handle_level_search(color, name, total_list)
    elif std == '物量查歌':
        res = total_list.filter(total=float(name))
        #print(res)
    #普通：不精确， 曲师：不精确， BPM：不精确， 定数：精确， 等级：精确， 物量：精确
    #此处的精确与否指的是是否精确到难度 -- XiaoYan
    true_charts_num = return_true_num(res, std, name)

    if true_charts_num == 0:
        await search_music.send("没有搜索到任何结果。", reply_message = True)
    elif true_charts_num == 1:
        music = total_list.by_id(res[0]['id'])
        msg = await music_info_pic(music)
        await mai_id.send(msg, reply_message = True)
    elif true_charts_num <= 15:
        search_result = ""
        search_result_list = []
        for music in sorted(res, key = lambda i: int(i['id'])):
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
            if not color and (std == '定数查歌' or std == '等级查歌' or std== '物量查歌'):
                difficulty_color = ''
                if std == '定数查歌':
                    for ds_index, ds_value in enumerate(music['ds']):
                        if ds_value == float(name):
                            difficulty_color = list(color_to_index.keys())[ds_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
                elif std == '等级查歌':
                    for level_index, level_value in enumerate(music['level']):
                        if level_value == name:
                            difficulty_color = list(color_to_index.keys())[level_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
                elif std == '物量查歌':
                    total_notes = []
                    for chart in music['charts']:
                        total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                    music["total_notes"] = total_notes
                    for total_index, total_value in enumerate(music["total_notes"]):
                        if total_value == float(name):
                            difficulty_color = list(color_to_index.keys())[total_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
            else:
                search_result_list.append(f"{music['id']}  {music['title']}\n")
        for single_song_info in search_result_list:
            search_result += single_song_info
        await search_music.send(f"共找到 {true_charts_num} 条结果：\n"+ search_result.strip(), reply_message = True)
    #理论上在前面计算真实谱面数量函数 return_true_num 的限制下应该是不会出现多算的情况的
    #直接沿用老代码试试 -- XiaoYan

    #后记：忘了DX谱的情况了，这下成澄闪了 -- XiaoYan
    else:
        per_page = 15
        total_pages = (true_charts_num + (per_page - 1)) // per_page
        #这里换成真实谱面数量来计算页面数量以免出错
        start = (page - 1) * per_page
        end = start + per_page
        search_result_list = []
        search_result = ""
        for music in sorted(res, key = lambda i: int(i['id'])):
            #这边相当于是先按顺序排序把所有的谱面全筛选出来,放进 search_result_list 这个列表里
            #把上面的res[start:end] 改为 -> res(整个列表)
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
            if not color and (std == '定数查歌' or std == '等级查歌' or std== '物量查歌'):
                difficulty_color = ''
                if std == '定数查歌':
                    for ds_index, ds_value in enumerate(music['ds']):
                        if ds_value == float(name):
                            difficulty_color = list(color_to_index.keys())[ds_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
                elif std == '等级查歌':
                    for level_index, level_value in enumerate(music['level']):
                        if level_value == name:
                            difficulty_color = list(color_to_index.keys())[level_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
                elif std == '物量查歌':
                    total_notes = []
                    for chart in music['charts']:
                        total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                    music["total_notes"] = total_notes
                    for total_index, total_value in enumerate(music["total_notes"]):
                        if total_value == float(name):
                            difficulty_color = list(color_to_index.keys())[total_index]
                            search_result_list.append(f"{music['id']}  {difficulty_color}  {music['title']}\n")
            else:
                search_result_list.append(f"{music['id']}  {music['title']}\n")
        for single_song_info in search_result_list[start:end]:
            #在这里对已经过滤过一遍的列表截断在正确的页面并将数据输出
            search_result += single_song_info
        await search_music.send(f"共找到 {true_charts_num} 条结果，第 {page}/{total_pages} 页:\n"+ search_result.strip() + f"\n使用参数 -p [页码] 来翻页", reply_message = True)
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
                with open(file_path, "rb") as img_f:
                    img_str = str(base64.b64encode(img_f.read()))
                img_ba64 = img_str[2: len(img_str) - 1]
                msg = Message(f"""[CQ:image,file=base64://{img_ba64}]""" + 
                                            f"\n{music_ds_a['id']}. {music_ds_a['title']}\n" + 
                                            f'''艺术家：{music_ds_a['basic_info']['artist']}
分类：{music_ds_a['basic_info']['genre']}
BPM：{music_ds_a['basic_info']['bpm']}
谱面类型：{music_ds_a['type']}
版本：{music_ds_a['basic_info']['from']}
等级：{', '.join(music_ds_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_ds_a['ds'])}''')
            await random_music.send(msg, reply_message = True)
        elif set == '等级':
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
                with open(file_path, "rb") as img_f:
                    img_str = str(base64.b64encode(img_f.read()))
                img_ba64 = img_str[2: len(img_str) - 1]
                msg = Message(f"""[CQ:image,file=base64://{img_ba64}]""" + 
                                            f"\n{music_level_a['id']}. {music_level_a['title']}\n" + 
                                            f'''艺术家：{music_level_a['basic_info']['artist']}
分类：{music_level_a['basic_info']['genre']}
BPM：{music_level_a['basic_info']['bpm']}
谱面类型：{music_level_a['type']}
版本：{music_level_a['basic_info']['from']}
等级：{', '.join(music_level_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_level_a['ds'])}''')
            await random_music.send(msg, reply_message = True)
        elif set == None:
            if pic:
                msg = await music_info_pic(total_list.random())
            else:
                music = total_list.random()
                mid3 = f"{music['id']}"
                file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len6_id(mid3)}.png')

                if not os.path.exists(file_path):
                    raise FileNotFoundError
                with open(file_path, "rb") as img_f:
                    img_str = str(base64.b64encode(img_f.read()))
                img_ba64 = img_str[2: len(img_str) - 1]
                msg = Message(f"""[CQ:image,file=base64://{img_ba64}]""" + 
                                            f"\n{music['id']}. {music['title']}\n" + 
                                            f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
谱面类型：{music['type']}
版本：{music['basic_info']['from']}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}''')
            await random_music.send(msg, reply_message = True)
    except Exception as e:
        await random_music.finish(f"指定的条件下没有任何歌曲。\n{e}", reply_message = True)
#-----s-random-----END


#-----s-mai_plate-----START
mai_plate = on_regex(mai_regex + r"牌子条件")

@mai_plate.handle()
async def _(event: Event, message: Message = EventMessage()):
    plate_path = os.path.join(MusicPic, rf'plate_rule.jpg')
    with open(plate_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
    await mai_plate.send(MessageSegment.image(f"base64://{base64_data}"), reply_message = True)
#-----s-mai_plate-----END
    
#-----s-rating_cal-----START
rating_cal = on_regex(mai_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?")

@rating_cal.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = mai_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?"
    match = re.search(regex, str(message)).groups()
    ds, ach = match
    # if not ds and not ach:
    #     await rating_cal.send("异常\n请输入正确的定数与达成率！")
    if not (1.0 <= float(ds) <= 15.0):
        await rating_cal.finish("请输入正确的定数与达成率！", reply_message = True)
    try:
        ra = computeRaB50(float(ds), float(ach))
        await rating_cal.send(f"定数 {float(ds)} \n在 {float(ach):.4f}% 的得分是 {ra}", reply_message = True)
    except ValueError:
        await rating_cal.send("请输入正确的定数与达成率！", reply_message = True)
    except TypeError:
        await rating_cal.send("请输入正确的定数与达成率！", reply_message = True)
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
        await alias_search.finish('没有搜索到任何结果。', reply_message = True)
    if len(data) != 1:
        msg = f"共找到 {len(data)} 条结果：\n"
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
        await alias_search.finish(msg, reply_message = True)
    music = total_list.by_id(str(data[0].song_id))
    await alias_search.finish(await music_info_pic(music), reply_message = True)
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
        await alias_search.finish('这首歌现在没有别名。', reply_message = True)
    
    await alias_look.finish(f"这首歌的别名有: \n{data}\n别名数据来自Xray Bot。", reply_message = True)
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

    await score_x.finish(img, reply_message = True)


#-----s-score_line-----END

#-----s-plate_process-----START
plate_process = on_regex(mai_regex + r'([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸星宙祭])([極极将舞神者]舞?)进度\s?', priority=1, block=True)

@plate_process.handle()
async def _(event: Event, message: Message = EventMessage(), match: Tuple = RegexGroup()):
    qqid = event.get_user_id()
    if f'{match[0]}{match[1]}' == '真将':
        await plate_process.finish()
    
    version_name = match[0]
    plate_type = match[1]

    data = plate_process_xray(version_name, qqid, plate_type, version_name)
    
    # data = await player_plate_data({'qq': qqid, 'version': ['maimai ORANGE PLUS']}, match)
    await plate_process.finish(data, reply_message = True)
#-----s-plate_process-----END

#-----s-level_process-----START
level_process = on_regex(mai_regex + r'\s?等级进度\s?([0-9]+\+?)\s?(.+)\s?(.+)?', priority=1,block=True)

@level_process.handle()
async def _(event: Event, message: Message = EventMessage(), match: Tuple = RegexGroup()):
    # try:
    #     with open("./data/bind_data.json", "r", encoding="utf-8") as f:
    #         bind_data = json.load(f)
    # except UnicodeDecodeError:
    #     with open("./data/bind_data.json", "r", encoding="utf-8-sig") as f:
    #         bind_data = json.load(f)
    # qqid = bind_data[str(event.user_id)]
    # nickname = ''

    # if match[0] not in levelList:
    #     await level_process.finish('输入不正确。', reply_message=True)
    # if match[1].lower() not in scoreRank + comboRank + syncRank:
    #     await level_process.finish('输入不正确。', reply_message=True)
    # elif match[2]:
    #     nickname = match[2]
    #     payload = {'username': match[2].strip()}
    # else:
    #     payload = {'username': qqid}


    # payload['version'] = list(set(version for version in plate_to_version.values()))

    # data = await level_process_data(payload, match, nickname)
    await level_process.finish("暂未支持", reply_message = True)
#-----s-level_process-----END

#-----b50-----START

type_map = {
    "SD":"standard",
    "DX":"dx"
}

def translate_df_to_lx(player_data):
    best = []
    for score in player_data:
        id = score['song_id']
        music_type = type_map.get(score['type'])
        if music_type == 'dx':
            id-=10000
        song_name = score['title']
        level = score['level']
        level_index = score['level_index']
        achievements = score['achievements']
        fc = score['fc'] if score['fc'] != "" else None
        fs = score['fs'] if score['fs'] != "" else None
        dx_score = score['dxScore']
        dx_rating = score['ra']
        rate = score['rate']
        best.append({
            "id": id,
            "song_name": song_name,
            "level": level,
            "level_index": level_index,
            "achievements": achievements,
            "fc": fc,
            "fs": fs,
            "dx_score": dx_score,
            "dx_rating": dx_rating,
            "rate": rate,
            "type": music_type
        })
    return best

def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


mai_b50 = on_command("/b50", priority=2, block=True)


@mai_b50.handle() 
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.user_id), 'b50': 1}
    else:
        payload = {'username': username.strip(), 'b50': 1}

    lx_data_v = {
        "data":{}
    }

    req = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/player",json=payload)
    player_data = req.json()
    try:
        standard_total = sum([score['ra'] for score in player_data['charts']['sd']])
        dx_total = sum([score['ra'] for score in player_data['charts']['dx']])
    except:
        await mai_b50.send("您还未绑定水鱼，请先绑定后再获取。", reply_message = True)
    lx_data_v['data']['standard_total'] = standard_total
    lx_data_v['data']['dx_total'] = dx_total
    lx_data_v['data']['standard'] = translate_df_to_lx(player_data['charts']['sd'])
    lx_data_v['data']['dx'] = translate_df_to_lx(player_data['charts']['dx'])
    course_rank  = player_data["additional_rating"]
    if course_rank >= 11:
        course_rank  = player_data["additional_rating"] + 1
    other_data = [player_data["nickname"], {'name': 'maimai DX Rating Information', 'color': 'Normal'}, course_rank, 0, {'name': player_data["plate"]}, None, None]

    b64Data = mai_best50.lxns(lx_data_v['data'], other_data)
    best50_message_list = [MessageSegment.reply(event.message_id),
                                    MessageSegment.image(f"base64://{str(image_to_base64(b64Data), encoding='utf-8')}")]
    await mai_b50.send(best50_message_list)
#-----b50-----END

#-----AP50------START
def filter_all_perfect_records(records):
    b15_all_perfect_records = []
    b35_all_perfect_records = []
    for item in records:
      if item['fc'] in ['ap', 'app']:
        if total_list.by_id(str(item['song_id'])).version == NOW_VERSION:
            b15_all_perfect_records.append(item)
        else:
            b35_all_perfect_records.append(item)

    b35_sorted_data = sorted(b35_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]

mai_ap_50 = on_command("/ap50", priority=2, block=True)


@mai_ap_50.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.user_id), 'b50': 1}
        payload_rec = {"qq": str(event.user_id)}
    else:
        payload = {'username': username.strip(), 'b50': 1}
        payload_rec = {'username': username.strip()}


    lx_data_v = {
        "data":{}
    }

    b50_req = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/player",json=payload)
    player_b50_data = b50_req.json()
    #获取玩家B50信息以获取基础信息
    player_records_data = await get_player_records(payload_rec)
    match player_records_data:
        case "Player Not Found":
            await mai_ap_50.finish("未找到该玩家。", reply_message = True)
        case "Private Setting":
            await mai_ap_50.finish("隐私设置。", reply_message = True)
        case "Data Lost":
            await mai_ap_50.finish("数据意外丢失，请联系管理员。", reply_message = True)
        case _:
            pass
    #获取玩家所有成绩信息准备过滤

    ap_b35_data, ap_b15_data = filter_all_perfect_records(player_records_data["records"])
    if len(ap_b35_data) == 0 and len(ap_b15_data) == 0:
        await mai_ap_50.finish("您还没有AP的成绩哦，请继续加油！", reply_message = True)

    player_data = {"additional_rating":player_b50_data["additional_rating"], "charts":{"dx":ap_b15_data, "sd":ap_b35_data},
                   "nickname":player_b50_data["nickname"],"plate":player_b50_data["plate"],"rating":player_b50_data["rating"],
                   "user_general_data":player_b50_data["user_general_data"],"username":player_b50_data["username"]}
    #手动构建一下关键信息
    
    standard_total = sum([score['ra'] for score in player_data['charts']['sd']])
    dx_total = sum([score['ra'] for score in player_data['charts']['dx']])

    lx_data_v['data']['standard_total'] = standard_total
    lx_data_v['data']['dx_total'] = dx_total
    lx_data_v['data']['standard'] = translate_df_to_lx(player_data['charts']['sd'])
    lx_data_v['data']['dx'] = translate_df_to_lx(player_data['charts']['dx'])
    course_rank  = player_data["additional_rating"]
    if course_rank >= 11:
        course_rank  = player_data["additional_rating"] + 1
    other_data = [player_data["nickname"], {'name': 'maimai DX Rating Information', 'color': 'Normal'}, course_rank, 0, {'name': player_data["plate"]}, None, None]

    b64Data = mai_best50.lxns(lx_data_v['data'], other_data)
    ap50_message_list = [MessageSegment.reply(event.message_id),
                                    MessageSegment.image(f"base64://{str(image_to_base64(b64Data), encoding='utf-8')}")]
    await mai_ap_50.send(ap50_message_list)
#-----AP50------END

#-----Single_Score-----START
mai_single_score = on_regex(r"^/mai score (.+)$", priority=1, block=True)


@mai_single_score.handle()
async def _(event: Event):
    user_qqid = str(event.get_user_id())
    with open("./src/plugins/maimai/music_data/maidxCN-Today.json", "r", encoding = "utf-8") as f:
        music_data = json.load(f)
    match = re.match(r"^/mai score (.+)$", event.get_plaintext())
    user_song_id = match.group(1)
    if user_song_id not in music_data.keys():
        await mai_single_score.finish("ID错误或不存在。", reply_message = True)
    elif int(user_song_id) >= 100000:
        await mai_single_score.finish("宴会场请通过分数列表查询。", reply_message = True) 
    #ID筛选完毕

    get_status = await get_player_records({"qq": user_qqid})
    match get_status:
        case "Player Not Found":
            await mai_single_score.finish("未找到该玩家。", reply_message = True)
        case "Private Setting":
            await mai_single_score.finish("隐私设置。", reply_message = True)
        case "Data Lost":
            await mai_single_score.finish("数据意外丢失，请联系管理员。", reply_message = True)
        case _:
            pass
    #获取用户数据

    filter_song_data = []
    for single_song_data in get_status["records"]:
        if str(single_song_data["song_id"]) == user_song_id:
            filter_song_data.append(single_song_data)
    if len(filter_song_data) == 0:
        await mai_single_score.finish("您没有此曲目的成绩。", reply_message = True)
    #过滤用户成绩
    
    translate_data = generate_tool.translate_fish2lx(filter_song_data)
    b64Data = mai_score.lxns(translate_data, music_data)
    await mai_single_score.send(MessageSegment.image(f"base64://{b64Data}"), reply_message = True)
#-----Single_Score-----END

#-----lv_score-----START
mai_lv_score = on_regex(r"^/mai 分数列表 (.+?)(?: -p (\d+))?$", priority=1, block=True)


@mai_lv_score.handle()
async def _(event: Event):
    plain_text = event.get_plaintext()
    matchs = re.match(r"^/mai 分数列表 (.+?)(?: -p (\d+))?$", plain_text)
    user_level = matchs.group(1)
    user_page = matchs.group(2) if matchs.group(2) else 1
    if user_page == None:
        user_page == 1
    user_qqid = str(event.get_user_id())

    with open("./src/plugins/maimai/music_data/maidxCN-Today.json", "r", encoding = "utf-8") as f:
        music_data = json.load(f)

    get_status = await get_player_records({"qq": user_qqid})
    match get_status:
        case "Player Not Found":
            await mai_lv_score.finish("未找到该玩家。", reply_message = True)
        case "Private Setting":
            await mai_lv_score.finish("隐私设置。", reply_message = True)
        case "Data Lost":
            await mai_lv_score.finish("数据意外丢失，请联系管理员。", reply_message = True)
        case _:
            pass
    
    draw_data = song_data_filter(get_status, user_level, user_page, music_data, user_level)
    match draw_data:
        case "Data is Empty":
            await mai_lv_score.finish("您查询的等级没有成绩。", reply_message = True)
        case "Page Error":
            await mai_lv_score.finish("页码错误。", reply_message = True)
        case _:
            pass

    b64Data = draw_mai_lv(draw_data, music_data)
    await mai_lv_score.send(MessageSegment.image(f"base64://{b64Data}"), reply_message = True)
#-----lv_score-----END

#-----course-----START
mai_course = on_command("/mai 段位认定", priority=5)
@mai_course.handle()
async def _():
        with open("./src/static/mai/pic/mai-course.png", 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        await mai_course.send(MessageSegment.image(f"base64://{base64_data}"), reply_message = True)
    
mai_shincourse = on_command("/mai 真段位认定", priority=5)
@mai_shincourse.handle()
async def _():
        with open("./src/static/mai/pic/mai-shincourse.png", 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        await mai_shincourse.send(MessageSegment.image(f"base64://{base64_data}"), reply_message = True)
#-----course-----END