from nonebot import on_command, on_regex
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from nonebot.rule import *
from nonebot.adapters.onebot.v11 import *
from nonebot.utils import *

from .lib.MusicPic import MusicCover, music_info_pic, MusicPic
from .lib.tool import *
from .lib.chunithm_music import *
from .lib.image import *
from .lib.chart import get_chunithm_chart
from .lib.chunithm_score_list import chu_score_list

import aiofiles
import re
import os
import base64
import json
import math

from .json_update import *

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .lib.chunithm_best_30 import generate_by_lx, generate_by_df

chu_regex = r'/chu\s*'

best_30_pic = on_command('/b30' , aliases={'chub30','chu b30','cb30'}, priority=5)

@best_30_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message)
    if username:
        img, success = await generate_by_df({"username": username})
    
    else:
        user_id = str(event.get_user_id()) 
        img, success = await generate_by_df({"qq": user_id})
    if int(success) == 400:
        await best_30_pic.send("您还未绑定水鱼，请先绑定后再获取。", reply_message = True)
    await best_30_pic.send(Message([
                MessageSegment("image", {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
        })
    ]), reply_message = True)

def getSongCover(songId):
    cover = Image.open(rf"src\static\chu\cover\CHU_UI_Jacket_{get_cover_len4_id(songId)}.png")
    cover_rgb = cover.convert('RGB')
    return cover_rgb

#-----s-chusong------START
music_song = on_regex(chu_regex + r"(song)\s*(\d+)")

@music_song.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"(song)\s*(\d+)"
    match = re.match(regex, str(message))
    groups = match.groups()
    mid = int(groups[1])
    music = total_list.by_id(mid)
    print(music)
    from_text = music['basic_info']['from']


    try:

        img = getSongCover(mid)
        # base64_data = base64.b64encode(byte_data).decode()
        # #判断版本开头是否为maimai 或 maimai でらっくす
        # if from_text == "maimai PLUS":
        #     from_text = from_text
        # elif from_text.startswith("舞萌"):
        #     from_text = from_text
        # elif from_text.startswith("maimai "):
        #     from_text = from_text.split("maimai ", 1)[1]
        # else:
        #     from_text = from_text  

            
        await music_song.send(Message(f"""[CQ:image,file=base64://{str(image_to_base64(img), encoding='utf-8')}]""" + 
                                      f"\n{music['id']}. {music['title']}\n" + 
                                      f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
版本：{from_text}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}'''), reply_message = True)
    except (FileNotFoundError, Exception) as e:
        print(e)
        await music_song.send("歌曲不存在哦！", reply_message = True)
#-----s-chusong------END


#-----s-chuchart------START
chu_chart = on_regex(chu_regex + r"(chart)\s*([绿黄红紫黑]?)\s*(\d+)")

@chu_chart.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"(chart)\s*([绿黄红紫黑]?)\s*(\d+)"
    match = re.match(regex, str(message))

    #判断表达式第二组是否在level_labels内，若不在则终止命令
    level_labels = ['绿', '黄', '红', '紫', '黑']
    if match is None or match.group(2) not in level_labels:
        await chu_chart.finish("难度输入不对哦！", reply_message = True)

    groups = match.groups()
    level_index = level_labels.index(groups[1])
    level_name = ['BASIC', 'ADVANCED', 'EXPERT', 'MASTER', 'ULTIMA']
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


        #封面图
        img = getSongCover(mid)

        music = song_get(mid)
        #print(music)
        error_log = music
        #from_ver = total_list.by_id(id)
        #music = total_list.by_id(mid)
        for num, difficulty in enumerate(music.difficulties):
            if num == level_index:
                #print(music.difficulties)
                chart = difficulty["notes"][0]
                #chart = music['charts'][level_index]
                cha = difficulty['note_designer']
                ds = difficulty['level_value']
                level = difficulty['level']
            #print(num)
            #print(difficulty)
        #combo = sum(chart['notes'])

                note = f'''TOTAL：{chart.total}
TAP：{chart.tap}
HOLD：{chart.hold}
SLIDE：{chart.slide}
AIR：{chart.air}
FLICK：{chart.flick}
谱师：{cha}'''
                print(note)
        await chu_chart.send(Message(f"""[CQ:image,file=base64://{str(image_to_base64(img), encoding='utf-8')}]""" +
                                       f"\n{music.id}. {music.title}\n" +
                                       f'''BPM：{music.bpm}
难度：{level_name[level_index]} {level} ({ds})\n''' +
note
                                       ), reply_message = True)
    except (FileNotFoundError, Exception) as e:
        print(e)
        await chu_chart.send("歌曲不存在哦！", reply_message = True)
#-----s-chuchart------END




#-----s-search-----START
search_music = on_regex(chu_regex + r"(查歌|search|bpm查歌|BPM查歌|曲师查歌|定数查歌|等级查歌|物量查歌)\s*([绿黄红紫白]?)\s*(.+?)(?:\s*-p\s*(\d+))?$")

#定数查歌相关
def handle_ds_search(color, name, total_list):
    level_labels = ['绿', '黄', '红', '紫', '黑']
    if color:
        level_index = level_labels.index(color)
        return total_list.filter(ds=float(name), level_search=level_labels[level_index])
    return total_list.filter(ds=float(name))

#等级查歌相关
def handle_level_search(color, name, total_list):
    level_labels = ['绿', '黄', '红', '紫', '黑']
    if color:
        level_index = level_labels.index(color)
        return total_list.filter(level=name, level_search2=level_labels[level_index])
    return total_list.filter(level=name)

@search_music.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"(查歌|search|bpm查歌|BPM查歌|曲师查歌|定数查歌|等级查歌|物量查歌)\s*([绿黄红紫白]?)\s*(.+?)(?:\s*-p\s*(\d+))?$"
    match = re.match(regex, str(message)).groups()

    std, color, name, page = match
    page = int(page) if page else 1
    if name.strip() == "":
        return
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
        await search_music.send("没有搜索到任何结果。", reply_message = True)
    elif len(res) == 1:
        #music = total_list.by_id(res[0]['id'])
        from_ver = total_list.by_id(res[0]['id'])
        print(from_ver)       
        music = song_get(res[0]['id'])
        print(music)
        msg = await music_info_pic(music, from_ver)
        await chu_id.send(msg, reply_message = True)
    elif len(res) <= 15:
        search_result = ""
        temp = None
        for music in sorted(res, key = lambda i: int(i['id'])):
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '黑': 4}
            if not color and (std == '定数查歌' or std == '等级查歌' or std== '物量查歌'):
                difficulty_color = ''
                if std == '定数查歌':
                    print(music['ds'])
                    for ds_index, ds_value in enumerate(music['ds']):
                        if ds_value == float(name):
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
        await search_music.send(f"共找到 {len(res)} 条结果：\n"+ search_result.strip(), reply_message = True)
    else:
        per_page = 15
        total_pages = math.ceil(len(res) / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        search_result = ""
        temp = None
        for music in sorted(res[start:end], key = lambda i: int(i['id'])):
            color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '黑': 4}
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
        await search_music.send(f"共找到 {len(res)} 条，第 {page}/{total_pages} 页:\n"+ search_result.strip() + f"\n使用参数 -p [页码] 来翻页", reply_message = True)
#-----s-search-----END
        

#-----s-id------START
chu_id = on_regex(chu_regex + r"id\s*(\d+)")

@chu_id.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"id\s*(\d+)"
    match = re.match(regex, str(message))
    groups = match.groups()
    id = int(groups[0])
    music_check = total_list.by_id(id)

    if music_check:                      
        try:
            music = song_get(id)
            error_log = music
            from_ver = total_list.by_id(id)
            msg = await music_info_pic(music, from_ver) 
        except Exception :
            msg = f"\n出错了，请稍后重试或联系管理员。\n{error_log}"

        await chu_id.send(msg, reply_message = True)
    else:
        await chu_id.send('歌曲不存在哦！', reply_message = True)
#-----s-id------END

#-----s-random-----START
random_music = on_regex(chu_regex + r"(定数|等级)?\s*随歌\s*([绿黄红紫黑])?\s*([0-9]+\.?[0-9]*[+]?)?\s*(-pic)?")



@random_music.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"(定数|等级)?\s*随歌\s*([绿黄红紫黑])?\s*([0-9]+\.?[0-9]*[+]?)?\s*(-pic)?"
    match = re.search(regex, str(message)).groups()
    set, level, ds, pic = match
    print(match)
    print(pic)
    print(level)
    print(ds)
    try:
        if level == " ":
            level = None
        if set == '定数':
            music_ds = total_list.filter(ds=float(ds))
            if level:
                level_labels = ['绿', '黄', '红', '紫', '黑']
                level_index = level_labels.index(level)
                music_l1 = total_list.filter(level_search=level_labels[level_index], ds=float(ds))
                music_ds_a = random.choice(music_l1)
            else:
                music_ds_a = random.choice(music_ds)
            mid = f"{music_ds_a['id']}"
            if pic:
                mid_int = int(mid)
                from_ver = total_list.by_id(mid_int)
                song_ds = song_get(mid)
                if level:
                    msg = await music_info_pic(song_ds, from_ver)
                else:
                    msg = await music_info_pic(song_ds, from_ver)
            else:
                img = getSongCover(mid)
                #file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len4_id(mid)}.png')

                # file = Image.open(file_path)
                # #调整封面图片以正确显示
                # buffer = BytesIO()
                # file.save(buffer, format='PNG')  
                # byte_data = buffer.getvalue()
                msg = Message(f"""[CQ:image,file=base64://{str(image_to_base64(img), encoding='utf-8')}]""" + 
                                            f"\n{music_ds_a['id']}. {music_ds_a['title']}\n" + 
                                            f'''艺术家：{music_ds_a['basic_info']['artist']}
分类：{music_ds_a['basic_info']['genre']}
BPM：{music_ds_a['basic_info']['bpm']}
版本：{music_ds_a['basic_info']['from']}
等级：{', '.join(music_ds_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_ds_a['ds'])}''')
            await random_music.send(msg, reply_message = True)
        elif set == '等级':
            music_level = total_list.filter(level=ds)
            if level:
                level_labels2 = ['绿', '黄', '红', '紫', '黑']
                level_index2 = level_labels2.index(level)
                music_l2 = total_list.filter(level_search2=level_labels2[level_index2], level=ds)
                music_level_a = random.choice(music_l2)
            else:
                music_level_a = random.choice(music_level)
            mid2 = f"{music_level_a['id']}"
            if pic:
                song_level = song_get(mid2)
                mid2_int = int(mid2)
                from_ver = total_list.by_id(mid2_int)
                if level:
                    msg = await music_info_pic(song_level, from_ver)
                else:
                    msg = await music_info_pic(song_level, from_ver)
            else:
                img2 = getSongCover(mid2)
                #file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len4_id(mid2)}.png')

                msg = Message(f"""[CQ:image,file=base64://{str(image_to_base64(img2), encoding='utf-8')}]""" + 
                                            f"\n{music_level_a['id']}. {music_level_a['title']}\n" + 
                                            f'''艺术家：{music_level_a['basic_info']['artist']}
分类：{music_level_a['basic_info']['genre']}
BPM：{music_level_a['basic_info']['bpm']}
版本：{music_level_a['basic_info']['from']}
等级：{', '.join(music_level_a['level'])}
定数：{', '.join(f'{d:.1f}' for d in music_level_a['ds'])}''')
            await random_music.send(msg, reply_message = True)
        elif set == None:
            music = total_list.random()
            print(music)
            mid3 = f"{music['id']}"
            print(mid3)
            if pic:
                music_none = song_get(music['id'])
                mid3_int = int(mid3)
                from_ver = total_list.by_id(mid3_int)
                msg = await music_info_pic(music_none,from_ver)
            else:
                
                img3 = getSongCover(mid3)
                #file_path = os.path.join(MusicCover, rf'UI_Jacket_{get_cover_len4_id(mid3)}.png')

                msg = Message(f"""[CQ:image,file=base64://{str(image_to_base64(img3), encoding='utf-8')}]""" + 
                                            f"\n{music['id']}. {music['title']}\n" + 
                                            f'''艺术家：{music['basic_info']['artist']}
分类：{music['basic_info']['genre']}
BPM：{music['basic_info']['bpm']}
版本：{music['basic_info']['from']}
等级：{', '.join(music['level'])}
定数：{', '.join(f'{d:.1f}' for d in music['ds'])}''')
            await random_music.send(msg, reply_message = True)    
    except Exception as e:
        await random_music.finish(f"没有搜索到任何结果。\n{e}", reply_message = True)
#-----s-random-----END

#-----s-alias-----START
alias_search = on_regex(chu_regex + r"找歌\s*(.+)")

@alias_search.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"找歌\s*(.+)"
    match_regex = re.match(regex, str(event.get_message())).groups()
    name = match_regex[0]
    data = total_alias_list.by_alias(name)
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
    music = song_get(str(data[0].song_id))
    from_ver = total_list.by_id(int(data[0].song_id))
    await alias_search.finish(await music_info_pic(music, from_ver), reply_message = True)
#-----s-alias-----END

#-----s-lookalia-----START
alias_look = on_regex(chu_regex + r"查看别名\s*(.+)")

@alias_look.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"查看别名\s*(.+)"
    match_regex = re.match(regex, str(event.get_message())).groups()
    mid = int(match_regex[0])
    data = total_alias_list.by_id(mid)
    if not data:
        await alias_search.finish('这首歌现在没有别名。\n您可以前往落雪咖啡屋的曲目别名投票申请创建曲目别名。', reply_message = True)
    
    await alias_look.finish(f"这首歌的别名有: \n{data}\n别名数据来自落雪咖啡屋。", reply_message = True)
#-----s-lookalia-----END

#-----s-rating_cal-----START
rating_cal = on_regex(chu_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?")

@rating_cal.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = chu_regex + r"ra计算\s*([0-9]+\.?[0-9]*[+]?)?\s*([0-9]+\.?[0-9]*[+]?)?"
    match = re.search(regex, str(message)).groups()
    ds, ach = match
    # if not ds and not ach:
    #     await rating_cal.send("\n异常\n请输入正确的定数与达成率！")
    if not (1.0 <= float(ds) <= 15.4):
        await rating_cal.finish("请输入正确的定数与达成率！", reply_message = True)
    try:
        ra = computeRaB30(float(ds), int(ach))
        f_ra = truncate_f(ra,2)
        await rating_cal.send(f"定数 {float(ds)} \n在 {int(ach)} 的得分是 {f_ra}", reply_message = True)
    except ValueError:
        await rating_cal.send("请输入正确的定数与达成率！", reply_message = True)
    except TypeError:
        await rating_cal.send("请输入正确的定数与达成率！", reply_message = True)
#-----s-rating_cal-----END

# searchChartInfo = on_regex(r"^(中二|c|chu)\s*c?查谱([0-9]+)", permission=GROUP, priority=1, block=False)



# @searchChartInfo.handle()
# async def searchChartInfo_main(matchers: searchChartInfo, event: GroupMessageEvent):
#     await searchChartInfo.send("正在生成歌曲谱面图片，少女祈祷中...（一般需要3-5分钟时间，请耐心等待）")
#     cwd = os.getcwd()
#     difficulty = "master"
#     if str(event.message).lower().endswith(("ma", "master")):
#         difficulty = "master"
#     elif str(event.message).lower().endswith(("expert", "ex")):
#         difficulty = "expert"
#     musicid = re.sub(r"^(中二|c|chu)\s*c?查谱|\s+", "", str(event.message), flags=re.I)
#     musicid = re.sub(r"ma|master|expert|ex$", "", musicid, flags=re.I)
#     result = await get_chunithm_chart(musicid, difficulty)
#     if result is not None:
#         title, image_url = result
#         with open(os.path.join(cwd, image_url), 'rb') as f:
#             img_data = f.read()
#         base64_img = base64.b64encode(img_data).decode('utf-8')
#         msg = Message(f"[CQ:image,file=base64://{base64_img},cache=0]")
#     else:
#         msg = Message(f"生成图片出错，请重试，若重试多次无效，请联系老父亲")
#     await searchChartInfo.finish(msg, reply_message=True)


# def inner_level_q(ds1, ds2=None):
#     result_set = []
#     diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'Ult']
#     if ds2 is not None:
#         music_data = total_list.filter(ds=(ds1, ds2))
#     else:
#         music_data = total_list.filter(ds=ds1)
#     for music in sorted(music_data, key = lambda i: int(i['id'])):
#         for i in music.diff:
#             result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
#     return result_set

# inner_level = on_command('中二定数查歌', aliases={'c定数查歌','chu 定数查歌','chu定数查歌'})


# @inner_level.handle()
# async def _(event: Event, message: Message = CommandArg()):
#     argv = str(message).strip().split(" ")
#     if len(argv) > 2 or len(argv) == 0:
#         await inner_level.finish("命令格式为\n/chu 定数查歌 <定数>\n/chu 定数查歌 <定数下限> <定数上限>")
#         return
#     if len(argv) == 1:
#         result_set = inner_level_q(float(argv[0]))
#     else:
#         result_set = inner_level_q(float(argv[0]), float(argv[1]))
#     if len(result_set) > 100:
#         await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
#         return
#     s = ""
#     for elem in result_set:
#         s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
#         msg = s.strip()

#     await inner_level.finish(Message([
#             MessageSegment("image", {
#                 "file": f"base64://{str(image_to_base64(TextToImg(msg)), encoding='utf-8')}"
#             })
#         ]))

#-----chu_score_list start-----
chu_lv_score = on_regex(r"^/chu 分数列表 (.+?)(?: -p (\d+))?$", priority = 1, block = True)


@chu_lv_score.handle()
async def _(event: Event):
    plain_text = event.get_plaintext()
    matchs = re.match(r"^/chu 分数列表 (.+?)(?: -p (\d+))?$", plain_text)
    user_level = matchs.group(1)
    user_page = matchs.group(2) if matchs.group(2) else 1
    if user_page == None:
        user_page == 1
    user_qqid = str(event.get_user_id())

    b64_data = await chu_score_list(qq = user_qqid, level = user_level, page = user_page)
    await chu_lv_score.send(MessageSegment.image(f"base64://{b64_data}"), reply_message = True)
#-----chu_score_list end-----