# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw,ImageFont
from src.plugins.maimai.lib.music import total_list
from pathlib import Path
import os

from src.plugins.maimai.lib.plate_map import VERSION_DF_MAP, VERSION_MAP, DELETED_MUSIC, MAI_DELETED_MUSIC_REM,MAI_DELETED_MUSIC_Normal
from src.plugins.maimai.lib import completion_utils as utils
import asyncio


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

cover_height = 80+20
# 纵间距
inds_vertical_spacing = 20
# 横间距
inds_horizontal_spacing = 16

ds_vertical_spacing = 20



def generate_base_level_image(version:str):
    result_list, musiclist_rem = total_list.by_versions_for_cn(VERSION_MAP[version])
    default_song_list = {"15":[],"14+":[],"14":[],"13+":[],"13":[],"12+":[],"12":[],"11+":[],"11":[],"10+":[],"10":[],"9+":[],"9":[],"8+":[],"8":[],"7+":[],"7":[],"6":[],"5":[],"4":[],"3":[],"2":[],"1":[]}
    for song_info in result_list:
        if version in '舞霸':
            if len(song_info.level) == 5:
                level= song_info.level[4]
                default_song_list[level].append(song_info.id)
        else:
            if int(song_info.id) > 99999:
                continue
            level= song_info.level[3]
            default_song_list[level].append(song_info.id)

    music_content_hight = 0
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
    init_y = 0

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

                # base_img = Image.open(NEW_LEVEL_STATUS_TABLE_PATH + "/song/upperbox.png").convert('RGBA')
                # music_box.paste(base_img,(0,0),base_img)

                # diff_img = diff_img_list[music['level_index']]
                # music_box.paste(diff_img,(0,0),diff_img)
                # music_box_draw = ImageDraw.Draw(music_box)

                # tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RaglanPunchStd-UB.otf", 11, encoding='utf-8')
                # fx,fy = tempFont.getsize(str(id))
                # font_color = (255,255,255) if music['level_index'] < 4 else (34, 47, 62)
                # music_box_draw.text((27 - int(fx/2),91.8- fy/2), str(id), font=tempFont, fill=font_color)

                plate_base_image.paste(music_box,(x_point,y_point),music_box)

                x_point += cover_height + inds_horizontal_spacing
                line_count += 1
                if line_count == row_count and index+1 != len(musics):
                    y_point += cover_height + inds_vertical_spacing
                    x_point = init_x
                    line_count = 0
            x_point = init_x
            print(index)
            print(len(musics))
            if index != len(musics) -1:
                y_point -= inds_vertical_spacing
                y_point += ds_vertical_spacing
            else:
                y_point += cover_height + ds_vertical_spacing

    plate_base_image.show()
    
    print(music_content_hight)
generate_base_level_image('暁')

