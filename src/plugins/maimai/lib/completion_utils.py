from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
from .music import total_list
from src.plugins.maimai.lib.plate_map import VERSION_DF_MAP, VERSION_MAP, DELETED_MUSIC, MAI_DELETED_MUSIC_REM,TRADITIONAL2SIMPLIFIED

def generate_level_ds_data():
    level_list = {
        "15":[15.0],
        "14+":[14.9,14.8,14.7],
        "14":[14.6,14.5,14.4,14.3,14.2,14.1,14.0],
        "13+":[13.9,13.8,13.7],
        "13":[13.6,13.5,13.4,13.3,13.2,13.1,13.0],
        "12+":[12.9,12.8,12.7],
        "12":[12.6,12.5,12.4,12.3,12.2,12.1,12.0],
        "11+":[11.9,11.8,11.7],
        "11":[11.6,11.5,11.4,11.3,11.2,11.1,11.0],
        "10+":[10.9,10.8,10.7],
        "10":[10.6,10.5,10.4,10.3,10.2,10.1,10.0],
        "9+":[9.9,9.8,9.7],
        "9":[9.6,9.5,9.4,9.3,9.2,9.1,9.0],
        "8+":[8.9,8.8,8.7],
        "8":[8.6,8.5,8.4,8.3,8.2,8.1,8.0],
        "7+":[7.9,7.8,7.7],
        "7":[7.6,7.4,7.4,7.3,7.2,7.1,7.0]
    }

    level_ds_list = {}
    for level in level_list.items():
        level_ds_list[level[0]] = {}
        for ds in level[1]:
            level_ds_list[level[0]][ds] = total_list.by_ds_for_lcst(ds)
    return level_ds_list


def get_cover_len6_id(mid: str) -> str:
    mid = int(mid)
    if mid > 10000:
        mid -= 10000
    return f'{mid:06d}'
            
def open_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return -1
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content)).convert('RGBA')
        return image
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    
def calculate_cols(num,i):
    if num % i == 0:
        return num // i
    else:
        return num // i + 1
    
def get_decimal_part(number):
    # 确保输入是浮点数
    float_number = float(number)
    
    # 将浮点数转换为字符串
    number_str = str(float_number)
    
    # 找到小数点的位置
    if '.' in number_str:
        # 提取小数点后的部分
        decimal_part = number_str.split('.')[-1]
    else:
        # 如果没有小数点，返回 '0'
        decimal_part = '0'
    
    # 如果小数部分为空，则返回 '0'
    if not decimal_part:
        decimal_part = '0'
    
    return decimal_part


def get_dxscore_type(dxscorepen):
    if dxscorepen <= 85:
        return 0
    elif dxscorepen <= 90:
        return 1
    elif dxscorepen <= 93:
        return 2
    elif dxscorepen <= 95:
        return 3     
    elif dxscorepen <= 97:
        return 4     
    else:
        return 5


def exec_star_num(music_id,level_index,dx_scroe):
    start_mun = dx_scroe / (sum(total_list.by_id(str(music_id)).charts[level_index]['notes'])*3) *100
    star_index = get_dxscore_type(start_mun)
    return star_index

def tran_plate_name(plate_name:str):
    for k,v in TRADITIONAL2SIMPLIFIED.items():
        plate_name = plate_name.replace(k,v)
    return plate_name

# LEVEL_DS_DICT = generate_level_ds_data()


        # raise Exception("抽象化错误")
        # url = f"https://download.fanyu.site/abstract/{cover_path}.png"
        # print(url)
        # cover = open_image_from_url(url)
        # if cover == -1:
        #     return get_nomal_cover_path(int(music_id))
        # cover.save(img_path)
        # print('保存新的抽象画资源')
        # return img_path