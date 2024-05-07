
import asyncio
import os
import math
from typing import Optional, Dict, List, Tuple

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .chunithm_music import get_cover_len4_id, total_list


scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')


class ChartInfo(object):
    def __init__(self, idNum:str, diff:int, achievement:float, rank:float, ra:int, comboId:int,title:str, ds:float, lv:str):
        self.idNum = idNum
        self.diff = diff
        #self.tp = tp
        self.achievement = achievement
        self.rank = rank
        self.ra = ra
        self.comboId = comboId
        #self.scoreId = achievement
        self.title = title
        self.ds = ds
        self.lv = lv


    def __str__(self):
        return '%-50s' % f'{self.title}' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra


    @classmethod
    def from_json(cls, data):
        #rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        #ri = rate.index(data["rate"])
        fc = ['', 'fullcombo', 'alljustice']
        fi = fc.index(data["fc"])
        return cls(
            idNum=total_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            #scoreId=ri,
            lv=data["level"],
            rank=data["score"],
            achievement=data["score"],
            #tp=data["type"]
        )



class BestList(object):

    def __init__(self, size:int):
        self.data = []
        self.size = size

    def push(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while(len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class DrawBest(object):

    def __init__(self, sdBest:BestList, dxBest:BestList, userName:str, playerRating:int, musicRating:int):
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userName = self._stringQ2B(userName)
        self.playerRating = playerRating
        self.musicRating = musicRating
        #self.rankRating = self.playerRating - self.musicRating
        self.pic_dir = 'src/static/chu/pic/'
        self.cover_dir = 'src/static/chu/cover/'
        self.img = Image.open(self.pic_dir + 'UI_TTR_BG_Base_Plus.png').convert('RGBA')
        self.ROWS_IMG = [2]
        for i in range(6):
            self.ROWS_IMG.append(116 + 96 * i)
        self.COLOUMS_IMG = []
        for i in range(6):
            self.COLOUMS_IMG.append(2 + 172 * i)
        for i in range(4):
            self.COLOUMS_IMG.append(888 + 172 * i)
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

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s:str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s:str, len:int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img:Image.Image, time:float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))


    #def _findRaPic(self) -> str:
        #num = '10'
        #if self.playerRating < 1000:
            #num = '01'
        #elif self.playerRating < 2000:
            #num = '02'
        #elif self.playerRating < 3000:
            #num = '03'
        #elif self.playerRating < 4000:
            #num = '04'
        #elif self.playerRating < 5000:
            #num = '05'
        #elif self.playerRating < 6000:
            #num = '06'
        #elif self.playerRating < 7000:
            #num = '07'
        #elif self.playerRating < 8000:
            #num = '08'
        #elif self.playerRating < 8500:
            #num = '09'
        #return f'UI_CMN_DXRating_S_{num}.png'

    #def _drawRating(self, ratingBaseImg:Image.Image):
        #COLOUMS_RATING = [86, 100, 115, 130, 145]
        #theRa = self.playerRating
        #i = 4
        #while theRa:
            #digit = theRa % 10
            #theRa = theRa // 10
            #digitImg = Image.open(self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            #digitImg = self._resizePic(digitImg, 0.6)
            #ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 2, 9), mask=digitImg.split()[3])
            #i = i - 1
        #return ratingBaseImg



    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList):
        itemW = 166
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (90, 20, 0)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        comboPic = ' FC FCp AP APp'.split(' ')
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(sdBest)):
            i = num // 6
            j = num % 6
            chartInfo = sdBest[num]
            rank = get_rank(chartInfo.rank)
            pngPath = self.cover_dir + f'CHU_UI_Jacket_{get_cover_len4_id(chartInfo.idNum)}.png'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir + 'CHU_UI_Jacket_dummy.png'
            temp = Image.open(pngPath).convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{chartInfo.achievement}', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rank}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.5)
            temp.paste(rankImg, (110, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (103, 60), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'DS: {chartInfo.ds} -> {"%.2f" % chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(sdBest), sdBest.size):
            i = num // 6
            j = num % 6
            temp = Image.open(self.cover_dir + f'CHU_UI_Jacket_dummy.png').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(0, len(dxBest)):
            i = num // 2
            j = num % 2
            chartInfo = dxBest[num]
            rank = get_rank(chartInfo.rank)
            pngPath = self.cover_dir + f'CHU_UI_Jacket_{get_cover_len4_id(chartInfo.idNum)}.png'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir + 'CHU_UI_Jacket_dummy.png'
            temp = Image.open(pngPath).convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 13:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{chartInfo.achievement}', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rank}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.5)
            temp.paste(rankImg, (110, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert(
                    'RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (119, 60), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {"%.2f" %chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j + 7] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j + 7] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(dxBest), dxBest.size):
            i = num // 3
            j = num % 3
            temp = Image.open(self.cover_dir + f'CHU_UI_Jacket_dummy.png').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j + 7] + 4, self.ROWS_IMG[i + 1] + 4))

    def draw(self):
        chuLogo = Image.open(self.pic_dir + 'UI_CMN_TabTitle.png').convert('RGBA')
        chuLogo = self._resizePic(chuLogo, 0.65)
        self.img.paste(chuLogo, (10, 10), mask=chuLogo.split()[3])

        #ratingBaseImg = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        #ratingBaseImg = self._drawRating(ratingBaseImg)
        #ratingBaseImg = self._resizePic(ratingBaseImg, 0.85)
        #self.img.paste(ratingBaseImg, (240, 8), mask=ratingBaseImg.split()[3])

        namePlateImg = Image.open(self.pic_dir + 'UI_TST_PlateMask.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((302, 112))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 28, encoding='unic')
        namePlateDraw.text((60, 2), ' '.join(list(self.userName)), 'black', font1)
        shougouDraw = ImageDraw.Draw(namePlateImg)
        font2 = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
        playCountInfo = f'RATING  {"%.2f" % self.musicRating}'
        shougouDraw.text((60, 60), playCountInfo, 'black', font2)

        #nameDxImg = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        #nameDxImg = self._resizePic(nameDxImg, 0.9)
        #namePlateImg.paste(nameDxImg, (230, 4), mask=nameDxImg.split()[3])
        self.img.paste(namePlateImg, (225, 12), mask=namePlateImg.split()[3])
        self._drawBestList(self.img, self.sdBest, self.dxBest)

        authorBoardImg = Image.open(self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        authorBoardImg = self._resizePic(authorBoardImg, 0.35)
        authorBoardDraw = ImageDraw.Draw(self.img)
        authorBoardDraw.text((601, 9), '   Generated by MoeMoeKoishi', 'black', font2)
        self.img.paste(authorBoardImg, (1224, 19), mask=authorBoardImg.split()[3])

        dxImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        self.img.paste(dxImg, (1064, 65), mask=dxImg.split()[3])
        #sdImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        #self.img.paste(sdImg, (758, 65), mask=sdImg.split()[3])

        # self.img.show()

    def getDir(self):
        return self.img

def get_rank(rank:float) -> str:
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

def computeRa(ds: float, achievement:float) -> int:
    baseRa = 15.0
    if achievement >= 50 and achievement < 60:
        baseRa = 5.0
    elif achievement < 70:
        baseRa = 6.0
    elif achievement < 75:
        baseRa = 7.0
    elif achievement < 80:
        baseRa = 7.5
    elif achievement < 90:
        baseRa = 8.0
    elif achievement < 94:
        baseRa = 9.0
    elif achievement < 97:
        baseRa = 9.4
    elif achievement < 98:
        baseRa = 10.0
    elif achievement < 99:
        baseRa = 11.0
    elif achievement < 99.5:
        baseRa = 12.0
    elif achievement < 99.99:
        baseRa = 13.0
    elif achievement < 100:
        baseRa = 13.5
    elif achievement < 100.5:
        baseRa = 14.0

    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)


async def generate(payload: Dict) -> Tuple[Optional[Image.Image], bool]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/chunithmprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        b30_best = BestList(30)
        r10_best = BestList(10)
        obj = await resp.json()
        b30: List[Dict] = obj["records"]["b30"]
        r10: List[Dict] = obj["records"]["r10"]
        for c in b30:
            b30_best.push(ChartInfo.from_json(c))
        for c in r10:
            r10_best.push(ChartInfo.from_json(c))
        pic = DrawBest(b30_best, r10_best, obj["nickname"], obj["rating"], obj["rating"]).getDir()
        return pic, 0
