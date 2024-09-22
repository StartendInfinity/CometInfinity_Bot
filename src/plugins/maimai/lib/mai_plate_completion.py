# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw,ImageFont
from src.plugins.maimai.lib.music import total_list
from src.lib.client.diving_fish_client import df_client
from src.plugins.maimai.lib.music_data_counter import MusicDataCounter
from pathlib import Path
import os
from src.plugins.maimai.lib.plate_map import MAIPLATE_FILE_ID_MAP, VERSION_MAP, VERSION_DF_MAP, MAI_DELETED_MUSIC_REM,MAI_DELETED_MUSIC_Normal
from src.plugins.maimai.lib import completion_utils as utils
import asyncio

COMPLETION_BASE_PATH = "src/static/mai/plate_completion_base"
PLATE_BASE_PATH = "src/static/mai/b50/plate"
FONT_PATH = "src/static/mai/pic/font"
NEW_LEVEL_STATUS_TABLE_PATH = "src/static/mai/plate_completion"

fc_enum = ['', 'fc', 'fcp', 'ap', 'app']
fs_enum = ['', 'fs', 'fsp', 'fsd', 'fsdp','sync']
star_enum = ['','1星','2星','3星','4星','5星']
rank_min_achievements_map = {
    'sssp':100.5,
    'sss':100,
    'ssp':99.5,
    'ss':99,
    'sp':98,
    's':97,
    'clear':80
}

row_count = 10

cover_width = 80
cover_height = 80+20

# 纵间距
inds_vertical_spacing = 20
# 横间距
inds_horizontal_spacing = 16
ds_vertical_spacing = 20


async def query_user_plate_data(music_data:dict,versions,qq:int = None,user_name:str = None):
    user_plate_music_data:dict = await df_client.maimaidxprober_query_plate(version_list=versions,qq=qq,username=user_name)
    user_plate_music_data = user_plate_music_data['verlist']
    for music_score in user_plate_music_data:
        key = f"{music_score['id']}-{music_score['level_index']}"
        music = music_data.get(key,{})
        music['is_played'] = True
        music.update(music_score)
    return music_data
    # print(user_plate_music_data)
    # finishs = r.json()
    # version_song_info = {}
    # for song in version_list:
    #     version_song_info[song.id] = {}
    #     for index ,level in enumerate(song['level']):
    #         version_song_info[song.id][index] = get_music_info(finishs,int(song.id),index)
    # return version_song_info

def generate_t_music_data(version:str,is_mai_version):
    musiclist, musiclist_rem = total_list.by_versions_for_cn(VERSION_MAP[version],is_mai_version=is_mai_version)
    music_data = {}
    for music in musiclist:
        for level_index in [0,1,2,3]:
            key = f"{music.id}-{level_index}"
            music_data[key] = {
                "id":music.id,
                "level_index":level_index,
                "is_played": False
            }
    for music in musiclist_rem:
        key = f"{music.id}-4"
        music_data[key] = {
            "id":music.id,
            "level_index":4,
            "is_played": False
        }
    return music_data


def generate_base_level_image(version:str,is_mai_version:bool,default_song_list:dict):
    music_content_hight = 18
    for level,musics in default_song_list.items():
        if level:
            cols = utils.calculate_cols(len(musics),row_count)
            music_content_hight += ( cols * (cover_height+inds_vertical_spacing) ) - inds_vertical_spacing
            music_content_hight += ds_vertical_spacing
    music_content_hight -= ds_vertical_spacing*2
    plate_base_image = Image.new("RGBA",(1280,music_content_hight),(255,255,255,255))
    music_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/middle.png").convert('RGBA')
    plate_base_image.paste(music_image,(0,0),music_image)

    init_x = 230
    init_y = 240-222
    x_point = init_x
    y_point = init_y
    for level,musics in default_song_list.items():
        if musics:
            line_count = 0
            level = level.replace('+','p')
            level_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/lv_{level}.png").convert('RGBA')
            level_image = level_image.resize((100, 45), Image.ANTIALIAS)
            plate_base_image.paste(level_image,(100,y_point + (262-240)),level_image)
            for index,music_id in enumerate(musics):
                music_box = Image.new("RGBA",(80,100),(255,255,255,255))
                song_id_6 = utils.get_cover_len6_id(music_id)
                cover_path = f"./src/static/mai/cover/UI_Jacket_{song_id_6}.png"
                cover = Image.open(cover_path).convert('RGBA')
                cover = cover.resize((80, 80), Image.ANTIALIAS)
                music_box.paste(cover, (0, 0), cover)
                plate_base_image.paste(music_box,(x_point,y_point),music_box)

                x_point += cover_width + inds_horizontal_spacing
                line_count += 1
                if line_count == row_count and index+1 != len(musics):
                    y_point += cover_height + inds_vertical_spacing
                    x_point = init_x
                    line_count = 0
            x_point = init_x
            if index != len(musics) -1:
                y_point -= inds_vertical_spacing
                y_point += ds_vertical_spacing
            else:
                y_point += cover_height + ds_vertical_spacing
    return plate_base_image
    # plate_base_image.show()

def merge_full_image(version:str,is_mai_version:bool,default_song_list:dict):
    plate_base_image = generate_base_level_image(version,is_mai_version,default_song_list)
    base_w,base_h = plate_base_image.size
    top_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/up.png").convert('RGBA')
    down_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/down.png").convert('RGBA')
    total_height = base_h + 222 + 222
    full_image = Image.new("RGBA",(1280,total_height),(255,255,255,255))
    full_image.paste(top_image,(0,0),top_image)
    full_image.paste(plate_base_image,(0,222),plate_base_image)
    full_image.paste(down_image,(0,222+base_h),down_image)
    return full_image

def generate_default_song_list(version:str,is_mai_version:bool):
    musiclist, musiclist_rem = total_list.by_versions_for_cn(VERSION_MAP[version],is_mai_version=is_mai_version)
    default_song_list = {"15":[],"14+":[],"14":[],"13+":[],"13":[],"12+":[],"12":[],"11+":[],"11":[],"10+":[],"10":[],"9+":[],"9":[],"8+":[],"8":[],"7+":[],"7":[],"6":[],"5":[],"4":[],"3":[],"2":[],"1":[]}

    if is_mai_version:
        for music in musiclist_rem:
            level= music.level[4]
            default_song_list[level].append(music.id)
    else:
        for music in musiclist:
            level= music.level[3]
            default_song_list[level].append(music.id)
    return default_song_list


def draw_user_music_box(music_id,user_plate_music_data:dict,is_mai_version:bool,plate_mode:str):
    level_index = 4 if is_mai_version else 3
    is_show_ok = True
    music_box = Image.new("RGBA",(80,100),(255,255,255,0))
    if not is_mai_version:
        basic_ok_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/basic-ok.png").convert('RGBA').resize((20,8))
        advanced_ok_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/advanced-ok.png").convert('RGBA').resize((20,8))
        expert_ok_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/expert-ok.png").convert('RGBA').resize((20,8))
        master_ok_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/master-ok.png").convert('RGBA').resize((20,8))
        ok_image_map = {
            0:basic_ok_image,
            1:advanced_ok_image,
            2:expert_ok_image,
            3:master_ok_image
        }
        for level_index in [0,1,2,3]:
            key = f"{music_id}-{level_index}"
            user_music_data = user_plate_music_data[key]
            if user_music_data['is_played']:
                if plate_mode == '极':
                    ok_status = user_music_data['fc'] in ['fc','fcp','ap','app']
                if plate_mode == '将':
                    ok_status = user_music_data['achievements'] >= 100
                if plate_mode == '神':
                    ok_status = user_music_data['fc'] in ['ap','app']
                if plate_mode == '舞舞':
                    ok_status = user_music_data['fs'] in ['fsd','fsdp']
                if ok_status:
                    ok_image = ok_image_map[level_index]
                    music_box.paste(ok_image,(level_index*20,80),ok_image)
                else:
                    if is_show_ok:
                        is_show_ok = False
            else:
                if is_show_ok:
                        is_show_ok = False
    else:
        remaster_ok_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/4x/remaster-ok.png").convert('RGBA').resize((80,8))

        is_show_ok = True

        for level_index in [0,1,2,3,4]:
            key = f"{music_id}-{level_index}"
            user_music_data = user_plate_music_data[key]
            if user_music_data['is_played']:
                if plate_mode == '极':
                    ok_status = user_music_data['fc'] in ['fc','fcp','ap','app']
                if plate_mode == '将':
                    ok_status = user_music_data['achievements'] >= 100
                if plate_mode == '神':
                    ok_status = user_music_data['fc'] in ['ap','app']
                if plate_mode == '舞舞':
                    ok_status = user_music_data['fs'] in ['fsd','fsdp']
                if plate_mode == '者':
                    ok_status = user_music_data['achievements'] >= 80

                if ok_status:
                    if level_index == 4:
                        music_box.paste(remaster_ok_image,(0,80),remaster_ok_image)
                if not ok_status:
                    if is_show_ok:
                        is_show_ok = False
            else:
                if is_show_ok:
                        is_show_ok = False


    return music_box,is_show_ok
    



def draw_user_music_image(base_image:Image.Image,default_song_list:dict,user_music_data:dict,is_mai_version:bool,plate_mode:str):
    sss_cover_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/sss-cover.png").convert('RGBA').resize((80,80))
    fc_cover_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/fc-cover.png").convert('RGBA').resize((80,80))
    ap_cover_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/ap-cover.png").convert('RGBA').resize((80,80))
    fsd_cover_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/fsd-cover.png").convert('RGBA').resize((80,80))
    a_cover_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/a-cover.png").convert('RGBA').resize((80,80))
    cover_map = {
        '将':sss_cover_image,
        '极':fc_cover_image,
        '神':ap_cover_image,
        '舞舞':fsd_cover_image,
        '者':a_cover_image
    }



    init_x = 230
    init_y = 240
    x_point = init_x
    y_point = init_y
    for level,musics in default_song_list.items():
        if musics:
            line_count = 0
            for index,music_id in enumerate(musics):
                music_box,is_show_ok = draw_user_music_box(music_id,user_music_data,is_mai_version,plate_mode)
                if is_show_ok:
                    cover_image = cover_map[plate_mode]
                    music_box.paste(cover_image,(0,0),cover_image)
                base_image.paste(music_box,(x_point,y_point),music_box)

                x_point += cover_width + inds_horizontal_spacing
                line_count += 1
                if line_count == row_count and index+1 != len(musics):
                    y_point += cover_height + inds_vertical_spacing
                    x_point = init_x
                    line_count = 0
            x_point = init_x
            if index != len(musics) -1:
                y_point -= inds_vertical_spacing
                y_point += ds_vertical_spacing
            else:
                y_point += cover_height + ds_vertical_spacing
    return base_image


def music_count(user_plate_music_data:dict):
    basic_counter = MusicDataCounter()
    advanced_counter = MusicDataCounter()
    expert_counter = MusicDataCounter()
    master_counter = MusicDataCounter()
    rem_master_counter = MusicDataCounter()
    counter_map = {
        0:basic_counter,
        1:advanced_counter,
        2:expert_counter,
        3:master_counter,
        4:rem_master_counter,
    }
    for user_music in user_plate_music_data.values():
        counter = counter_map[user_music['level_index']]
        counter.append_music(user_music,user_music['is_played'])
    return basic_counter,advanced_counter,expert_counter,master_counter,rem_master_counter


def draw_user_total_counter(base_image:Image.Image,plate_mode,is_mai_version:bool,basic_counter,advanced_counter,expert_counter,master_counter,rem_master_counter):
    max_level = 5 if is_mai_version else 4
    counter_map = {
        0:basic_counter,
        1:advanced_counter,
        2:expert_counter,
        3:master_counter,
        4:rem_master_counter,
    }
    if is_mai_version:
        level_config = {
            0:{'y':35,"color":"#6fd43d"},
            1:{'y':62,"color":"#f8b709"},
            2:{'y':89,"color":"#ff78a1"},
            3:{'y':116,"color":"#9f51dc"},
            4:{'y':143,"color":"#e4c5ff"},
        }
    else:
        level_config = {
            0:{'y':43,"color":"#6fd43d"},
            1:{'y':70,"color":"#f8b709"},
            2:{'y':97,"color":"#ff78a1"},
            3:{'y':124,"color":"#9f51dc"},
        }

    status_image_map = {
        '0-0': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/basic-total.png").convert('RGBA').resize((20,20)),
        '0-1': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/basic-total-finished.png").convert('RGBA').resize((20,20)),
        '1-0': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/advanced-total.png").convert('RGBA').resize((20,20)),
        '1-1': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/advanced-total-finished.png").convert('RGBA').resize((20,20)),
        '2-0': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/expert-total.png").convert('RGBA').resize((20,20)),
        '2-1': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/expert-total-finished.png").convert('RGBA').resize((20,20)),
        '3-0': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/master-total.png").convert('RGBA').resize((20,20)),
        '3-1': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/master-total-finished.png").convert('RGBA').resize((20,20)),
        '4-0': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/remaster-total.png").convert('RGBA').resize((20,20)),
        '4-1': Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/remaster-total-finished.png").convert('RGBA').resize((20,20))
    }

    base_draw = ImageDraw.Draw(base_image)

    for level_index in range(max_level):
        counter:MusicDataCounter = counter_map[level_index]
        total_count = counter.total
        if plate_mode == '极':
            ok_count = counter.fc
        if plate_mode == '将':
            ok_count = counter.sss
        if plate_mode == '神':
            ok_count = counter.ap
        if plate_mode == '舞舞':
            ok_count = counter.fdx
        if plate_mode == '者':
            ok_count = counter.clear
        
        i = '1' if ok_count==total_count else '0'
        status_key = f'{level_index}-{i}'
        status_image = status_image_map[status_key]

        y_point = level_config[level_index]['y']
        base_image.paste(status_image,(1000,y_point),status_image)

        outline_color = "white"
        tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RodinNTLGPro-B.otf", 21, encoding='utf-8')
        content = str(ok_count)
        fx,fy = tempFont.getsize(content)
        font_color = level_config[level_index]['color']
        x = 1055-(fx/2)
        base_draw.text((x-2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x-2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x,y_point), content, font=tempFont, fill=font_color)


        content = '/'
        fx,fy = tempFont.getsize(content)
        font_color = level_config[level_index]['color']
        x = 1090-(fx/2)
        base_draw.text((x-2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x-2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x,y_point), content, font=tempFont, fill=font_color)


        content = str(total_count)
        fx,fy = tempFont.getsize(content)
        font_color = level_config[level_index]['color']
        x = 1125-(fx/2)
        base_draw.text((x-2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point-2), content, font=tempFont, fill=outline_color)
        base_draw.text((x-2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x+2, y_point+2), content, font=tempFont, fill=outline_color)
        base_draw.text((x,y_point), content, font=tempFont, fill=font_color)

    return base_image


async def draw_user_music_info(version:str,plate_mode:str,qq:int = None,user_name:str = None):
    is_mai_version = version in '舞霸'

    default_song_list = generate_default_song_list(version,is_mai_version)

    base_image_path = Path(f"{COMPLETION_BASE_PATH}/{version}.png")
    if base_image_path.exists():
        full_image = Image.open(base_image_path).convert('RGBA')
    else:
        full_image = merge_full_image(version,is_mai_version,default_song_list)
        os.makedirs(COMPLETION_BASE_PATH,exist_ok=True)
        full_image.save(base_image_path)
        
    # 姓名框
    plate_name = utils.tran_plate_name(version+plate_mode)
    try:
        plate_id = MAIPLATE_FILE_ID_MAP[plate_name]
        plate_image = Image.open(PLATE_BASE_PATH + f"/UI_Plate_{plate_id}.png").convert('RGBA')
    except:
        return f"错误的文件:{plate_name}"
    # todo 可替换成灰度姓名框资源

    plate_image = plate_image.resize((540,87))
    full_image.paste(plate_image,(370,50),plate_image)

    user_music_data = await query_user_plate_data(generate_t_music_data(version,is_mai_version),VERSION_DF_MAP[version],qq=qq,user_name=user_name)

    full_image = draw_user_music_image(full_image,default_song_list,user_music_data,is_mai_version,plate_mode)

    basic_counter,advanced_counter,expert_counter,master_counter,rem_master_counter = music_count(user_music_data)

    full_image = draw_user_total_counter(full_image,plate_mode,is_mai_version,basic_counter,advanced_counter,expert_counter,master_counter,rem_master_counter)

    return full_image





# # full_image = draw_user_music_info('舞','神',qq=381268035)
# # full_image.show()
# async def main():
#     full_image = await draw_user_music_info('舞','神',qq=381268035)
#     full_image.show()
#     # print(result)


# asyncio.run(main())




