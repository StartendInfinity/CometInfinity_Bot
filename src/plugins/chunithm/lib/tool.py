import time
import base64
import json
import os
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont



def hash(qq: int):
    days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
        time.strftime("%m", time.localtime(time.time()))) + 77
    return (days * qq) >> 8

def image_to_base64_gif(imgPath):
    with open(imgPath, "rb") as f:
        base64_data = base64.b64encode(f.read())
        f.close()
    return base64_data

def readJson(path):
    with open(path, 'r',encoding='utf-8') as f:
        tempData = json.load(f)
        f.close()
    return tempData

def writeJson(path,data):
    with open(path, 'w+', encoding="utf-8")as f:
        json.dump(data, f,ensure_ascii=False)
        f.close()
    return 0

def getRandomFile(path):
    FileList = []
    for root, dirs, files in os.walk(path):
        for file in files:
            FileList.append(os.path.join(root, file))
    return FileList[random.randint(0, len(FileList)-1)]

def TextToImg(text):
    bgImg = Image.new("RGB", (1920, 1080), (255, 255, 255))
    bgImgDr = ImageDraw.Draw(bgImg)
    font = ImageFont.truetype(os.path.join("fonts", "simhei.ttf"), 15)
    imgSize = bgImgDr.multiline_textsize(text, font=font)
    newImg = bgImg.resize((imgSize[0] + 10, imgSize[1] + 10))
    newImgDr = ImageDraw.Draw(newImg)
    newImgDr.text((1, 1), text, font=font, fill="#000000")
    return newImg

def wrap_text(text, font, max_width):
    lines = []
    line = ''
    for char in text:
        if font.getsize(line + char)[0] <= max_width:
            line += char
        else:
            lines.append(line)
            line = char
    lines.append(line)  # 添加最后一行
    return lines

def truncate_text(text, font, max_width):
    if font.getsize(text)[0] <= max_width:
        return text
    else:
        for i in range(len(text), 0, -1):
            if font.getsize(text[:i] + '...')[0] <= max_width:
                return text[:i] + '...'
        return '...'
