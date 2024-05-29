#重要!! 由于晓炎与团队内各位的编程风格有很大不同,故此处使用了aiohttp
#请在合并进master前安装aiohttp或统一代码风格,拜托了
import aiohttp

LXNSAUTH = "pCx9K3Sta3034GljtbR6ykfQfbR12uZbnbYdePcQKGM="
HEADERS = {"Authorization": LXNSAUTH}

async def fetch_mai_best50_lxns(friend_code, ap):
    """
    此函数用于获取玩家的Best50信息

    参数:
        friend_code(str):用户的好友码或者用户名
        ap(bool):是否为ap50

    返回:
        "Not Allow Thirdparty Dev Fetch Score": 玩家隐私设置
        "User Not Found": 未找到用户
        "Score Not Uploaded": 分数未上传

        获取状态(str), best50信息(dict), 玩家信息(list)
    """
    best_url = f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}/bests"
    if ap:
        best_url = f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}/bests/ap"
    async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}", headers = HEADERS) as resp:
        if resp.status == 403:
            return "Not Allow Thirdparty Dev Fetch Score", None, None
        elif resp.status == 404:
            return "User Not Found", None, None
        else:
            playerInfo = await resp.json()
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
    async with aiohttp.request("GET", best_url, headers = HEADERS) as resp:
        if resp.status == 404:
            return "Score Not Uploaded", None, None
        return "Success", await resp.json(), [playerName, playerTrophy, playerCourseRank, playerClassRank, playerPlate, playerIcon, playerFrame]
#---以上为好友码获取---

# async def fetch_mai_best50_lxns_qq(user_qid):
#     """
#     此函数用于获取玩家的Best50信息

#     参数:
#         user_qid(str):用户的QQ号

#     返回:
#         "Not Allow Thirdparty Dev Fetch Score": 玩家隐私设置
#         "User Not Found": 未找到用户
#         "Score Not Uploaded": 分数未上传

#         获取状态(str), best50信息(dict), 玩家信息(list)
#     """
#     async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/qq/{user_qid}", headers = HEADERS) as resp:
#         if resp.status == 403:
#             return "Not Allow Thirdparty Dev Fetch Score", None, None
#         elif resp.status == 404:
#             return "User Not Found", None, None
#         else:
#             playerInfo = await resp.json()
#             playerFC = playerInfo["data"]["friend_code"]
#             playerName = playerInfo["data"]["name"]
#             playerTrophy = playerInfo["data"]["trophy"]
#             playerCourseRank = playerInfo["data"]["course_rank"]
#             playerClassRank = playerInfo["data"]["class_rank"]
#             try:
#                 playerPlate = playerInfo["data"]["name_plate"]
#             except KeyError:
#                 playerPlate = None
#             try:
#                 playerIcon = playerInfo["data"]["icon"]
#             except KeyError:
#                 playerIcon = None
#             try:
#                 playerFrame = playerInfo["data"]["frame"]
#             except KeyError:
#                 playerFrame = None
#             #由于爬取收藏品是可设置的，当参数为None时，调用默认/或不绘制
#     async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/{playerFC}/bests", headers = HEADERS) as resp:
#         if resp.status == 404:
#             return "Score Not Uploaded", None, None
#         return "Success", await resp.json(), [playerName, playerTrophy, playerCourseRank, playerClassRank, playerPlate, playerIcon, playerFrame]
# #以上为QQ号获取

async def fetch_single_score_lxns(friend_code, song_id, song_type):
    #song_type std:标准 dx:DX
    async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}/bests?song_id={song_id}&song_type={song_type}", headers = HEADERS) as resp:
        score = await resp.json()
        if resp.status == 404:
            return "Song Type Not Found", None
        #未找到指定歌曲类型
        if score["data"] == None:
            return "Score Not Found", None
        return "Success", score
        #没有玩过该乐曲