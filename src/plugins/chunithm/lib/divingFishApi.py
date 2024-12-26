import aiohttp

TOKEN = "Ol3pAoaD9NFuUMxdsAg1dwtT1zjGH2Jy"


class divingFishApi:
    API_URL = 'https://www.diving-fish.com/api'
    post = 'POST'
    get = 'GET'

    async def request_json(self, method: str, endpoint: str, params: dict = None, json: dict = None):
        url = f'{self.API_URL}{endpoint}'
        async with aiohttp.ClientSession(headers={"developer-token": TOKEN}) as session:
            async with session.request(method, url, params=params, json=json) as response:
                if response.status != 200:
                    return None
                else:
                    return await response.json()

    def get_request_payload(self, qq: str = None, username: str = None):
        if qq is None and username is None:
            raise ValueError('QQ and username is null')
        else:
            if qq:
                payload = {"qq": qq}
            else:
                payload = {"username": username}
            return payload

    async def chunithmprober_dev_player_record(self, qq: int = None, username: str = None):
        payload = self.get_request_payload(qq=qq, username=username)
        if qq:
            endpoint = f'/chunithmprober/dev/player/records?qq={qq}'
        else:
            endpoint = f'/chunithmprober/dev/player/records?username={username}'
        resp_json = await self.request_json(self.get, endpoint, json=payload)
        return resp_json

df_client = divingFishApi()