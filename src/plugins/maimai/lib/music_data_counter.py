from decimal import Decimal, ROUND_DOWN

class MusicDataCounter():
    fc_enum = ['', 'fc', 'fcp', 'ap', 'app']
    fs_enum = ['', 'fs', 'fsp', 'fsd', 'fsdp','sync']

    def __str__(self) -> str:
        print(self.__dict__)
        return "yes"
        # return self.__dict__
    
    def __init__(self) -> None:
        self.total = 0

        self.is_played_count = 0
        self.total_achievements = 0

        self.sssp = 0
        self.sss = 0
        self.ssp = 0
        self.ss = 0
        self.sp = 0
        self.s = 0
        self.clear = 0

        self.app = 0
        self.ap = 0
        self.fcp = 0
        self.fc = 0

        self.fdxp = 0
        self.fdx = 0
        self.fsp = 0
        self.fs = 0
        self.sync = 0

        self.star_0 = 0
        self.star_1 = 0
        self.star_2 = 0
        self.star_3 = 0
        self.star_4 = 0
        self.star_5 = 0

    def _get_dxscore_type(self,dxscorepen):
        if dxscorepen <= 85:
            return 0
        elif dxscorepen <= 90:
            return 1
        elif dxscorepen <= 93:
            return 2
        elif dxscorepen <= 95:
            return 3     
        elif dxscorepen <= 97:
            return 4     
        else:
            return 5

    def append_music(self,music_score,is_played:bool = True):
        self.total += 1

        if is_played:
            self.is_played_count += 1
            self.total_achievements += music_score['achievements']
            if music_score['achievements'] >= 100.5:
                self.sssp += 1
            if music_score['achievements'] >= 100:
                self.sss += 1
            if music_score['achievements'] >= 99.5:
                self.ssp += 1
            if music_score['achievements'] >= 99:
                self.ss += 1
            if music_score['achievements'] >= 98:
                self.sp += 1
            if music_score['achievements'] >= 97:
                self.s += 1
            if music_score['achievements'] >= 80:
                self.clear += 1

            if self.fc_enum.index(music_score['fc']) >= 4:
                self.app += 1
            if self.fc_enum.index(music_score['fc']) >= 3:
                self.ap += 1
            if self.fc_enum.index(music_score['fc']) >= 2:
                self.fcp += 1
            if self.fc_enum.index(music_score['fc']) >= 1:
                self.fc += 1
            if self.fs_enum.index(music_score['fs']) == 5:
                self.sync += 1
            if self.fs_enum.index(music_score['fs']) == 4:
                self.fdxp += 1
            if self.fs_enum.index(music_score['fs']) in [3,4]:
                self.fdx += 1
            if self.fs_enum.index(music_score['fs']) in [2,3,4]:
                self.fsp += 1
            if self.fs_enum.index(music_score['fs']) in [1,2,3,4]:
                self.fs += 1

            # start_mun = music_score['dxScore'] / (sum(total_list.by_id(str(music_score['song_id'])).charts[music_score['level_index']]['notes'])*3) *100
            # star_index = self._get_dxscore_type(start_mun)
            # if star_index == 0:
            #     self.star_0 += 1
            # if star_index >= 1:
            #     self.star_1 += 1
            # if star_index >= 2:
            #     self.star_2 += 1
            # if star_index >= 3:
            #     self.star_3 += 1
            # if star_index >= 4:
            #     self.star_4 += 1
            # if star_index >= 5:
            #     self.star_5 += 1


    def get_rank_result(self):
        return [self.sssp,self.sss,self.ss,self.s]
    
    def get_fc_result(self):
        return [self.fc,self.fcp,self.ap,self.app]
    
    def get_fs_result(self):
        return [self.fs,self.fsp,self.fdx,self.fdxp]
    
    def get_star_result(self):
        return [self.star_5,self.star_4,self.star_3,self.star_1]
    

    def get_achievements_adv(self):
        result = Decimal(self.total_achievements) / Decimal(self.is_played_count)
        return result.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)