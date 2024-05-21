import json
import time

from music import total_list

from PIL import Image, ImageDraw, ImageFont

class generate_tool():

    def calc_avg_rating_lxns(score_info):
        all_rating = 0
        for info in score_info:
            all_rating+=info["dx_rating"]
        return f"{all_rating / len(score_info):.01f}"

    def fullwidth_to_halfwidth(text):
        result = []
        for char in text:
            code_point = ord(char)
            # 全角空格（U+3000）转换为半角空格（U+0020）
            if code_point == 0x3000:
                result.append(chr(0x0020))
            # 其他全角字符（U+FF01 至 U+FF5E）转换为对应的半角字符（U+0021 至 U+007E）
            elif 0xFF01 <= code_point <= 0xFF5E:
                result.append(chr(code_point - 0xFEE0))
            else:
                result.append(char)
        return ''.join(result)

    def get_rank_plate_id(rank_plate_name):
            with open("./src/plugins/maimai/lib/id_to_plate_name.json", "r", encoding="utf-8") as f:
                plate_data = dict(json.load(f))
                if rank_plate_name in plate_data.keys():
                    return plate_data[rank_plate_name]
                else:
                    return None

    def return_ra_bg(dxRating):
        match dxRating:
            case dxRating if dxRating < 1000:
                return "01"
            case dxRating if dxRating < 2000:
                return "02"
            case dxRating if dxRating < 4000:
                return "03"
            case dxRating if dxRating < 7000:
                return "04"
            case dxRating if dxRating < 10000:
                return "05"
            case dxRating if dxRating < 12000:
                return "06"
            case dxRating if dxRating < 13000:
                return "07"
            case dxRating if dxRating < 14000:
                return "08"
            case dxRating if dxRating < 14500:
                return "09"
            case dxRating if dxRating < 15000:
                return "10"
            case _:
                return "11"

    def calc_rating_to_ds(dx_rating, list):
        achievement_list = [100.5, 100.0, 99.5, 99.0]
        for achi in achievement_list:
            list.append(generate_tool.get_TargetDs(float(dx_rating), achi))
        return list
    
    def computeRa(ds: float, achievement: float) -> int:
        baseRa = 22.4 
        if achievement < 50:
            baseRa = 7.0
        elif achievement < 60:
            baseRa = 8.0 
        elif achievement < 70:
            baseRa = 9.6 
        elif achievement < 75:
            baseRa = 11.2 
        elif achievement < 80:
            baseRa = 12.0 
        elif achievement < 90:
            baseRa = 13.6 
        elif achievement < 94:
            baseRa = 15.2 
        elif achievement < 97:
            baseRa = 16.8 
        elif achievement < 98:
            baseRa = 20.0 
        elif achievement < 99:
            baseRa = 20.3
        elif achievement < 99.5:
            baseRa = 20.8 
        elif achievement < 100:
            baseRa = 21.1 
        elif achievement < 100.5:
            baseRa = 21.6 
        return int(ds * (min(100.5, achievement) / 100) * baseRa)
    
    def get_TargetDs(ra: int, rank: float):
        for d in [x/10 for x in range(10,151)]:
            if generate_tool.computeRa(d, rank) in [ra, ra+1,ra+2]:
                return str(d)
        return "-"

    def draw_number(dx_rating, base):
        x = 295
        rating_list = list(str(dx_rating))
        if dx_rating < 10000:
            x = 313
        for file_name in rating_list:
            num_image = Image.open(f"./src/static/mai/b50/numbers/{file_name}.png")
            num_image_resize = num_image.resize([19, 22])
            base.paste(num_image_resize, (x, 62), num_image_resize)
            x+=18
        return base

    def simple_draw(base, path, resize, xy):
        ori_pic = Image.open(path)
        ori_pic_reisize = ori_pic.resize(resize)
        base.paste(ori_pic_reisize, xy, ori_pic_reisize)
        return base

    def center_font(font_x, img, text, font):
        return font_x - int(img.textlength(text, font) / 2)

    def right_font(font_x, img, text, font):
        return font_x - int(img.textlength(text, font))
    
    def get_cover_len6_id(mid: str) -> str:
        mid = int(mid)
        if mid > 10000:
            mid -= 10000
        return f'{mid:06d}'

    def return_dx_star(min:int,max:int):
        final=min/max*100
        final_round=round(final,2)
        if final_round<85:
            return 0
        elif final_round<90.00:
            return 1
        elif final_round<93.00:
            return 2
        elif final_round<95.00:
            return 3
        elif final_round<97.00:
            return 4
        else:
            return 5

    def draw_bests(base, data, type):
        index = 0
        song_no = 1
        pic_y = 624
        _range = 15
        FotB_12 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=12)
        FotB_20 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-EB.otf", size=20)
        FotEB_14 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=14)
        HanSans35_16 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_35.otf", size=16)
        if type == 35:
            _range = 35
            pic_y = 1034
        for count in range(_range):
            if index > 4:
                index = 0
                pic_y+=120
            try:
                song_info = data[count]
                song_id_6 = generate_tool.get_cover_len6_id(song_info["id"])
                song_level = song_info["level_index"]
                song_id = song_info["id"]
                song_dx_score = song_info["dx_score"]
                song_achi = f"{song_info["achievements"]:.4f}"
                dx_ra = int(song_info["dx_rating"])
                song_rate = song_info["rate"].upper()
                song_fc = song_info["fc"]
                song_fs = song_info["fs"]
                if song_fc != None:
                    song_fc = song_info["fc"].upper()
                if song_fs != None:
                    song_fs = song_info["fs"].upper()
                text_color = (255, 255, 255)
                if song_level == 4:
                    text_color = (195, 70, 231)
                base = generate_tool.simple_draw(base, f"./src/static/mai/b50/diff/mai-frame-{song_level}.png", [282, 120], [19 + index * 280 ,pic_y])
                base = generate_tool.simple_draw(base, f"./src/static/mai/cover/UI_Jacket_{song_id_6}.png", [60, 60], [36 + index * 280 ,pic_y + 17])
                if song_info["type"] == "dx":
                    base = generate_tool.simple_draw(base, "./src/static/mai/b50/UI_RSL_MBase_mode_DX.png", [19, 9], [38 + index * 280 ,pic_y + 66])
                    song_id+=10000
                else:
                    base = generate_tool.simple_draw(base, "./src/static/mai/b50/UI_RSL_MBase_mode_SD.png", [19, 9], [38 + index * 280 ,pic_y + 66])
                song_name = song_info["song_name"]
                draw_info = ImageDraw.Draw(base)
                if draw_info.textlength(song_name, HanSans35_16) > 178.0:
                    for _count_ in range(len(song_name)):
                        text_len = draw_info.textlength(song_name[0:_count_], HanSans35_16)
                        if text_len > 178.0:
                            song_name = song_info["song_name"][0:_count_ - 2] + "..."
                            break
                        count+=1
                draw_info.text([105 + index * 280, pic_y + 11], song_name, text_color, HanSans35_16)
                draw_info.text([106 + index * 280, pic_y + 41], "ID " + str(song_id), text_color, FotB_12)
                draw_info.text([35 + index * 280, pic_y + 92], "#" + str(song_no), (0, 0, 0), FotEB_14)
                song_max_dx_score = total_list.by_id(str(song_id))["charts"][song_level]["dxscore"]
                font_left = generate_tool.right_font(284 + index * 280, draw_info, str(song_dx_score) + " / " + str(song_max_dx_score), FotB_12)
                draw_info.text([font_left, pic_y + 41], str(song_dx_score) + " / " + str(song_max_dx_score), text_color, FotB_12)
                draw_info.text([105 + index * 280, pic_y + 59], str(song_achi) + "%", text_color, FotB_20)
                song_ds = float(total_list.by_id(str(song_id))["ds"][song_level])
                font_left = generate_tool.right_font(126 + index * 280, draw_info, str(song_ds) + " ▶", FotB_12)
                draw_info.text([font_left, pic_y + 94], str(song_ds) + " ▶", (0, 0, 0), FotB_12)
                draw_info.text([130 + index * 280, pic_y + 92], str(dx_ra), (0, 0, 0), FotEB_14)
                base = generate_tool.simple_draw(base, f"./src/static/mai/b50/achi/UI_TTR_Rank_{song_rate}.png", [56, 25], [234 + index * 280, pic_y + 57])
                dx_star = generate_tool.return_dx_star(song_dx_score, song_max_dx_score)
                base = generate_tool.simple_draw(base, f"./src/static/mai/b50/star/dxstar_{dx_star}.png", [20, 20], [175 + index * 280, pic_y + 89])
                if song_fc != None:
                    base = generate_tool.simple_draw(base, f"./src/static/mai/b50/sync/UI_RSL_{song_fc}_Text_01.png", [47, 24], [203 + index * 280, pic_y + 87])
                if song_fs != None:
                    base = generate_tool.simple_draw(base, f"./src/static/mai/b50/sync/UI_RSL_{song_fs}_Text_01.png", [47, 24], [245 + index * 280, pic_y + 87])

            except IndexError:
                base = generate_tool.simple_draw(base, f"./src/static/mai/b50/diff/mai-frame-empty.png", [282, 120], [19 + index * 280 ,pic_y])
            count+=1
            index+=1
            song_no+=1

class mai_best50():

    def lxns(b50_info, player_data):
        start_time = time.time()
        best_35_info = b50_info["standard"]
        best_15_info = b50_info["dx"]
        avg_best_35 = generate_tool.calc_avg_rating_lxns(best_35_info)
        avg_best_15 = generate_tool.calc_avg_rating_lxns(best_15_info)
        best_35_top = int(best_35_info[0]["dx_rating"])
        best_35_low = int(best_35_info[-1]["dx_rating"])
        best_15_top = int(best_15_info[0]["dx_rating"])
        best_15_low = int(best_15_info[-1]["dx_rating"])
        dxRating = b50_info["standard_total"] + b50_info["dx_total"]
        player_name = generate_tool.fullwidth_to_halfwidth(player_data[0])
        player_trophy_name = player_data[1]["name"]
        if len(player_trophy_name) > 21:
            player_trophy_name[0:21] + "..."
        # TODO:这边应该还有优化的空间,回头再看
        player_trophy_color = player_data[1]["color"]
        player_course_rank = '{:02d}'.format(player_data[2])
        player_class_rank = '{:02d}'.format(player_data[3])
        #不足2位补0
        player_plate_id = "000001"
        player_icon_id =  "000001"
        player_frame_id = None
        if player_data[4] != None:  #playerPlate
            player_plate_name = player_data[4]["name"]
            player_plate_id = generate_tool.get_rank_plate_id(player_plate_name)
            #plate_name仅用于获取正确的将牌ID, 无其他用途
            if player_plate_id == None:
                player_plate_id = str(player_data[4]["id"])
        if player_data[5] != None: #playerIcon
            player_icon_id = str(player_data[5]["id"])
        if player_data[6] != None: #playerFrame
            player_frame_id = str(player_data[6]["id"])
        b50_image = Image.open("./src/static/mai/b50/mai-b50-bud.png")
        HanSans37_28 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", size=28)
        HanSans37_16 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", size=16)
        FotB_19 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=19)
        FotB_24 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=24)
        if player_frame_id != None:
            b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/frame/UI_Frame_{player_frame_id}.png", [1440, 603], [0, 0])
        b50_image = generate_tool.simple_draw(b50_image, "./src/static/mai/b50/LXNS.png", [174, 24], [1188, 110])
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/plate/UI_Plate_{player_plate_id}.png", [960, 155], [40, 40])
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/icon/UI_Icon_{player_icon_id}.png", [131, 131], [52, 52])
        ra_bg_index = generate_tool.return_ra_bg(dxRating)
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/rating/UI_CMN_DXRating_{ra_bg_index}.png", [225, 44], [190, 50])
        b50_image = generate_tool.draw_number(dxRating, b50_image)
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/class/UI_CMN_Class_S_{player_class_rank}.png", [120, 72], [430, 24])
        b50_image = generate_tool.simple_draw(b50_image, "./src/static/mai/b50/playername.png", [386, 78], [178, 87])
        draw_nickname = ImageDraw.Draw(b50_image)
        draw_nickname.text((203, 100), player_name, (0,0,0), HanSans37_28)
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/course/UI_CMN_DaniPlate_{player_course_rank}.png", [104, 48], [437, 98])
        b50_image = generate_tool.simple_draw(b50_image, f"./src/static/mai/b50/trophy/UI_CMN_Shougou_{player_trophy_color}.png", [368, 48], [185, 145])
        draw_trophy = ImageDraw.Draw(b50_image)
        trophy_x = generate_tool.center_font(369, draw_trophy, player_trophy_name, HanSans37_16)
        #计算居中后的X值
        draw_trophy.text([trophy_x, 153], player_trophy_name, (255, 255, 255), HanSans37_16, stroke_width = 1, stroke_fill=(0, 0, 0))
        b50_image = generate_tool.simple_draw(b50_image, "./src/static/mai/b50/ratingtable.png", [814, 325], [40 ,240])
        draw_rating_table = ImageDraw.Draw(b50_image)
        draw_rating_table.text([520, 305], avg_best_15, (30, 54, 99), FotB_19)
        draw_rating_table.text([650, 305], str(b50_info["dx_total"]), (30, 54, 99), FotB_19)
        draw_rating_table.text([520, 435], avg_best_35, (30, 54, 99), FotB_19)
        draw_rating_table.text([650, 435], str(b50_info["standard_total"]), (30, 54, 99), FotB_19)
        center_list = [246, 380, 514, 648, 781]
        y_list = [342, 392, 472, 522]
        rating_list = [best_15_top, best_15_low, best_35_top, best_35_low]
        index_y = 0
        for rating in rating_list:
            index = 0
            calc_list = generate_tool.calc_rating_to_ds(str(rating), [str(rating)])
            for element in calc_list:
                center = generate_tool.center_font(center_list[index], draw_rating_table, element, FotB_24)
                draw_rating_table.text([center, y_list[index_y]], element, (30, 54, 99), FotB_24)
                index+=1
            index_y+=1
        generate_tool.draw_bests(b50_image, best_15_info, 15)
        generate_tool.draw_bests(b50_image, best_35_info, 35)
        
        print(str((time.time() - start_time) * 1000) + "ms")
        b50_image.show()

    def fish():
        print("fish")

#----导入测试数据----

post_data = {}
other_data = []

def test():
    with open ("./src/plugins/maimai/lib/temp/testdata_lxns.json", "r", encoding="utf-8") as f:
        all_data = dict(json.load(f))
    with open ("./src/plugins/maimai/lib/temp/testdata2_lxns.json", "r", encoding="utf-8") as f:
        playerInfo = dict(json.load(f))
        playerName = playerInfo["data"]["name"]
        playerTrophy = playerInfo["data"]["trophy"]
        playerCourseRank = playerInfo["data"]["course_rank"]
        playerClassRank = playerInfo["data"]["class_rank"]
        try:
            playerPlate = playerInfo["data"]["name_plate"]
        except KeyError:
            playerPlate = None
        try:
            playerIcon = playerInfo["data"]["icon"]
        except KeyError:
            playerIcon = None
        try:
            playerFrame = playerInfo["data"]["frame"]
        except KeyError:
            playerFrame = None
        #由于爬取收藏品是可设置的，当参数为None时，调用默认/或不绘制
        return all_data, [playerName, playerTrophy, playerCourseRank, playerClassRank, playerPlate, playerIcon, playerFrame]

post_data, other_data = test()

mai_best50.lxns(post_data["data"], other_data)