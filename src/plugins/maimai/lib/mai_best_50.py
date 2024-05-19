import json

from music import total_list

from PIL import Image, ImageDraw, ImageFont

class mai_best50():
    """
    此类用于生成maimaiBest50成绩图
    请使用mai_best50.generate(mai_best50, args)来调用
    使用水鱼Api时请在player_data中传入None(?)

    参数:
        b50_info(dict):玩家的Best50信息
        player_data(list):玩家的其他信息(如姓名框/称号等)
        api_choice(str):选择的api
        落雪:"lxns", 水鱼:"fish"
    
    返回:
        b64data(base64):图片信息
    """
    def  __init__(self) -> None:
        pass
        
    def generate(self, b50_info, player_data, api_choice):
        if api_choice == "lxns":
            self.lxns(b50_info["data"], player_data=player_data, b50_info=b50_info["data"])
        else:
            self.fish(b50_info)
    
    def lxns(self, b50_info, player_data):
        best_35_info = b50_info["standard"]
        best_15_info = b50_info["dx"]
        dxRating = b50_info["standard_total"] + b50_info["dx_total"]
        player_name = mai_best50.fullwidth_to_halfwidth(mai_best50, player_data[0])
        player_trophy_name = player_data[1]["name"]
        if len(player_trophy_name) > 21:
            player_trophy_name[0:21] + "..."
        # TODO:这边应该还有优化的空间,回头再看
        player_trophy_color = player_data[1]["color"]
        player_course_rank = '{:02d}'.format(player_data[2])
        player_class_rank = '{:02d}'.format(player_data[3])
        #不足2位补0
        if player_data[4] == None:  #playerPlate
            player_plate_id = "000001"
        else:
            player_plate_name = player_data[4]["name"]
            player_plate_id = mai_best50.get_rank_plate_id(mai_best50, rank_plate_name=player_plate_name)
            #plate_name仅用于获取正确的将牌ID, 无其他用途
            if player_plate_id == None:
                player_plate_id = str(player_data[4]["id"])
        if player_data[5] == None: #playerIcon
            player_icon_id =  "000001"
        else:
            player_icon_id = str(player_data[5]["id"])
        if player_data[6] == None: #playerFrame
            player_frame_id = None
        else:
            player_frame_id = str(player_data[6]["id"])
            #后续检测若frame_id == None则不绘制底板
        b50_image = Image.open("./src/static/mai/b50/mai-b50-bud.png")
        HanSans37_28 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", size=28)
        HanSans37_16 = ImageFont.truetype("./src/static/mai/pic/font/SourceHanSans_37.ttf", size=16)
        if player_frame_id != None:
            frame_img = Image.open(f"./src/static/mai/b50/frame/UI_Frame_{player_frame_id}.png")
            frame_img_resize = frame_img.resize([1440, 603])
            b50_image.paste(frame_img_resize, (0,0), frame_img_resize)
        mode_img = Image.open("./src/static/mai/b50/LXNS.png")
        mode_img_resize = mode_img.resize([174, 24])
        b50_image.paste(mode_img_resize, (1188, 110), mode_img_resize)
        plate_img = Image.open(f"./src/static/mai/b50/plate/UI_Plate_{player_plate_id}.png")
        plate_img_resize = plate_img.resize([960, 155])
        b50_image.paste(plate_img_resize, (40, 40), plate_img_resize)
        icon_img = Image.open(f"./src/static/mai/b50/icon/UI_Icon_{player_icon_id}.png")
        icon_img_resize = icon_img.resize([131, 131])
        b50_image.paste(icon_img_resize, (52, 52), icon_img_resize)
        ra_bg_index = mai_best50.returnRatingBackground(mai_best50, dxRating=dxRating)
        rating_image = Image.open(f"./src/static/mai/b50/rating/UI_CMN_DXRating_{ra_bg_index}.png")
        rating_image_resize = rating_image.resize([225, 44])
        b50_image.paste(rating_image_resize, (190, 50), rating_image_resize)
        b50_image = mai_best50.draw_number(mai_best50, dx_rating=dxRating, b50_image=b50_image)
        #绘制DX Rating数字
        class_image = Image.open(f"./src/static/mai/b50/class/UI_CMN_Class_S_{player_class_rank}.png")
        class_image_resize = class_image.resize([120,72])
        b50_image.paste(class_image_resize, (430, 24), class_image_resize)
        nickname_bg = Image.open("./src/static/mai/b50/playername.png")
        nickname_bg_resize = nickname_bg.resize([386, 78])
        b50_image.paste(nickname_bg_resize, [178, 87], nickname_bg_resize)
        draw_nickname = ImageDraw.Draw(b50_image)
        draw_nickname.text((203, 100), player_name, (0,0,0), HanSans37_28)
        course_image = Image.open(f"./src/static/mai/b50/course/UI_CMN_DaniPlate_{player_course_rank}.png")
        course_image_resize = course_image.resize([104,48])
        b50_image.paste(course_image_resize, (437, 98), course_image_resize)
        trophy_bg = Image.open(f"./src/static/mai/b50/trophy/UI_CMN_Shougou_{player_trophy_color}.png")
        trophy_bg_resize = trophy_bg.resize([368 ,48])
        b50_image.paste(trophy_bg_resize, (185, 145), trophy_bg_resize)
        draw_trophy = ImageDraw.Draw(b50_image)
        trophy_x = 369 - int(draw_trophy.textlength(player_trophy_name, HanSans37_16) / 2)
        #计算居中后的X值
        draw_trophy.text([trophy_x, 153], player_trophy_name, (255, 255, 255), HanSans37_16, stroke_width = 1, stroke_fill=(0, 0, 0))
        rating_table = Image.open("./src/static/mai/b50/ratingtable.png")
        rating_table_resize = rating_table.resize([814, 325])
        b50_image.paste(rating_table_resize, (40, 240), rating_table_resize)

        b50_image.show()

    def fullwidth_to_halfwidth(self, text):
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

    def get_rank_plate_id(self, rank_plate_name):
        with open("./src/plugins/maimai/lib/id_to_plate_name.json", "r", encoding="utf-8") as f:
            plate_data = dict(json.load(f))
            if rank_plate_name in plate_data.keys():
                return plate_data[rank_plate_name]
            else:
                return None

    def returnRatingBackground(self, dxRating):
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

    def draw_number(self, dx_rating, b50_image):
        x = 295
        rating_list = list(str(dx_rating))
        if dx_rating < 10000:
            x = 313
        for file_name in rating_list:
            num_image = Image.open(f"./src/static/mai/b50/numbers/{file_name}.png")
            num_image_resize = num_image.resize([19, 22])
            b50_image.paste(num_image_resize, (x, 62), num_image_resize)
            x+=18
        return b50_image

    def fish(self, b50_info):
        pass
    #尝试一下python类

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

mai_best50.generate(mai_best50, post_data, other_data, "lxns")