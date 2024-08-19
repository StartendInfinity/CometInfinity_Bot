from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import base64

def simple_draw(base, path: str, resize: list, xy: list):
    ori_pic = Image.open(path)
    ori_pic_reisize = ori_pic.resize(resize)
    base.paste(ori_pic_reisize, xy, ori_pic_reisize)
    return base

def center_font(font_x:int , img, text: str, font) -> int:
    return font_x - int(img.textlength(text, font) / 2)

def right_font(font_x, img, text, font):
    return font_x - int(img.textlength(text, font))

def return_dx_star(min: int, max: int) -> int:
    final = min / max * 100
    final_round=round(final, 2)
    if final_round < 85:
        return 0
    elif final_round < 90.00:
        return 1
    elif final_round < 93.00:
        return 2
    elif final_round < 95.00:
        return 3
    elif final_round < 97.00:
        return 4
    else:
        return 5

def song_data_filter(all_data: dict, target_level: str, target_page: int, music_data: dict, user_level:str) -> dict|None:
    diff_count = 0
    filter_data = []
    song_static = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    temp_static = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #sssp sss ssp ss sp s a fc fcp ap app
    song_data = all_data["records"]
    for single_song in song_data:
        if single_song["level"] == target_level:
            match single_song["rate"]:
                case "sssp":
                    temp_static[0] = temp_static[0] + 1
                case "sss":
                    temp_static[1] = temp_static[1] + 1
                case "ssp":
                    temp_static[2] = temp_static[2] + 1
                case "ss":
                    temp_static[3] = temp_static[3] + 1
                case "sp":
                    temp_static[4] = temp_static[4] + 1
                case "s":
                    temp_static[5] = temp_static[5] + 1
            if single_song["achievements"] >= 80.0:
                song_static[6] = song_static[6] + 1
            match single_song["fc"]:
                case "fc":
                    temp_static[7] = temp_static[7] + 1
                case "fcp":
                    temp_static[8] = temp_static[8] + 1
                case "ap":
                    temp_static[9] = temp_static[9] + 1
                case "app":
                    temp_static[10] = temp_static[10] + 1
            filter_data.append(single_song)
            #如果符合条件则加入,刚好在此处进行统计,减少循环次数
    for single_data in music_data:
        level_list = music_data[single_data]["level"]
        for level in level_list:
            if level == user_level:
                diff_count = diff_count + 1
    step = 0
    for count in range(6):
        step = temp_static[count] + step
        song_static[count] = step
    step = 0
    for count in range(4):
        step = temp_static[-1 - count] + step
        song_static[-1 - count] = step
    if len(filter_data) == 0:
        return "Data is Empty"
    filter_data.sort(key = lambda x: x["achievements"], reverse = True)
    total_pages = (len(filter_data) + 24) // 25
    if int(target_page) < 1 or int(target_page) > total_pages:
        return "Page Error"
    start_index = (int(target_page) - 1) * 25
    end_index = start_index + 25
    return {"level":target_level, "now_page":target_page, "total_pages": total_pages, "total_records": diff_count, "song_static": song_static
, "data": filter_data[start_index: end_index]}
#过滤玩家歌曲数据,验证页码

def draw_mai_lv(draw_data: dict, music_data: dict):
    img = Image.open("./src/static/mai/lv_score/mai-lvscore-bg.png")
    img_text = ImageDraw.Draw(img)
    song_static_xpos = [230, 330, 430, 530, 630, 730, 830, 960, 1060, 1160, 1260]
    fc_translate = {"": "", "fc": "FC", "fcp": "FC+", "ap": "AP", "app": "AP+"}
    fs_translate = {"": "", "fs": "FS", "fsp": "FS+", "fsd": "FDX", "fsdp": "FDX+", "sync": "SYNC"}
    #id->right name->left
    HanSans37_48 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", 48)
    HanSans35_48 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_35.otf", 48)
    HanSans37_32 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", 32)
    HanSans15_32 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_15.otf", 32)

    img_text.text([250, 42], f'Lv {str(draw_data["level"])}', (0, 0, 0), HanSans37_48)
    img_text.text([720, 56], f'第 {str(draw_data["now_page"])} / {str(draw_data["total_pages"])} 页', (0, 0, 0), HanSans37_32)
    #-13 pixels 难度 页码

    img_text.text([50, 152], str(draw_data["total_records"]), (0, 0, 0), HanSans35_48)
    #-13 pixels 总成绩数

    static_index = 0
    for static_x in song_static_xpos:
        center_x = center_font(static_x, img_text, str(draw_data["song_static"][static_index]), HanSans15_32)
        img_text.text([center_x, 182], str(draw_data["song_static"][static_index]), (0, 0, 0), HanSans15_32)
        static_index += 1
        #-10 pixels 统计表
    
    data_index = 0
    for single_data in draw_data["data"]:
        img_text.text([50, 265 + data_index * 50], f"{single_data['achievements']:.4f}%", (0, 0, 0), HanSans15_32)
        img_text.text([255, 265 + data_index * 50], fc_translate[single_data["fc"]], (0, 0, 0), HanSans15_32)
        img_text.text([350, 265 + data_index * 50], fs_translate[single_data["fs"]], (0, 0, 0), HanSans15_32)
        dxstar = return_dx_star(single_data["dxScore"], music_data[str(single_data["song_id"])]["charts"][single_data["level_index"]]["dxscore"])
        simple_draw(img, f"./src/static/mai/lv_score/dxstar_{dxstar}.png", [24, 24], [465, 280 + data_index * 50])
        #+11 pixels dx星星
        img_text.text([500, 265 + data_index * 50], str(dxstar), (0, 0, 0), HanSans15_32)
        simple_draw(img, f'./src/static/mai/lv_score/diff_{single_data["level_index"]}.png', [24, 24], [555, 280 + data_index * 50])
        #+11 pixels 难度
        img_text.text([590, 265 + data_index * 50], str(single_data["ds"]), (0, 0, 0), HanSans15_32)
        right_x = right_font(795, img_text, f'{single_data["song_id"]}.', HanSans15_32)
        img_text.text([right_x, 265 + data_index * 50], f'{single_data["song_id"]}.', (0, 0, 0), HanSans15_32)
        song_name = single_data["title"]
        if img_text.textlength(song_name, HanSans15_32) > 585.0:
            for _count_ in range(len(song_name)):
                text_len = img_text.textlength(song_name[0:_count_], HanSans15_32)
                if text_len > 585.0:
                    song_name = single_data["title"][0:_count_ - 2] + "..."
                    break
        img_text.text([810, 265 + data_index * 50], song_name, (0, 0, 0), HanSans15_32)
        data_index += 1

    n_lv_image =  img.convert("RGB")
    out_buffer = BytesIO()
    n_lv_image.save(out_buffer, "JPEG")
    bytes_data = out_buffer.getvalue()

    return base64.b64encode(bytes_data).decode()