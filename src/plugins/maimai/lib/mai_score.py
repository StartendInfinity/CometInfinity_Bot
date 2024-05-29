import base64

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class generate_tool():

    def simple_draw(base, path, resize, xy):
        ori_pic = Image.open(path)
        ori_pic_reisize = ori_pic.resize(resize)
        base.paste(ori_pic_reisize, xy, ori_pic_reisize)
        return base
    
    def get_cover_len6_id(mid: str) -> str:
        mid = int(mid)
        if mid > 10000:
            mid -= 10000
        return f'{mid:06d}'

    def return_dx_star(min:int,max:int):
        final=min/max*100
        final_round=round(final,1)
        if final_round<85:
            return 0, final_round
        elif final_round<90.00:
            return 1, final_round
        elif final_round<93.00:
            return 2, final_round
        elif final_round<95.00:
            return 3, final_round
        elif final_round<97.00:
            return 4, final_round
        else:
            return 5, final_round

    def center_font(font_x, img, text, font):
        return font_x - int(img.textlength(text, font) / 2)

    def generate_charts(base, draw, score_data, music_data, mas: bool):
        index = 4
        if mas:
            index = 5
        chart_info = {}
        for __count__ in range(index):
            try:
                for element in score_data:
                    level_index = element["level_index"]
                    if level_index == __count__:
                        chart_info[__count__] = element
                        break
                    else:
                        chart_info[__count__] = {}
            except:
                chart_info[__count__] = {}
        #乐曲信息补全...

        FotB_48 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=48)
        FotB_28 = ImageFont.truetype("./src/static/mai/pic/font/FOT-RodinNTLGPro-B.otf", size=28)
        base_y = [577, 717, 857, 997, 1137]
        for element in chart_info.keys():
            chart = chart_info[element]
            colors = (255, 255, 255)
            if element > 3:
                colors = (195, 70, 231)
            if len(chart) == 0:
                draw.text([110, base_y[element]], "NO DATA", colors, FotB_48)
                draw.text([1255, base_y[element] - 12], str('{:.01f}'.format(music_data["ds"][element])), colors, FotB_28)
                draw.text([1255, base_y[element] + 25], "-", colors, FotB_28)
                #字形有点问题 正常显示的话为+29 横线好像会偏下
            else:
                song_fc = chart["fc"]
                song_fs = chart["fs"]
                song_dx_score = chart["dx_score"]
                song_max_dx_score = music_data["charts"][element]["dxscore"]
                draw.text([1255, base_y[element] - 12], str('{:.01f}'.format(music_data["ds"][element])), colors, FotB_28)
                draw.text([1255, base_y[element] + 29], str(int(chart["dx_rating"])), colors, FotB_28)
                draw.text([110, base_y[element]], '{:.04f}'.format(chart["achievements"]) + "%", colors, FotB_48)
                generate_tool.simple_draw(base, f"./src/static/mai/score/achi/UI_TTR_Rank_{chart['rate']}.png", [160, 60], [415, base_y[element] - 7])
                if song_fc != None:
                    
                    base = generate_tool.simple_draw(base, f"./src/static/mai/score/sync/UI_RSL_{song_fc.upper()}_Text_01.png", [126, 64], [575, base_y[element] - 9])
                if song_fs != None:
                    base = generate_tool.simple_draw(base, f"./src/static/mai/score/sync/UI_RSL_{song_fs.upper()}_Text_01.png", [126, 64], [705, base_y[element] - 9])
                dx_star, dx_achi = generate_tool.return_dx_star(song_dx_score, song_max_dx_score)
                generate_tool.simple_draw(base, f"./src/static/mai/b50/star/dxstar_{dx_star}.png", [70, 70], [1080, base_y[element] - 12])
                dx_score_center = generate_tool.center_font(950, draw, f"{str(song_dx_score)} / {str(song_max_dx_score)}", FotB_28)
                draw.text([dx_score_center, base_y[element] - 12], f"{str(song_dx_score)} / {str(song_max_dx_score)}", colors, FotB_28) 
                dx_achi_center = generate_tool.center_font(950, draw, f"(-{song_max_dx_score - song_dx_score}) {dx_achi}%", FotB_28)
                draw.text([dx_achi_center, base_y[element] + 25], f"(-{song_max_dx_score - song_dx_score}) {dx_achi}%", colors, FotB_28)

class mai_score():

    def lxns(chart_data, music_data):
        score_data = chart_data['data']
        song_id = score_data[0]["id"]
        song_id2 = music_data["id"]
        song_name = music_data["title"]
        song_artist = music_data["basic_info"]["artist"]
        song_genre = music_data["basic_info"]["genre"]
        song_bpm = music_data["basic_info"]["bpm"]
        song_ds = music_data["ds"]
        song_type = music_data["type"]
        mas = False
        song_id_6 = generate_tool.get_cover_len6_id(str(song_id))
        #版本和是否有成绩之前已经判断过了,应该不会出事
        HanSans35_42 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_35.otf", size=42)
        HanSans15_24 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_15.otf", size=24)
        HanSans17_28 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_17.ttf", size=28)
        default_color = (30, 54, 99)
        if len(song_ds) > 4:
            score_image = Image.open("./src/static/mai/score/mai-score-5.png")
            mas = True
        else:
            score_image = Image.open("./src/static/mai/score/mai-score-4.png")
        draw_image = ImageDraw.Draw(score_image)
        generate_tool.simple_draw(score_image, f"./src/static/mai/cover/UI_Jacket_{song_id_6}.png", [300, 300], [130, 130])
        if song_type == "DX":
            generate_tool.simple_draw(score_image, "./src/static/mai/pic/DX.png", [90, 30], [133, 400])
        else:
            generate_tool.simple_draw(score_image, "./src/static/mai/pic/标准.png", [90, 30], [133, 400])
        count = 0
        if draw_image.textlength(song_name, HanSans35_42) > 840.0:
            for _count_ in range(len(song_name)):
                text_len = draw_image.textlength(song_name[0:_count_], HanSans35_42)
                if text_len > 336.0:
                    song_name = song_name[0:_count_ - 2] + "..."
                    break
                count+=1
        draw_image.text([460, 140], song_name, default_color, HanSans35_42)
        #乐曲名
        count = 0
        if draw_image.textlength(song_artist, HanSans15_24) > 840.0:
            for _count_ in range(len(song_artist)):
                text_len = draw_image.textlength(song_artist[0:_count_], HanSans15_24)
                if text_len > 336.0:
                    song_artist = song_artist[0:_count_ - 2] + "..."
                    break
                count+=1
        draw_image.text([460, 265], song_artist, default_color, HanSans15_24)
        #艺术家
        draw_image.text([460, 395], f'ID {song_id2}          {song_genre}          BPM: {song_bpm}', default_color, HanSans17_28)
        generate_tool.generate_charts(score_image, draw_image, score_data, music_data ,mas)
        n_score_image =  score_image.convert("RGB")

        out_buffer = BytesIO()
        n_score_image.save(out_buffer, "JPEG")
        bytes_data = out_buffer.getvalue()
        return base64.b64encode(bytes_data).decode()

    def fish():
        print("fish")