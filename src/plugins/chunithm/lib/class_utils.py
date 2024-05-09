from .chunithm_music import total_list
from .request_client import generate_best_30_data_by_lx,generate_best_30_data_by_df

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
    def from_json_by_df(cls, data):
        def check_is_ajc(achievement,comboId):
            fc = ['', 'fullcombo', 'alljustice']
            if achievement == 1010000:
                return 3
            else:
                return fc.index(comboId)
            
        fi = check_is_ajc(data['score'],data["fc"])
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
    def __init__(self, user_Name,rating,best_30,recent_10,namePlate="2",icon="0",titleColor="Trophy",titleContent="Chunithm Best 30",level="??"):
        self.userName = user_Name
        self.rating = rating
        self.best_30 = best_30
        self.recent_10 = recent_10
        self.namePlate = namePlate
        self.titleColor = titleColor
        self.titleContent = titleContent
        self.level = level
        self.icon = icon

    def __str__(self) -> str:
        return f"userName:{self.userName}-rating:{self.rating}-namePlate:{self.namePlate}-icon:{self.icon}-{len(self.best_30)}-{len(self.recent_10)}"

    @classmethod  
    async def generate_best_30_data_lx_mode(cls, user_id,friend_code=None):
        status_code, player_data = await generate_best_30_data_by_lx(user_id,friend_code)
        if status_code != 200:
            return status_code,player_data
        b30_best = BestList(30)
        r10_best = BestList(10)
        b30 = player_data["bests"]
        r10 = player_data["recents"]
        for c in b30:
            b30_best.push(ChartInfo.from_json_by_lx(c))
        for c in r10:
            r10_best.push(ChartInfo.from_json_by_lx(c))
        character = player_data.get('character',{})
        if character:
            icon = character.get('id',"0")
        else:
            icon = "0"
        return 200,cls(player_data['name'],player_data['rating'],b30_best,r10_best,
                   namePlate=str(player_data.get('name_plate',{}).get('id',"2")),
                   titleColor=player_data['trophy']['color'],
                   titleContent=player_data['trophy']['name'],
                   level=player_data['level'],
                   icon = str(icon)
                )
    
    @classmethod  
    async def generate_best_30_data_df_mode(cls, params):  
        status_code, player_data = await generate_best_30_data_by_df(params)
        if status_code != 200:
            return status_code,player_data
        b30_best = BestList(30)
        r10_best = BestList(10)
        b30 = player_data["records"]['b30']
        r10 = player_data["records"]['r10']
        for c in b30:
            b30_best.push(ChartInfo.from_json_by_df(c))
        for c in r10:
            r10_best.push(ChartInfo.from_json_by_df(c))
        return 200,cls(player_data['nickname'],player_data['rating'],b30_best,r10_best)
    