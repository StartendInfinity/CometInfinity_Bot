from .chunithm_music import total_list
from .request_client import generate_best_30_data

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
        fc = ['', 'fullcombo', 'alljustice']
        fi = fc.index(data["fc"])
        return cls(
            idNum=total_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            lv=data["level"],
            rank=data["score"],
            achievement=data["score"],
        )

    @classmethod
    def from_json_by_lx(cls, data):
        
        def check_is_ajc(achievement,comboId):
            fc = [None, 'fullcombo', 'alljustice']
            if achievement == 1010000:
                return 3
            else:
                return fc.index(comboId)
            
        fi = check_is_ajc(data['score'],data["full_combo"])
        return cls(
            idNum=data['id'],
            title=data["song_name"],
            diff=data["level_index"],
            ra=data["rating"],
            ds=total_list.by_id(int(data['id'])).ds[data["level_index"]],
            comboId=fi,
            lv=data["level"],
            rank=data["rank"],
            achievement=data["score"],
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

class UserData(object):
    def __init__(self, user_Name,rating,best_30,recent_10,namePlate=None,icon=None,titleColor=None,titleContent=None,level=None):
        self.userName = user_Name
        self.rating = rating
        self.best_30 = best_30
        self.recent_10 = recent_10,
        self.namePlate = namePlate
        self.titleColor = titleColor
        self.titleContent = titleContent
        self.level = level
        self.icon = icon

    def __str__(self) -> str:
        return f"{self.userName}-{self.rating}-{self.namePlate}-{self.icon}-{len(self.best_30)}-{len(self.recent_10)}"

    @classmethod  
    async def generate_best_30_data_by_lx(cls, user_id):  
        status_code, player_data = await generate_best_30_data(user_id)
        if status_code != 200:
            return None,status_code
        b30_best = BestList(30)
        r10_best = BestList(10)
        b30 = player_data["bests"]
        r10 = player_data["recents"]
        for c in b30:
            b30_best.push(ChartInfo.from_json_by_lx(c))
        for c in r10:
            r10_best.push(ChartInfo.from_json_by_lx(c))
        return cls(player_data['name'],player_data['rating'],b30_best,r10_best,
                   namePlate=str(player_data['name_plate']['id']),
                   titleColor=player_data['trophy']['color'],
                   titleContent=player_data['trophy']['name'],
                   level=player_data['level'],
                   icon = str(player_data['character']['id'])
                )

        