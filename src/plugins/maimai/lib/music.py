import random
import requests
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy
from collections import namedtuple
from pydantic import BaseModel, Field

from .plate_map import VERSION_DF_MAP, VERSION_MAP, DELETED_MUSIC, MAI_DELETED_MUSIC_REM,MAI_DELETED_MUSIC_Normal
from .request_client import HEADERS

#对于json相关，第一个为CN，第二个为JP
import json
with open('src/plugins/maimai/music_data/maidxCN.json', 'r', encoding='utf-8') as f:
    obj = json.load(f)

# with open('src/plugins/maimai/music_data/maidxJP-135B.json', 'r', encoding='utf-8') as f:
#     obj_JP = json.load(f)
scoreRank = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 's+', 'ss', 'ss+', 'sss', 'sss+']
score_Rank = {'d': 'D', 'c': 'C', 'b': 'B', 'bb': 'BB', 'bbb': 'BBB', 'a': 'A', 'aa': 'AA', 'aaa': 'AAA', 's': 'S', 'sp': 'Sp', 'ss': 'SS', 'ssp': 'SSp', 'sss': 'SSS', 'sssp': 'SSSp'}
comboRank = ['fc', 'fc+', 'ap', 'ap+']
combo_rank = ['fc', 'fcp', 'ap', 'app']
syncRank = ['fs', 'fs+', 'fdx', 'fdx+']
sync_rank = ['fs', 'fsp', 'fsd', 'fsdp']
diffs = ['绿', '黄', '红', '紫', '白']
levelList = ['1', '2', '3', '4', '5', '6', '7', '7+', '8', '8+', '9', '9+', '10', '10+', '11', '11+', '12', '12+', '13', '13+', '14', '14+', '15']
achievementList = [50.0, 60.0, 70.0, 75.0, 80.0, 90.0, 94.0, 97.0, 98.0, 99.0, 99.5, 100.0, 100.5]
BaseRaSpp = [7.0, 8.0, 9.6, 11.2, 12.0, 13.6, 15.2, 16.8, 20.0, 20.3, 20.8, 21.1, 21.6, 22.4]
fcl = {'fc': 'FC', 'fcp': 'FCp', 'ap': 'AP', 'app': 'APp'}
fsl = {'fs': 'FS', 'fsp': 'FSp', 'fsd': 'FSD', 'fsdp': 'FSDp'}

plate_to_version = {
    '真极': '6101',
    '真神': '6102',
    '真舞舞': '6103',
    '超极': '6104',
    '超将': '6105',
    '超神': '6106',
    '超舞舞': '6107',
    '檄极': '6108',
    '檄将': '6109',
    '檄神': '6110',
    '檄舞舞': '6111',
    '橙极': '6112',
    '橙将': '6113',
    '橙神': '6114',
    '橙舞舞': '6115',
    '晓极': '6116',
    '晓将': '6117',
    '晓神': '6118',
    '晓舞舞': '6119',
    '桃极': '6120',
    '桃将': '6121',
    '桃神': '6122',
    '桃舞舞': '6123',
    '樱极': '6124',
    '樱将': '6125',
    '樱神': '6126',
    '樱舞舞': '6127',
    '紫极': '6128',
    '紫将': '6129',
    '紫神': '6130',
    '紫舞舞': '6131',
    '堇极': '6132',
    '堇将': '6133',
    '堇神': '6134',
    '堇舞舞': '6135',
    '白极': '6136',
    '白将': '6137',
    '白神': '6138',
    '白舞舞': '6139',
    '雪极': '6140',
    '雪将': '6141',
    '雪神': '6142',
    '雪舞舞': '6143',
    '辉极': '6144',
    '辉将': '6145',
    '辉神': '6146',
    '辉舞舞': '6147',
    '霸者': '6148',
    '舞极': '6149',
    '舞将': '6150',
    '舞神': '6151',
    '舞舞舞': '6152',
    '熊极': '55101',
    '熊将': '55102',
    '熊神': '55103',
    '熊舞舞': '55104',
    '华极': '109101',
    '华将': '109102',
    '华神': '109103',
    '华舞舞': '109104',
    '爽极': '159101',
    '爽将': '159102',
    '爽神': '159103',
    '爽舞舞': '159104',
    '煌极': '209101',
    '煌将': '209102',
    '煌神': '209103',
    '煌舞舞': '209104',
    '宙极': '259101',
    '宙将': '259102',
    '宙神': '259103',
    '宙舞舞': '259104',
    '星极': '309101',
    '星将': '309102',
    '星神': '309103',
    '星舞舞': '309104',
    "祭极": "359101",
    "祭将": "359102",
    "祭神": "359103",
    "祭舞舞": "359104",
    "祝极": "409101",
    "祝将": "409102",
    "祝神": "409103",
    "祝舞舞": "409104",
    "双极": "459101",
    "双将": "459102",
    "双神": "459103",
    "双舞舞": "459104"
}

async def get_player_data(project: str, payload: dict) -> Union[dict, str]:
    import httpx
    maimaiapi = 'https://www.diving-fish.com/api/maimaidxprober'
    """
    获取用户数据，获取失败时返回字符串
    - `project` : 项目
        - `best` : 玩家数据
        - `plate` : 牌子
    - `payload` : 传递给查分器的数据
    """
    if project == 'best':
        p = 'player'
    elif project == 'plate':
        p = 'plate'
    else:
        return '项目错误'
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f'{maimaiapi}/query/{p}', json=payload)
            if resp.status_code == 400:
                data = 'player_error'
            elif resp.status_code == 403:
                data = '该用户禁止了其他人获取数据。'
            elif resp.status_code == 200:
                data = resp.json()
            else:
                data = '未知错误'
    except Exception as e:
        data = f'获取玩家数据时发生错误: {type(e)}'
    return data

async def get_player_data_lx(project: str, payload: str, plate_name: str) -> Union[dict, str]:
    import httpx
    maimaiapi = 'https://maimai.lxns.net/api/v0/maimai/player'
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if project == 'scores':
                p = 'scores'
                resp = await client.get(f'{maimaiapi}/{payload}/{p}', headers=HEADERS)
            elif project == 'plate':
                p = 'plate'
                plate_num = plate_to_version[plate_name]
                resp = await client.get(f'{maimaiapi}/{payload}/{p}/{plate_num}', headers=HEADERS)
            else:
                return '项目错误'
            
            if resp.status_code == 400:
                data = 'player_error'
            elif resp.status_code == 403:
                data = '该用户禁止了其他人获取数据。'
            elif resp.status_code == 200:
                data = resp.json()
            else:
                data = '未知错误'
    except Exception as e:
        data = f'获取玩家数据时发生错误: {type(e)}'
    return data

def findsong_byid(id,index,list):
    for item in list:
        if item["id"] == id and item['level_index'] == index:
            return item
    return None

def plate_process_xray(version, qq: str, plateType: str, vername: str):
    if version[0] in ["舞", "霸"]:
        version_list, version_list_rem = total_list.by_versions_for_cn(VERSION_MAP[version], True)
    else:
        version_list, version_list_rem = total_list.by_versions_for_cn(VERSION_MAP[version], False)

    version_chart_list = [0, 0, 0, 0, 0]
    version_all_chart = 0
    for song in version_list:
        # if len(song["charts"]) == 4:
        for count in range(4):
            version_chart_list[count] = version_chart_list[count] + 1


    if version[0] in ["舞", "霸"]:
        for song in version_list_rem:
            version_chart_list[4] = version_chart_list[4] + 1


    for count in version_chart_list:
        version_all_chart += count
        

    payload = {'qq': qq, 'version': VERSION_DF_MAP[version]}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    finishs = r.json()
    if r.status_code == 400:
        return "未找到该玩家。"
    unfinishList = {0: [], 1: [], 2: [], 3: [], 4: []}

    for song in version_list:
        songid = int(song['id'])
        for index in range(len(song['level'])):
            if index in [0, 1, 2, 3]:
                song_result = findsong_byid(songid, index, finishs['verlist'])
                if song_result:
                    if plateType == '将':
                        if song_result['achievements'] < 100:
                            unfinishList[index].append(song_result)
                    elif plateType == '极':
                        if song_result['fc'] not in ['fc', 'ap', 'fcp', 'app']:
                            unfinishList[index].append(song_result)
                    elif plateType == '神':
                        if song_result['fc'] not in ['ap', 'app']:
                            unfinishList[index].append(song_result)
                    elif plateType == '舞舞':
                        if song_result['fs'] not in ['fsd', 'fsdp']:
                            unfinishList[index].append(song_result)
                    elif plateType == '者':
                        if song_result['achievements'] < 80:
                            unfinishList[index].append(song_result)
                else:
                    unfinishList[index].append(song)

    if version[0] in ["舞", "霸"]:
        for song in version_list_rem:
            songid = int(song['id'])
            for index in range(len(song['level'])):
                if index in [4]:
                    song_result = findsong_byid(songid, index, finishs['verlist'])
                    if song_result:
                        if plateType == '将':
                            if song_result['achievements'] < 100:
                                unfinishList[index].append(song_result)
                        elif plateType == '极':
                            if song_result['fc'] not in ['fc', 'ap', 'fcp', 'app']:
                                unfinishList[index].append(song_result)
                        elif plateType == '神':
                            if song_result['fc'] not in ['ap', 'app']:
                                unfinishList[index].append(song_result)
                        elif plateType == '舞舞':
                            if song_result['fs'] not in ['fsd', 'fsdp']:
                                unfinishList[index].append(song_result)
                        elif plateType == '者':
                            if song_result['achievements'] < 80:
                                unfinishList[index].append(song_result)
                    else:
                        unfinishList[index].append(song)
    # 高难度铺面
    HardSong = ''
    for item in unfinishList[3]:
        if len(unfinishList[3]) > 5:
            break
        if item.get('achievements', -1) >= 0:
            # print(item['level'],1,type(item['level']))
            if item['level'] in ["15", "14+", "14", "13+"]:
                HardSong += str(item['id']) + '. ' + item['title'] + '\n'
        else:
            # print(item['level'],2)
            if item['level'][3] in ["15", "14+", "14", "13+"]:
                HardSong += str(item['id']) + '. ' + item['title'] + '\n'
    if vername in ['舞', '霸']:
        for item in unfinishList[4]:
            if len(unfinishList[4]) > 5:
                break
            if item.get('achievements', -1) >= 0:
                # print(item['level'],1,type(item['level']))
                if item['level'] in ["15", "14+", "14", "13+"]:
                    HardSong += str(item['id']) + '. ' + item['title'] + '\n'
            else:
                # print(item['level'],2)
                if item['level'][3] in ["15", "14+", "14", "13+"]:
                    HardSong += str(item['id']) + '. ' + item['title'] + '\n'
    t = vername + plateType
    SendMsg = f'您的 {t} 完成进度如下：\n'
    unfinishSongCount = len(unfinishList[0]) + len(unfinishList[1]) + len(unfinishList[2]) + len(
        unfinishList[3]) if vername not in ['舞', '者'] else len(unfinishList[0]) + len(unfinishList[1]) + len(
        unfinishList[2]) + len(unfinishList[3]) + len(unfinishList[4])
    unfinishGCount = len(unfinishList[0])
    unfinishYCount = len(unfinishList[1])
    unfinishRCount = len(unfinishList[2])
    unfinishPCount = len(unfinishList[3])
    unfinishREPCount = len(unfinishList[4])
    if unfinishSongCount == 0:
        return f'您已经获得了 {t}。'
    SendMsg += f"已完成 {str(version_all_chart - unfinishSongCount)}/{str(version_all_chart)}， 剩余 {str(unfinishSongCount)}\n"
    if unfinishGCount == 0:
        SendMsg += '绿谱已全部完成\n'
    else:
        SendMsg += f'绿：{str(version_chart_list[0] - unfinishGCount)}/{str(version_chart_list[0])}， 剩余 {str(unfinishGCount)}\n'
    if unfinishYCount == 0:
        SendMsg += '黄谱已全部完成\n'
    else:
        SendMsg += f'黄：{str(version_chart_list[1] - unfinishYCount)}/{str(version_chart_list[1])}， 剩余 {str(unfinishYCount)}\n'
    if unfinishRCount == 0:
        SendMsg += '红谱已全部完成\n'
    else:
        SendMsg += f'红：{str(version_chart_list[2] - unfinishRCount)}/{str(version_chart_list[2])}， 剩余 {str(unfinishRCount)}\n'
    if unfinishPCount == 0:
        SendMsg += f'紫谱已全部完成\n'
    else:
        SendMsg += f'紫：{str(version_chart_list[3] - unfinishPCount)}/{str(version_chart_list[3])}， 剩余 {str(unfinishPCount)}\n'
    if vername in ['舞', '霸']:
        if unfinishREPCount == 0:
            SendMsg += f'白谱已全部完成\n'
        else:
            SendMsg += f'白：{str(version_chart_list[4] - unfinishREPCount)}/{str(version_chart_list[4])}， 剩余 {str(unfinishREPCount)}\n'
    # print(unfinishRCount,unfinishPCount)
    if (unfinishRCount != 0 or unfinishPCount != 0) and vername not in ["舞", "霸"]:
        # print('Join')
        if len(unfinishList[3]) <= 5 and len(unfinishList[3]) != 0:
            SendMsg += '\n未完成高难度谱面还剩下：\n'
        SendMsg += HardSong[0:-1]
    if vername in ["舞", "霸"]:
        if unfinishREPCount == 0:
            SendMsg += f"\n您已经 {t} 确认了"
            SendMsg += '\n请继续加油！'
        else:
            if len(unfinishList[3]) <= 5 and len(unfinishList[3]) != 0:
                SendMsg += '\n\n请继续加油！'
            else:
                SendMsg += '\n请继续加油！'
    else:
        if unfinishPCount == 0:
            SendMsg += f"\n您已经 {t} 确认了" 
            SendMsg += '\n请继续加油！'
        else:
            if len(unfinishList[3]) <= 5 and len(unfinishList[3]) != 0:
                SendMsg += '\n\n请继续加油！'
            else:
                SendMsg += '\n请继续加油！'
    return SendMsg

async def level_process_data(payload: str, match: Tuple):
    song_played = []
    song_remain = []
    song_total = []

    #data = await get_player_data('plate', payload)
    data = await get_player_data_lx('scores', payload)

    if isinstance(data, str):
        return data
    
    # if match[1].lower() in scoreRank:
    #     achievement = achievementList[scoreRank.index(match[1].lower()) - 1]
    #     for song in data['verlist']:
    #         if song['level'] == match[0] and song['achievements'] < achievement:
    #             song_remain.append([song['id'], song['level_index']])
                
    #         song_played.append([song['id'], song['level_index']])
    # elif match[1].lower() in comboRank:
    #     combo_index = comboRank.index(match[1].lower())
    #     for song in data['verlist']:
    #         if song['level'] == match[0] and ((song['fc'] and combo_rank.index(song['fc']) < combo_index) or not song['fc']):
    #             song_remain.append([song['id'], song['level_index']])
    #         song_played.append([song['id'], song['level_index']])
    # elif match[1].lower() in syncRank:
    #     sync_index = syncRank.index(match[1].lower())
    #     for song in data['verlist']:
    #         if song['level'] == match[0] and ((song['fs'] and sync_rank.index(song['fs']) < sync_index) or not song['fs']):
    #             song_remain.append([song['id'], song['level_index']])
    #         song_played.append([song['id'], song['level_index']])
    # for music in total_list:
    #     for i, lv in enumerate(music.level[2:]):
    #         if lv == match[0]:
    #             song_total.append([song['id']])
    #         if lv == match[0] and [int(music.id), i + 2] not in song_played:
    #             song_remain.append([int(music.id), i + 2])

    if match[1].lower() in scoreRank:
        #achievement = achievementList[scoreRank.index(match[1].lower()) - 1]
        for song in data['data']:
            if song['level'] == match[0] and song['rate'] == match[1]:
                song_remain.append([song['id'], song['level_index']])
                
            song_played.append([song['id'], song['level_index']])
    elif match[1].lower() in comboRank:
        combo_index = comboRank.index(match[1].lower())
        for song in data['verlist']:
            if song['level'] == match[0] and ((song['fc'] and combo_rank.index(song['fc']) < combo_index) or not song['fc']):
                song_remain.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match[1].lower() in syncRank:
        sync_index = syncRank.index(match[1].lower())
        for song in data['verlist']:
            if song['level'] == match[0] and ((song['fs'] and sync_rank.index(song['fs']) < sync_index) or not song['fs']):
                song_remain.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    for music in total_list:
        for i, lv in enumerate(music.level[2:]):
            if lv == match[0]:
                song_total.append([song['id']])
            if lv == match[0] and [int(music.id), i + 2] not in song_played:
                song_remain.append([int(music.id), i + 2])

    song_total = sorted(song_total, key=lambda i: int(i[0]))
    song_remain = sorted(song_remain, key=lambda i: int(i[1]))
    song_remain = sorted(song_remain, key=lambda i: int(i[0]))
    # songs = []
    # for song in song_remain:
    #     music = total_list.by_id(str(song[0]))
    #     songs.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], song[1]])

    r_total = len(song_total) - len(song_remain)
    msg = '\n'
    #song_record = [[s['id'], s['level_index']] for s in data['verlist']]
    msg += f'您的 {match[0]}  {match[1].upper()}\n'
    msg += f'完成进度：{r_total} / {len(song_total)}\n'
    msg += f'还有 {len(song_remain)} 张谱面！'

    return msg


Notes1 = namedtuple('Notes', ['tap', 'hold', 'slide', 'brk'])
Notes2 = namedtuple('Notes', ['tap', 'hold', 'slide', 'touch', 'brk'])


class Chart(Dict):

    notes: Optional[Union[Notes1, Notes2]]
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self.get('notes', [0])[0]
        elif item == 'hold':
            return self.get('notes', [0])[1]
        elif item == 'slide':
            return self.get('notes', [0])[2]
        elif item == 'touch':
            return self.get('notes', [0])[3] if len(self.get('notes', [])) == 5 else 0
        elif item == 'brk':
            return self.get('notes', [0])[-1]
        elif item == 'charter':
            return self.get('charter')
        return super().__getattribute__(item)


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret

class Stats(BaseModel):

    cnt: Optional[float] = None
    diff: Optional[str] = None
    fit_diff: Optional[float] = None
    avg: Optional[float] = None
    avg_dx: Optional[float] = None
    std_dev: Optional[float] = None
    dist: Optional[List[int]] = None
    fc_dist: Optional[List[float]] = None


class BasicInfo(BaseModel):

    title: Optional[str]
    artist: Optional[str]
    genre: Optional[str]
    bpm: Optional[int]
    release_date: Optional[str]
    version: Optional[str] = Field(alias='from')
    is_new: Optional[bool]

class Music(Dict):


    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    charts: Optional[List[Chart]] = []
    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version'}:
            if item == 'version':
                return self['basic_info'].get('from')
            return self['basic_info'].get(item)
        elif item in self:
            return self[item]
        return super().__getattribute__(item)



class MusicList(List[Music]):
    def by_versions_for_cn(self,music_version,is_mai_version:bool = False) -> Optional[Music]:
        musiclist = []
        musiclist_rem = []
        if is_mai_version:
            for music in self:
                if int(music.id) > 99999:
                    continue
                if int(music.id) in MAI_DELETED_MUSIC_REM:
                    musiclist_rem.append(music)
            for music in self:
                if int(music.id) > 99999:
                    continue
                if int(music.id) in MAI_DELETED_MUSIC_Normal:
                    musiclist.append(music)
        else:
            for music in self:
                if int(music.id) > 99999:
                    continue
                if int(music.id) in DELETED_MUSIC:
                    continue
                if music.version in music_version:
                    musiclist.append(music)
        return musiclist, musiclist_rem

    def by_id(self, music_id: str) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self):
        return random.choice(self)

    def filter(self,
               *,
               level_search: Optional[Union[str, List[str]]] = ...,
               level_search2: Optional[Union[str, List[str]]] = ...,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               artist: Optional[str] = ...,
               title_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               total: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue

            if int(music.id) > 100000:
                continue
            #由于宴会场暂时不在考虑范围内，因此先跳过对宴会场的随机

            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if total is not Ellipsis:
                #chart = music['charts']
                total_notes = []
                for chart in music['charts']:
                    #total_notes.append(sum(chart["notes"]))
                    total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                music["total_notes"] = total_notes
                combo = music["total_notes"]
                if not any(t == total for t in total_notes):
                    continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            if artist is not Ellipsis and artist.lower() not in music.artist.lower():
                continue
            if level_search is not Ellipsis:
                color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
                index = color_to_index.get(level_search.lower())
                if index < len(music.ds) and music.ds[index] == ds:
                    pass
                else:
                    continue
            if level_search2 is not Ellipsis:
                color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '白': 4}
                index = color_to_index.get(level_search2.lower())
                if index < len(music.level) and music.level[index] == level:
                    pass
                else:
                    continue
            music.diff = diff2
            new_list.append(music)
        return new_list
    
class Alias(BaseModel):

    song_id: Optional[int] = None
    aliases: Optional[List[str]] = None

class AliasList(List[Alias]):

    # def by_id(self, music_id: int) -> Optional[List[Alias]]:
    #     alias_music = []
    #     for music in self:
    #         if music.song_id == int(music_id):
    #             alias_music.append(music)
    #     return alias_music
    
    def by_id(self, music_id: int) -> Optional[List[Alias]]:
        alias_music = []
        for music in self:
            if music_id == music.song_id:
                alias_music.extend(music.aliases)
        return "\n".join(alias_music) if alias_music else None
    
    def by_alias(self, music_alias: str) -> Optional[List[Alias]]:
        alias_music = []
        for music in self:
            for alias in music.aliases:
                if music_alias == alias:
                    alias_music.append(music)
                    break  # 如果找到匹配的别名，就不需要再检查这个音乐的其他别名了
        print(alias_music)
        return alias_music
    
alias_data = []
total_alias_list = AliasList()

try:
    response = requests.get("https://download.fanyu.site/maimai/alias.json")
    response.raise_for_status()  # 检查请求是否成功  
    alias_data = response.json()
    # 将JSON数据转换为Alias对象的列表  
    alias_data = response.json()
    aliases = [Alias(song_id=key, aliases=value) for key, value in alias_data.items()]
    total_alias_list.extend(aliases)
except Exception as e:
    print(f'{e}')

#total_alias_list = AliasList(alias_data)
# for _ in range(len(total_alias_list)):
#     total_alias_list[_] = Alias(**alias_data[_])


total_list = MusicList()
total_list_JP = MusicList()

for music_data in obj:
    music = Music(music_data)
    for i, chart_data in enumerate(music['charts']):
        music.charts[i] = Chart(chart_data)
    total_list.append(music)

# for music_data in obj_JP.values():
#     music = Music(music_data)
#     for i, chart_data in enumerate(music['charts']):
#         music.charts[i] = Chart(chart_data)
#     total_list_JP.append(music)


#     if match[0] == '真':
#         verlist = list(filter(lambda x: x['title'] != 'ジングルベル', data['verlist']))
#     else:
#         verlist = data['verlist']

#     if match[1] in ['将', '者']:
#         for song in verlist:
#             if song['level_index'] == 0 and song['achievements'] < (100.0 if match[1] == '将' else 80.0):
#                 song_remain_basic.append([song['id'], song['level_index']])
#             if song['level_index'] == 1 and song['achievements'] < (100.0 if match[1] == '将' else 80.0):
#                 song_remain_advanced.append([song['id'], song['level_index']])
#             if song['level_index'] == 2 and song['achievements'] < (100.0 if match[1] == '将' else 80.0):
#                 song_remain_expert.append([song['id'], song['level_index']])
#             if song['level_index'] == 3 and song['achievements'] < (100.0 if match[1] == '将' else 80.0):
#                 song_remain_master.append([song['id'], song['level_index']])
#             if match[0] in ['舞', '霸'] and song['level_index'] == 4 and song['achievements'] < (100.0 if match[1] == '将' else 80.0):
#                 song_remain_re_master.append([song['id'], song['level_index']])
#             song_played.append([song['id'], song['level_index']])
#     elif match[1] in ['極', '极']:
#         for song in verlist:
#             if song['level_index'] == 0 and not song['fc']:
#                 song_remain_basic.append([song['id'], song['level_index']])
#             if song['level_index'] == 1 and not song['fc']:
#                 song_remain_advanced.append([song['id'], song['level_index']])
#             if song['level_index'] == 2 and not song['fc']:
#                 song_remain_expert.append([song['id'], song['level_index']])
#             if song['level_index'] == 3 and not song['fc']:
#                 song_remain_master.append([song['id'], song['level_index']])
#             if match[0] == '舞' and song['level_index'] == 4 and not song['fc']:
#                 song_remain_re_master.append([song['id'], song['level_index']])
#             song_played.append([song['id'], song['level_index']])
#     elif match[1] == '舞舞':
#         for song in verlist:
#             if song['level_index'] == 0 and song['fs'] not in ['fsd', 'fsdp']:
#                 song_remain_basic.append([song['id'], song['level_index']])
#             if song['level_index'] == 1 and song['fs'] not in ['fsd', 'fsdp']:
#                 song_remain_advanced.append([song['id'], song['level_index']])
#             if song['level_index'] == 2 and song['fs'] not in ['fsd', 'fsdp']:
#                 song_remain_expert.append([song['id'], song['level_index']])
#             if song['level_index'] == 3 and song['fs'] not in ['fsd', 'fsdp']:
#                 song_remain_master.append([song['id'], song['level_index']])
#             if match[0] == '舞' and song['level_index'] == 4 and song['fs'] not in ['fsd', 'fsdp']:
#                 song_remain_re_master.append([song['id'], song['level_index']])
#             song_played.append([song['id'], song['level_index']])
#     elif match[1] == '神':
#         for song in verlist:
#             if song['level_index'] == 0 and song['fc'] not in ['ap', 'app']:
#                 song_remain_basic.append([song['id'], song['level_index']])
#             if song['level_index'] == 1 and song['fc'] not in ['ap', 'app']:
#                 song_remain_advanced.append([song['id'], song['level_index']])
#             if song['level_index'] == 2 and song['fc'] not in ['ap', 'app']:
#                 song_remain_expert.append([song['id'], song['level_index']])
#             if song['level_index'] == 3 and song['fc'] not in ['ap', 'app']:
#                 song_remain_master.append([song['id'], song['level_index']])
#             if match[0] == '舞' and song['level_index'] == 4 and song['fc'] not in ['ap', 'app']:
#                 song_remain_re_master.append([song['id'], song['level_index']])
#             song_played.append([song['id'], song['level_index']])
#     for music in total_list:
#         if match[0] == '真' and music.title == 'ジングルベル':
#             continue
#         if music['basic_info']['from'] in payload['version']:
#             total_basic.append([int(music.id), 0])
#             total_advanced.append([int(music.id), 1])
#             total_expert.append([int(music.id), 2])
#             total_master.append([int(music.id), 3])
#             total_re_master.append([int(music.id), 4])
#             if [int(music.id), 0] not in song_played:
#                 song_remain_basic.append([int(music.id), 0])
#             if [int(music.id), 1] not in song_played:
#                 song_remain_advanced.append([int(music.id), 1])
#             if [int(music.id), 2] not in song_played:
#                 song_remain_expert.append([int(music.id), 2])
#             if [int(music.id), 3] not in song_played:
#                 song_remain_master.append([int(music.id), 3])
#             if match[0] in ['舞', '霸'] and len(music.level) == 5 and [int(music.id), 4] not in song_played:
#                 song_remain_re_master.append([int(music.id), 4])
#     total_basic = sorted(total_basic, key=lambda i: int(i[0]))
#     total_advanced = sorted(total_advanced, key=lambda i: int(i[0]))
#     total_expert = sorted(total_expert, key=lambda i: int(i[0]))
#     total_master = sorted(total_master, key=lambda i: int(i[0]))
#     total_re_master = sorted(total_re_master, key=lambda i: int(i[0]))
#     song_remain_basic = sorted(song_remain_basic, key=lambda i: int(i[0]))
#     song_remain_advanced = sorted(song_remain_advanced, key=lambda i: int(i[0]))
#     song_remain_expert = sorted(song_remain_expert, key=lambda i: int(i[0]))
#     song_remain_master = sorted(song_remain_master, key=lambda i: int(i[0]))
#     song_remain_re_master = sorted(song_remain_re_master, key=lambda i: int(i[0]))
#     for song in song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master:
#         music = total_list.by_id(str(song[0]))
#         if music.ds[song[1]] > 13.6:
#             song_remain_difficult.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], song[1]])


#     # total_basic = len([music for music in total_list if music['basic_info']['from'] in payload['version'][0]])
#     # print(f"绿：{[s for s in verlist if s['level_index'] == 0]}")
#     # total_advanced = len([music for music in total_list if music['basic_info']['from'] in payload['version']== 1])
#     # total_expert = len([music for music in total_list if music['basic_info']['from'] in payload['version']== 2])
#     # total_master = len([music for music in total_list if music['basic_info']['from'] in payload['version']== 3])
#     # print(f"紫：{[music for music in total_list if music['basic_info']['from'] in payload['version']== 3]}")
#     # total_re_master = len([music for music in total_list if music['basic_info']['from'] in payload['version']== 4])

#     completed_basic = len(total_basic )-len(song_remain_basic)
#     completed_advanced = len(total_advanced)-len(song_remain_advanced) 
#     completed_expert = len(total_expert)-len(song_remain_expert) 
#     completed_master = len(total_master) -len(song_remain_master)  
#     completed_re_master =len(total_re_master)-len(song_remain_re_master) 

#     total_songs_noRe = len(song_remain_basic) + len(song_remain_advanced) + len(song_remain_expert) + len(song_remain_master)
#     completed_songs = completed_basic + completed_advanced + completed_expert + completed_master + completed_re_master
#     c_total = total_basic + total_advanced + total_expert + total_master
# msg =
#     song_remain: list[list] = song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master
#     song_record = [[s['id'], s['level_index']] for s in verlist]
#     if match[0] in ['舞', '霸']:
#         msg += f'白：{len(total_re_master) - len(song_remain_re_master)}/{len(total_re_master)}，剩余 {len(song_remain_re_master)}\n'
#     if len(song_remain_difficult) > 0:
#         if len(song_remain_difficult) < 5:
#             msg += '等级 13+ 以上剩余的谱面：\n'
#             for i, s in enumerate(song_remain_difficult):
#                 self_record = ''
#                 if [int(s[0]), s[-1]] in song_record:
#                     record_index = song_record.index([int(s[0]), s[-1]])
#                     if match[1] in ['将', '者']:
#                         self_record = str(verlist[record_index]['achievements']) + '%'
#                     elif match[1] in ['極', '极', '神']:
#                         if verlist[record_index]['fc']:
#                             self_record = comboRank[combo_rank.index(verlist[record_index]['fc'])].upper()
#                     elif match[1] == '舞舞':
#                         if verlist[record_index]['fs']:
#                             self_record = syncRank[sync_rank.index(verlist[record_index]['fs'])].upper()
#                 msg += f'{s[0]} {s[2]} {s[1]} {s[3]} {self_record}'.strip() + '\n'
#         else:
#             msg += '等级 13+ 以上剩余的谱面：\n'
#             for i, s in enumerate(song_remain_difficult[:5]):
#                 self_record = ''
#                 if [int(s[0]), s[-1]] in song_record:
#                     record_index = song_record.index([int(s[0]), s[-1]])
#                     if match[1] in ['将', '者']:
#                         self_record = str(verlist[record_index]['achievements']) + '%'
#                     elif match[1] in ['極', '极', '神']:
#                         if verlist[record_index]['fc']:
#                             self_record = comboRank[combo_rank.index(verlist[record_index]['fc'])].upper()
#                     elif match[1] == '舞舞':
#                         if verlist[record_index]['fs']:
#                             self_record = syncRank[sync_rank.index(verlist[record_index]['fs'])].upper()
#                 msg += f'{s[0]} {s[2]} {s[1]} {s[3]} {self_record}'.strip() + '\n'
#             msg += f'还有 {len(song_remain_difficult) - 5} 首13+定数的曲目未展示。'
#     elif len(song_remain) > 0:
#         for i, s in enumerate(song_remain):
#             m = total_list.by_id(str(s[0]))
#             ds = m.ds[s[1]]
#             song_remain[i].append(ds)
#         if len(song_remain) < 5:
#             msg += '剩余曲目：\n'
#             for i, s in enumerate(sorted(song_remain, key=lambda i: i[2])):
#                 m = total_list.by_id(str(s[0]))
#                 self_record = ''
#                 if [int(s[0]), s[-1]] in song_record:
#                     record_index = song_record.index([int(s[0]), s[-1]])
#                     if match[1] in ['将', '者']:
#                         self_record = str(verlist[record_index]['achievements']) + '%'
#                     elif match[1] in ['極', '极', '神']:
#                         if verlist[record_index]['fc']:
#                             self_record = comboRank[combo_rank.index(verlist[record_index]['fc'])].upper()
#                     elif match[1] == '舞舞':
#                         if verlist[record_index]['fs']:
#                             self_record = syncRank[sync_rank.index(verlist[record_index]['fs'])].upper()
#                 msg += f'{m.id} {m.title} {diffs[s[1]]} {m.ds[s[1]]} {self_record}'.strip() + '\n'
#         else:
#             msg += '已经没有定数大于13.6的曲目了,加油清谱！\n'
#     else:
#         msg += f'恭喜您完成{match[0]}{match[1]}！'


