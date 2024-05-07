import json
import random
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy
from pydantic import BaseModel


from .. import json_update
import requests

def get_cover_len4_id(mid) -> str:
    mid = int(mid)
    if 10001 <= mid:
        mid -= 10000
    return f'{mid:04d}'

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


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


# class Chart(BaseModel):
#     total: Optional[int] = None
#     tap: Optional[int] = None
#     slide: Optional[int] = None
#     hold: Optional[int] = None
#     air: Optional[int] = None
#     flick: Optional[int] = None
class Chart(BaseModel):  
    total: int  
    tap: int  
    hold: int  
    slide: int  
    air: int  
    flick: int 
    

    
class diffi(BaseModel):  
    difficulty: Optional[int] = None  
    level: Optional[str] = None  
    level_value: Optional[float] = None  
    note_designer: Optional[str] = None  
    notes: Optional[List[Chart]] = []

def dict_to_chart(notes_dict):  
    return Chart(**notes_dict)



class Song(BaseModel):

    id: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    bpm: Optional[int] = None
    difficulties: List[Dict] = []
    #difficulties: Optional[List[Optional[diffi]]] = []


class Music(Dict):
    id: Optional[int] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[int] = None
    version: Optional[str] = None
    charts: Optional[Chart] = None
    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)

# class SongList(List[Song]):
#     def by_id(self, music_id: int) -> Optional[Song]:
#         for music in self:
#             if int(music.id) == music_id:
#                 return music
#         return None

#     def by_title(self, music_title: str) -> Optional[Song]:
#         for music in self:
#             if music.title == music_title:
#                 return music
#         return None

#     def random(self):
#         return random.choice(self)

#     def filter(self,
#                *,
#                level: Optional[Union[str, List[str]]] = ...,
#                ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
#                title_search: Optional[str] = ...,
#                genre: Optional[Union[str, List[str]]] = ...,
#                bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
#                type: Optional[Union[str, List[str]]] = ...,
#                diff: List[int] = ...,
#                ):
#         new_list = MusicList()
#         for music in self:
#             diff2 = diff
#             music = deepcopy(music)
#             ret, diff2 = cross(music.level, level, diff2)
#             if not ret:
#                 continue
#             ret, diff2 = cross(music.ds, ds, diff2)
#             if not ret:
#                 continue
#             if not in_or_equal(music.genre, genre):
#                 continue
#             if not in_or_equal(music.type, type):
#                 continue
#             if not in_or_equal(music.bpm, bpm):
#                 continue
#             if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
#                 continue
#             music.diff = diff2
#             new_list.append(music)
#         return new_list




class MusicList(List[Music]):
    def by_id(self, music_id: int) -> Optional[Music]:
        for music in self:
            if int(music.id) == music_id:
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
                    total_notes.append(chart["combo"])
                    #total_notes.append(sum([int(note) for note in chart["notes"] if isinstance(note, (int, str))]))
                music["total_notes"] = total_notes
                combo = music["total_notes"]
                if not any(t == total for t in total_notes):
                    continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            if artist is not Ellipsis and artist.lower() not in music.artist.lower():
                continue
            if level_search is not Ellipsis:
                color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '黑': 4}
                index = color_to_index.get(level_search.lower())
                if index < len(music.ds) and music.ds[index] == ds:
                    pass
                else:
                    continue
            if level_search2 is not Ellipsis:
                color_to_index = {'绿': 0, '黄': 1, '红': 2, '紫': 3, '黑': 4}
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
        return alias_music
    
alias_data = []
total_alias_list = AliasList()

try:
    response = requests.get("https://maimai.lxns.net/api/v0/chunithm/alias/list")
    response.raise_for_status()  # 检查请求是否成功  
    alias_data = response.json()
    # 将JSON数据转换为Alias对象的列表
    aliases = [Alias(**alias) for alias in alias_data['aliases']]  
    total_alias_list.extend(aliases)
except Exception as e:
    print(f'{e}')


    # def filter(self,
    #            *,
    #            level: Optional[Union[str, List[str]]] = ...,
    #            ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
    #            title_search: Optional[str] = ...,
    #            genre: Optional[Union[str, List[str]]] = ...,
    #            bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
    #            type: Optional[Union[str, List[str]]] = ...,
    #            diff: List[int] = ...,
    #            ):
    #     new_list = MusicList()
    #     for music in self:
    #         diff2 = diff
    #         music = deepcopy(music)
    #         ret, diff2 = cross(music.level, level, diff2)
    #         if not ret:
    #             continue
    #         ret, diff2 = cross(music.ds, ds, diff2)
    #         if not ret:
    #             continue
    #         if not in_or_equal(music.genre, genre):
    #             continue
    #         if not in_or_equal(music.type, type):
    #             continue
    #         if not in_or_equal(music.bpm, bpm):
    #             continue
    #         if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
    #             continue
    #         music.diff = diff2
    #         new_list.append(music)
    #     return new_list


with open('src/plugins/chunithm/music_data/music_data.json', 'r', encoding='utf-8') as f:
    obj = json.load(f)
total_list: MusicList = MusicList(obj)
for __i in range(len(total_list)):
    total_list[__i] = Music(total_list[__i])
    # for __j in range(len(total_list[__i].charts)):
    #     total_list[__i].charts[__j] = Chart(total_list[__i].charts[__j])

def song_get(mid: int):
    #obj2 = requests.get(f'https://maimai.lxns.net/api/v0/chunithm/song/{mid}').json()
    try:
        obj2 = requests.get(f'https://maimai.lxns.net/api/v0/chunithm/song/{mid}').json()
        #song_list: SongList = SongList(obj2)
        song_data = obj2.copy()  # 创建一个副本，以免修改原始数据  
        difficulties = []  # 创建一个新的列表来存储diffi实例  
        # 在遍历difficulties时转换notes  
        for diff_dict in song_data.get('difficulties', []):  
            notes_dict = diff_dict.get('notes', {})  
            chart_instance = dict_to_chart(notes_dict) if notes_dict else None  
            diff_dict['notes'] = [chart_instance] if chart_instance else []  
            difficulties.append(diffi(**diff_dict))  
        # 更新song实例中的difficulties字段  
        song_data['difficulties'] = difficulties  
        song = Song(**song_data)  
        return song
    except Exception as e:
        return e
