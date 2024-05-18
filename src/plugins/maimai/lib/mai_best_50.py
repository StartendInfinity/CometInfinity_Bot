import json

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
            self.lxns(b50_info, player_data)
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
        player_plate_name = player_data[4]["name"]
        player_plate_id = self.get_rank_plate_id(player_plate_name)
        if player_plate_id == None:
            player_plate_id = player_data[4]["id"]

    def get_music_data_cn(self):
        with open("./src/plugins/maimai/music_data/maidxCN.json", "r", encoding="utf-8") as f:
            all_data = json.load(f)
            data_dict = {}
            for song_id in all_data:
                song_name = all_data[song_id]["title"]
                

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