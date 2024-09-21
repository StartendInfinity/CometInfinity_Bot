import aiohttp
DEVELOPER_TOKEN = "Ol3pAoaD9NFuUMxdsAg1dwtT1zjGH2Jy"

class DivingFishClient:
    BASE_URL = 'https://www.diving-fish.com/api'
    post = "POST"
    get = "GET"

    async def request_json(self, method: str, endpoint: str, params: dict = None, json: dict = None):
        """
        发送异步 HTTP 请求，并自动管理会话。
        
        :param method: HTTP 方法 (GET, POST, etc.)
        :param endpoint: API 的具体 endpoint (例如 '/data')
        :param params: 查询参数 (适用于 GET 请求)
        :param json: 请求体 (适用于 POST 请求)
        :return: 返回 HTTP 响应
        """
        url = f'{self.BASE_URL}{endpoint}'

        # 使用上下文管理器来自动关闭会话
        async with aiohttp.ClientSession(headers={"developer-token": DEVELOPER_TOKEN}) as session:
            async with session.request(method, url, params=params, json=json) as response:
                return await response.json()
    
    def get_request_payload(self,qq:str = None,username:str = None):
        if qq is None and username is None:
            raise ValueError("qq and username is null")
        else:
            if qq:
                payload = {"qq":qq}
            else:
                payload = {"username":username}
            return payload
    

    async def maimaidxprober_query_plate(self,version_list:list,qq:int = None,username:str = None):
        payload = self.get_request_payload(qq=qq,username=username)
        payload['version'] = version_list
        endpoint = '/maimaidxprober/query/plate'
        resp_json = await self.request_json(self.post,endpoint,json=payload)
        return resp_json
    

    async def maimaidxprober_dev_player_record(self,music_list:list,qq:int = None,username:str = None):
        payload = self.get_request_payload(qq=qq,username=username)
        payload['music_id'] = music_list
        endpoint = '/maimaidxprober/dev/player/record'
        resp_json = await self.request_json(self.post,endpoint,json=payload)
        return resp_json
    
df_client = DivingFishClient()