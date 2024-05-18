#重要!! 由于晓炎与团队内各位的编程风格有很大不同,故此处使用了aiohttp
#请在合并进master前安装aiohttp或统一代码风格,拜托了
import aiohttp

LXNSAUTH = "pCx9K3Sta3034GljtbR6ykfQfbR12uZbnbYdePcQKGM="
HEADERS = {"Authorization": LXNSAUTH}

async def fetch_mai_best50_lxns(friend_code):
    """
    此函数用于获取玩家的Best50信息

    参数:
        friend_code(str):用户的好友码或者用户名

    返回:
        "Not Allow Thirdparty Dev Fetch Score": 玩家隐私设置
        "User Not Found": 未找到用户
        "Score Not Uploaded": 分数未上传

        获取状态(str), best50信息(dict), 玩家信息(list)
    """
    async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}", headers = HEADERS) as resp:
        if resp.status == 403:
            return "Not Allow Thirdparty Dev Fetch Score", None, None
        elif resp.status == 404:
            return "User Not Found", None, None
        else:
            playerInfo = await resp.json()
            playerFC = playerInfo["data"]["friend_code"]
            playerName = playerInfo["data"]["name"]
            playerTrophy = playerInfo["data"]["trophy"]
            playerCourseRank = playerInfo["data"]["course_rank"]
            playerClassRank = playerInfo["data"]["class_rank"]
            try:
                playerPlate = playerInfo["data"]["name_plate"]
            except:
                playerPlate = None
            #由于爬取姓名框是可设置的，当参数为None时，调用默认姓名框
    async with aiohttp.request("GET", f"https://maimai.lxns.net/api/v0/maimai/player/{friend_code}/bests", headers = HEADERS) as resp:
        if resp.status == 404:
            return "Score Not Uploaded", None, None
        return "Success", await resp.json(), [playerName, playerTrophy, playerCourseRank, playerClassRank, playerPlate]