import nonebot
from fastapi import FastAPI, Response
import io
from src.plugins.maimai.lib.mai_best_50 import mai_best50
import requests
app: FastAPI = nonebot.get_app()


type_map = {
    "SD":"standard",
    "DX":"dx"
}

def translate_df_to_lx(player_data):
    best = []
    for score in player_data:
        id = score['song_id']
        music_type = type_map.get(score['type'])
        if music_type == 'dx':
            id-=10000
        song_name = score['title']
        level = score['level']
        level_index = score['level_index']
        achievements = score['achievements']
        fc = score['fc'] if score['fc'] != "" else None
        fs = score['fs'] if score['fs'] != "" else None
        dx_score = score['dxScore']
        dx_rating = score['ra']
        rate = score['rate']
        best.append({
            "id": id,
            "song_name": song_name,
            "level": level,
            "level_index": level_index,
            "achievements": achievements,
            "fc": fc,
            "fs": fs,
            "dx_score": dx_score,
            "dx_rating": dx_rating,
            "rate": rate,
            "type": music_type
        })
    return best


@app.get("/user-best-50")
async def custom_api(username:str):


    payload = {'username': username.strip(), 'b50': 1}

    lx_data_v = {
        "data":{}
    }

    req = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/player",json=payload)
    player_data = req.json()
    standard_total = sum([score['ra'] for score in player_data['charts']['sd']])
    dx_total = sum([score['ra'] for score in player_data['charts']['dx']])

    lx_data_v['data']['standard_total'] = standard_total
    lx_data_v['data']['dx_total'] = dx_total
    lx_data_v['data']['standard'] = translate_df_to_lx(player_data['charts']['sd'])
    lx_data_v['data']['dx'] = translate_df_to_lx(player_data['charts']['dx'])
    course_rank  = player_data["additional_rating"]
    if course_rank >= 11:
        course_rank  = player_data["additional_rating"] + 1
    other_data = [player_data["nickname"], {'name': 'maimai DX Rating Information', 'color': 'Normal'}, course_rank, 0, {'name': player_data["plate"]}, None, None]

    b64Data = mai_best50.lxns(lx_data_v['data'], other_data)
    img_byte_arr = io.BytesIO()
    # 假设图片是 PNG 格式，你可以根据实际格式进行调整
    b64Data.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return Response(content=img_byte_arr, media_type="image/png")