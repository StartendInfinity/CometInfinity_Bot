
from PIL import Image, ImageDraw, ImageFont
from src.plugins.chunithm.lib.class_utils import UserData,ChartInfo
from src.plugins.chunithm.lib.tool import truncate_text

class DrawBest(object):
    def __init__(self, userData:UserData):
        self.userData = userData
        self.pic_dir = 'src/static/chu/b30/'
        self.cover_dir = 'src/static/chu/cover/'
        self.font_dir = 'src/static/chu/pic/font/'
        self.img = Image.open(self.pic_dir + 'chu-b30-lmn.png').convert('RGBA')
        self.imgDraw = ImageDraw.Draw(self.img)
        self.draw()

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: #转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def get_trophy_file_id(self,titleColor):
        title_color_map = {
            'normal':0,
            'bronze':1,
            'silver':2,
            'gold':3,
            'platina':4,
            'rainbow':5,
            'staff':6,
            'maimai':8,
            'ongeki':7
        }
        fileName = f"CHU_UI_Trophy_{title_color_map.get(titleColor,0)}.png"
        return fileName

    def get_rating_color(self):
        if self.userData.rating <= 3.99:
            return 'green'
        elif self.userData.rating <= 6.99:
            return 'orange'
        elif self.userData.rating <= 9.99:
            return 'red'
        elif self.userData.rating <= 11.99:
            return 'murasaki'
        elif self.userData.rating <= 13.24:
            return 'bronze'
        elif self.userData.rating <= 14.49:
            return 'sliver'
        elif self.userData.rating <= 15.24:
            return 'gold'
        elif self.userData.rating <= 15.99:
            return 'platinum'
        else:
            return 'rainbow'
        
    def get_rank(self,rank) -> str:
        if 1009000 <= rank <= 1010000:
            return 'SSSp'
        elif 1007500 <= rank <= 1008999:
            return 'SSS'
        elif 1005000 <= rank <= 1007499:
            return 'SSp'
        elif 1000000 <= rank <= 1004999:
            return 'SS'
        elif 990000 <= rank <= 999999:
            return 'Sp'
        elif 975000 <= rank <= 989999:
            return 'S'
        elif 950000 <= rank <= 974999:
            return 'AAA'
        elif 925000 <= rank <= 949999:
            return 'AA'
        elif 900000 <= rank <= 924999:
            return 'A'
        elif 800000 <= rank <= 899999:
            return 'BBB'
        elif 700000 <= rank <= 799999:
            return 'BB'
        elif 600000 <= rank <= 699999:
            return 'B'
        elif 500000 <= rank <= 599999:
            return 'C'
        else:
            return 'D'
    
    def drawRating(self,ratingColor):
        if self.userData.rating < 10:
            drawXCoorDinate = [271,283,295,311]
        else:
            drawXCoorDinate = [255,271,283,295,311]

        averageTotalRating = str(int(self.userData.rating * 100) / 100)  
        if '.0' == averageTotalRating[-2:]:
            averageTotalRating += '0'
        self.userData.rating = averageTotalRating

        for i,v in enumerate(str(self.userData.rating)):
            v = "point" if v == "." else v
            numImg = Image.open(self.pic_dir + f"num/{v}_{ratingColor}.png").convert('RGBA')
            numImg = numImg.resize((18,24))
            self.img.paste(numImg,(drawXCoorDinate[i],173),numImg.split()[3])
    
    def calculationAvgRating(self,ScoreList):
        if len(ScoreList) > 0:
            DetailedRating = sum([score.ra for score in ScoreList])
            averageTotalRating = DetailedRating / len(ScoreList)
            averageTotalRating = str(int(averageTotalRating * 10000) / 10000)  
            if '.0' == averageTotalRating[-2:]:
                averageTotalRating += '000'
            return averageTotalRating
        else:
            return "0.0000"

    def drawDetailedRating(self):
        totalScore = []
        for score in self.userData.recent_10: totalScore.append(score)
        for score in self.userData.best_30: totalScore.append(score)
        averageTotalRating = self.calculationAvgRating(totalScore)
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 16, encoding='utf-8')
        self.imgDraw.text((346, 179), f"({averageTotalRating})", 'black', tempFont)

        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 24, encoding='utf-8')

        averageBest30Rating = self.calculationAvgRating(self.userData.best_30)
        contentX = tempFont.getsize(averageBest30Rating)[0]
        self.imgDraw.text((835-int(contentX/2), 78), f"{averageBest30Rating}", '#1E3663', tempFont)

        averageRecent10Rating = self.calculationAvgRating(self.userData.recent_10)
        contentX = tempFont.getsize(averageRecent10Rating)[0]
        self.imgDraw.text((835-int(contentX/2), 118), f"{averageRecent10Rating}", '#1E3663', tempFont)

        if self.userData.recent_10:
            totalScore = []
            for _ in range(10):
                totalScore.append(self.userData.recent_10[0])
            for score in self.userData.best_30: totalScore.append(score)
            averageMaxRating = self.calculationAvgRating(totalScore)
            contentX = tempFont.getsize(averageMaxRating)[0]
            self.imgDraw.text((835-int(contentX/2), 158), f"{averageMaxRating}", '#1E3663', tempFont)
        else:
            averageMaxRating = '0.0000'
            contentX = tempFont.getsize(averageMaxRating)[0]
            self.imgDraw.text((835-int(contentX/2), 159), f"{averageMaxRating}", '#1E3663', tempFont)


    def drawGenerateUserInfo(self):
        if self.userData.namePlate:
            namePlateFileName = f"CHU_UI_NamePlate_{str(self.userData.namePlate).zfill(8)}.png"
            namePlateImg = Image.open(self.pic_dir + f"nameplate/{namePlateFileName}").convert('RGBA')
            self.img.paste(namePlateImg,(25,31),namePlateImg.split()[3])

        if self.userData.icon:
            temp_str = str(self.userData.icon)
            icon_id = temp_str[:-1] if temp_str[:-1] else "0"
            icon_index = temp_str[-1]
            iconFileName = f"CHU_UI_Character_{icon_id.zfill(4)}_{icon_index.zfill(2)}_02.png"
            iconImg = Image.open(self.pic_dir + f"character/{iconFileName}").convert('RGBA')
            iconImg = iconImg.resize((80,80))
            self.img.paste(iconImg,(495,119),iconImg.split()[3])

        if self.userData.titleContent:
            titleBoxImg = Image.open(self.pic_dir + f"honor/{self.get_trophy_file_id(self.userData.titleColor)}").convert('RGBA')
            titleBoxImg = titleBoxImg.resize((538,50))
            self.img.paste(titleBoxImg,(104,71),titleBoxImg.split()[3])

            tempFont = ImageFont.truetype(self.font_dir + "SourceHanSans_35.otf", 20, encoding='utf-8')
            titleContent = truncate_text(self.userData.titleContent, tempFont, 375)
            contentX,contentY = tempFont.getsize(titleContent)
            self.imgDraw.text((373-int(contentX/2), 92-int(contentY/2)), titleContent, 'black', tempFont)

        userNameBox = Image.open(self.pic_dir + f"name/name_01.png").convert('RGBA')
        self.img.paste(userNameBox,(160,113),userNameBox.split()[3])

        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 20, encoding='utf-8')
        self.imgDraw.text((175, 144), "Lv.", 'black', tempFont)
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 30, encoding='utf-8')
        self.imgDraw.text((206, 135), str(self.userData.level), 'black', tempFont)
        tempFont = ImageFont.truetype(self.font_dir + "SourceHanSans_35.otf", 32, encoding='utf-8')
        userName = truncate_text(self._stringQ2B(self.userData.userName), tempFont, 230)
        self.imgDraw.text((265, 124), userName, 'black', tempFont)

        ratingColor = self.get_rating_color()
        ratingImg = Image.open(self.pic_dir + f"num/rating_{ratingColor}.png").convert('RGBA')
        ratingImg = ratingImg.resize((70,16))
        self.img.paste(ratingImg,(175,180),ratingImg.split()[3])
        self.drawRating(ratingColor)
        self.drawDetailedRating()
        
    def drawMusicBox(self,musicChartInfo:ChartInfo,Bestindex:int,is_r10=False):
        musicBoxImg = Image.open(self.pic_dir + f"chu-frame-{musicChartInfo.diff}.png").convert('RGBA')
        musicBoxImg = musicBoxImg.resize((282,120))
        musicBoxDraw = ImageDraw.Draw(musicBoxImg)

        coverPath = self.cover_dir + f"CHU_UI_Jacket_{str(musicChartInfo.idNum).zfill(4)}.png"
        musicCoverImg = Image.open(coverPath).convert('RGBA')
        musicCoverImg = musicCoverImg.resize((60,60))
        musicBoxImg.paste(musicCoverImg,(17,17),musicCoverImg.split()[3])

        # 曲名
        tempFont = ImageFont.truetype(self.font_dir + "SourceHanSans_35.otf", 16, encoding='utf-8')
        musicTitle = truncate_text(musicChartInfo.title, tempFont, 178)
        musicBoxDraw.text((85, 12), musicTitle, 'white', tempFont)

        # id
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 12, encoding='utf-8')
        musicBoxDraw.text((86, 315-274), "ID "+str(musicChartInfo.idNum), 'white', tempFont)

        # 分数
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 20, encoding='utf-8')
        achievement = f"{musicChartInfo.achievement:,}"
        musicBoxDraw.text((86, 333-274), str(achievement), 'white', tempFont)

        # 评级字母
        rankImg = Image.open(self.pic_dir + f'rank_lmn_edited/UI_GAM_Rank_{self.get_rank(musicChartInfo.achievement)}.png')
        rankImg = rankImg.resize((55,22))
        musicBoxImg.paste(rankImg,(233-19,332-274),rankImg.split()[3])

        # 序号
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-EB.otf", 14, encoding='utf-8')
        musicBoxDraw.text((35-19, 366-274), f"#{Bestindex}", 'black', tempFont)

        # 定数
        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-B.otf", 12, encoding='utf-8')
        contentX = tempFont.getsize(f"{float(musicChartInfo.ds):.1f} ▶")[0]
        musicBoxDraw.text((126-19-contentX, 368-274), f"{float(musicChartInfo.ds):.1f} ▶", 'black', tempFont)

        tempFont = ImageFont.truetype(self.font_dir + "FOT-RodinNTLGPro-EB.otf", 14, encoding='utf-8')
        averageTotalRating = str(int(musicChartInfo.ra * 100) / 100)  
        if '.0' == averageTotalRating[-2:]:
            averageTotalRating += '0'
        if len(averageTotalRating.split('.')[1]) == 1:
            averageTotalRating += '0'
        musicBoxDraw.text((130-19, 366-274), averageTotalRating, 'black', tempFont)

        # 连击情况
        if is_r10:
            fcIconImg = Image.open(self.pic_dir + 'r10_not_support.png').convert('RGBA')
            fcIconImg = fcIconImg.resize((70,16))
            musicBoxImg.paste(fcIconImg,(205-19,1140-1049),fcIconImg.split()[3])
        else:
            fcIconImg = Image.open(self.pic_dir + f'full_combo_{musicChartInfo.comboId}.png').convert('RGBA')
            fcIconImg = fcIconImg.resize((103,16))
            musicBoxImg.paste(fcIconImg,(188-19,365-274),fcIconImg.split()[3])
        return musicBoxImg


    def draw(self):
        self.drawGenerateUserInfo()
        for index,ci in enumerate(self.userData.best_30):
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci,index+1)
            self.img.paste(MusicBoxImg,(18 + (280 * j),250 + (120 * i)),MusicBoxImg.split()[3])

        for index,ci in enumerate(self.userData.recent_10):
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci,index+1,is_r10=True)
            self.img.paste(MusicBoxImg,(18 + (280 * j),1049 + (120 * i)),MusicBoxImg.split()[3])

    def getDir(self):
        return self.img



async def generate_by_lx(user_id):
    statuscode,userData = await UserData.generate_best_30_data_lx_mode(user_id)
    if isinstance(userData,UserData):
        pic = DrawBest(userData).getDir()
        return pic,0
    else:
        return None,statuscode

async def generate_by_df(user_id):
    statuscode,userData = await UserData.generate_best_30_data_df_mode(user_id)
    if isinstance(userData,UserData):
        pic = DrawBest(userData).getDir()
        return pic,0
    else:
        return None,statuscode