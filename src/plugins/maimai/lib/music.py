import random
import requests
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy
from collections import namedtuple
from pydantic import BaseModel, Field

#对于json相关，第一个为CN，第二个为JP
import json
with open('src/plugins/maimai/music_data/maidxCN.json', 'r', encoding='utf-8') as f:
    obj = json.load(f)

# with open('src/plugins/maimai/music_data/maidxJP-135B.json', 'r', encoding='utf-8') as f:
#     obj_JP = json.load(f)
    

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

for music_data in obj.values():
    music = Music(music_data)
    for i, chart_data in enumerate(music['charts']):
        music.charts[i] = Chart(chart_data)
    total_list.append(music)

# for music_data in obj_JP.values():
#     music = Music(music_data)
#     for i, chart_data in enumerate(music['charts']):
#         music.charts[i] = Chart(chart_data)
#     total_list_JP.append(music)




