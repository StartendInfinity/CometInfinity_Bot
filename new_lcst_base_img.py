# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw,ImageFont
from src.plugins.maimai.lib.music import total_list
from pathlib import Path
import os

from src.plugins.maimai.lib.plate_map import MAIPLATE_FILE_ID_MAP, VERSION_MAP, DELETED_MUSIC, MAI_DELETED_MUSIC_REM,MAI_DELETED_MUSIC_Normal
from src.plugins.maimai.lib import completion_utils as utils
import asyncio

PLATE_BASE_PATH = "src/static/mai/b50/plate"
FONT_PATH = "src/static/font"
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


def generate_t_music_data(version:str,is_mai_version):
    musiclist, musiclist_rem = total_list.by_versions_for_cn(VERSION_MAP[version],is_mai_version=is_mai_version)
    music_data = {}
    for music in musiclist:
        for level_index in [0,1,2,3]:
            key = f"{music.id}-{level_index}"
            music_data[key] = {
                "music_id":music.id,
                "level_index":level_index
            }
    for music in musiclist_rem:
        key = f"{music.id}-4"
        music_data[key] = {
            "music_id":music.id,
            "level_index":4
        }
    return music_data


def generate_base_level_image(version:str):
    is_mai_version = version in '舞霸'
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
                music_box = Image.new("RGBA",(80,102),(255,255,255,255))
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

def merge_full_image(version:str):
    plate_base_image = generate_base_level_image(version)
    base_w,base_h = plate_base_image.size
    top_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/up.png").convert('RGBA')
    down_image = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + f"/down.png").convert('RGBA')
    total_height = base_h + 222 + 222
    full_image = Image.new("RGBA",(1280,total_height),(255,255,255,255))
    full_image.paste(top_image,(0,0),top_image)
    full_image.paste(plate_base_image,(0,222),plate_base_image)
    full_image.paste(down_image,(0,222+base_h),down_image)
    return full_image

def draw_user_music_info(version:str,plate_mode:str,qq:int = None,user_name:str = None):
    full_image = merge_full_image('舞')
    # 姓名框
    plate_name = utils.tran_plate_name(version+plate_mode)
    try:
        plate_id = MAIPLATE_FILE_ID_MAP[plate_name]
        plate_image = Image.open(PLATE_BASE_PATH + f"/UI_Plate_{plate_id}.png").convert('RGBA')
    except:
        return f"错误的文件:{plate_name}"

    plate_image = plate_image.resize((540,87))
    # todo 可替换成灰度姓名框资源
    # plate_image = plate_image.convert('L')
    full_image.paste(plate_image,(370,50),plate_image)
    return full_image

full_image = draw_user_music_info('舞','神',qq=381268035)
full_image.show()

