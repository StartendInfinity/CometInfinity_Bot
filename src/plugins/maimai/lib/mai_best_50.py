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
        player_name = player_data[0]
        player_trophy_name = player_data[1]["name"]
        player_trophy_color = player_data[1]["color"]
        player_course_rank = player_data[2]
        player_class_rank = player_data[3]
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
        b50_image = Image.open("./src/static/mai/pic/mai-b50-bud.png")
        if player_frame_id != None:
            frame_img = Image.open(f"./src/static/mai/frame/UI_Frame_{player_frame_id}.png")
            frame_img_resize = frame_img.resize([1440, 603])
            b50_image.paste(frame_img_resize, (0,0))
        
        b50_image.show()

    def get_rank_plate_id(self, rank_plate_name):
        with open("./src/plugins/maimai/lib/id_to_plate_name.json", "r", encoding="utf-8") as f:
            plate_data = dict(json.load(f))
            if rank_plate_name in plate_data.keys():
                return plate_data[rank_plate_name]
            else:
                return None

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