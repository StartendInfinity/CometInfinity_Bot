from PIL import Image, ImageDraw, ImageFont

class mai_best50():
    """
    此类用于生成maimaiBest50成绩图
    请使用mai_best50.generate(mai_best50, args)来调用

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
        pass

    def fish(self, b50_info):
        pass
    #尝试一下python类