import json, os, base64
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

from .divingFishApi import divingFishApi

Font_path = rf"src\static\chu\pic\font"
hans_15 = os.path.join(Font_path, 'SourceHanSans_15.otf')
hans_35 = os.path.join(Font_path, 'SourceHanSans_35.otf')
hans_37 = os.path.join(Font_path, 'SourceHanSans_37.ttf')

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

def format_number_with_commas(number):
    return "{:,}".format(number)


def convert_achievement(score):
    if score <= 499999:
        achievement = "D"
    elif score <= 599999:
        achievement = "C"
    elif score <= 699999:
        achievement = "B"
    elif score <= 799999:
        achievement = "BB"
    elif score <= 899999:
        achievement = "BBB"
    elif score <= 924999:
        achievement = "A"
    elif score <= 949999:
        achievement = "AA"
    elif score <= 974999:
        achievement = "AAA"
    elif score <= 989999:
        achievement = "S"
    elif score <= 999999:
        achievement = "S+"
    elif score <= 1004999:
        achievement = "SS"
    elif score <= 1007499:
        achievement = "SS+"
    elif score <= 1008999:
        achievement = "SSS"
    else:
        achievement = "SSS+"
    return achievement


def convert_fc(fc, score):
    if score == 1010000:
        return "AJC"
    if fc == "alljustice":
        return "AJ"
    elif fc == "fullcombo" or fc == "fullchain" or fc =="fullchain2":
        return "FC"
    else:
        return ""


def filter_and_sort(data, level):
    filtered_data = [item for item in data["records"]["best"] if item["level"] == level]
    sorted_data = sorted(filtered_data, key=lambda x: x["score"], reverse=True)
    return sorted_data


async def chu_score_list(level: str, qq: str = None, username: str = None, page: int = 1):
    df_client = divingFishApi()
    response = await df_client.chunithmprober_dev_player_record(qq=qq, username=username)
    if response is None:
        return None
    sorted_data = filter_and_sort(response, level)
    with open('./src/plugins/chunithm/music_data/music_data.json', 'r', encoding='utf-8') as f:
        music_data = json.load(f)
    total_music = 0
    for music in music_data:
        for d in music["level"]:
            if d == level:
                total_music += 1
    bg_path = os.path.join('./src/static/chu/socre_line/chu-lvscore-bg.png')
    bg = Image.open(bg_path).convert('RGBA')

    achi_list = [0, 0, 0, 0, 0, 0]
    fc_list = [0, 0]
    for i, item in enumerate(sorted_data):
        achi = convert_achievement(item["score"])
        fc = convert_fc(item["fc"], item["score"])
        if achi == "SSS+":
            for i in range(6):
                achi_list[i] += 1
        elif achi == "SSS":
            for i in range(5):
                achi_list[i] += 1
        elif achi == "SS+":
            for i in range(4):
                achi_list[i] += 1
        elif achi == "SS":
            for i in range(3):
                achi_list[i] += 1
        elif achi == "S+":
            for i in range(2):
                achi_list[i] += 1
        elif achi == "S":
            for i in range(1):
                achi_list[i] += 1

        if fc == "FC":
            fc_list[0] += 1
        elif fc == "AJ":
            fc_list[0] += 1
            fc_list[1] += 1

    font_37_48 = ImageFont.truetype(hans_37, 48)
    font_37_32 = ImageFont.truetype(hans_37, 32)
    font_35_48 = ImageFont.truetype(hans_35, 48)
    font_15_32 = ImageFont.truetype(hans_15, 32)

    total_pages = len(sorted_data) // 25 + 1
    draw = ImageDraw.Draw(bg)
    draw.text((290, 42), f"Lv {level}", font=font_37_48, fill=BLACK, anchor='la')
    draw.text((720, 60), f"第 {page} / {total_pages} 页", font=font_37_32, fill=BLACK, anchor='la')
    draw.text((50, 165), f"{total_music}", font=font_35_48, fill=BLACK)
    for i in range(6):
        draw.text((250 + 145 * i, 192), f"{achi_list[5 - i]}", font=font_15_32, fill=BLACK, anchor='ma')
    for i in range(2):
        draw.text((1145 + 145 * i, 192), f"{fc_list[i]}", font=font_15_32, fill=BLACK, anchor='ma')
    range_start = 25 * (page - 1)
    range_end = 25 * page

    for i, item in enumerate(sorted_data[range_start:range_end]):
        score = format_number_with_commas(item["score"])
        achievement = convert_achievement(item["score"])
        fc = convert_fc(item["fc"], item["score"])
        ds = item["ds"]
        cid = item["mid"]
        text_width, _ = draw.textsize(f"{cid}.", font=font_15_32)
        title = item["title"]
        draw.text((50, 265 + 50 * i), f"{score}", font=font_15_32, fill=BLACK)
        draw.text((255, 265 + 50 * i), f"{achievement}", font=font_15_32, fill=BLACK)
        draw.text((380, 265 + 50 * i), f"{fc}", font=font_15_32, fill=BLACK)
        draw.text((550, 265 + 50 * i), f"{ds}", font=font_15_32, fill=BLACK)
        draw.text((760 - text_width, 265 + 50 * i), f"{cid}.", font=font_15_32, fill=BLACK)
        draw.text((775, 265 + 50 * i), f"{title}", font=font_15_32, fill=BLACK)

        dif_label = item["level_index"]
        bg.alpha_composite(Image.open(os.path.join(f"./src/static/chu/socre_line/{dif_label}.png")).convert('RGBA').resize((24, 24)),
                           (515, 279 + 50 * i))

    n_bg = bg.convert("RGB")
    buffer = BytesIO()
    n_bg.save(buffer, format = "JPEG")
    byte_data = buffer.getvalue()
    return base64.b64encode(byte_data).decode()