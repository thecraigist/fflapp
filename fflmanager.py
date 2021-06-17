import csv
from collections import OrderedDict
import statistics
import fflconstants
from marshmallow import Schema, fields


class ManagerSchema(Schema):
    name = fields.Str()
    age = fields.Int()


class Manager:
    def __init__(self, id_manager, name, active, deadball_only):
        self.idManager = id_manager
        self.name = name
        self.active = active
        self.deadball_only = deadball_only

        self.wins = 0
        self.losses = 0
        self.playoffAppearances = 0
        self.byeWeekFinishes = 0

        self.winsDeadball = 0
        self.lossesDeadball = 0
        self.playoffAppearancesDeadball = 0
        self.byeWeekFinishesDeadball = 0

        self.winsPlayoff = 0
        self.lossesPlayoff = 0

        self.crowns = 0
        self.toilets = 0

        self.bestRecord = None
        self.worstRecord = None

    def __str__(self):
        if self.deadball_only:
            return "{} - {} (Deadball), {}-{}".format(self.idManager, self.name, self.wins, self.losses)
        elif self.active:
            return "{} - {} (Active), {}-{}".format(self.idManager, self.name, self.wins, self.losses)
        else:
            return "{} - {}, {}-{}".format(self.idManager, self.name, self.wins, self.losses)

    def accumulate_team(self, team):
        if team.year < fflconstants.FIRST_YEAR_MODERN_ERA:
            self.winsDeadball += team.wins
            self.winsDeadball += team.winsConsol
            self.lossesDeadball += team.losses
            self.lossesDeadball += team.lossesConsol
            if team.regularSeasonRank < 7:
                self.playoffAppearancesDeadball += 1
                if team.regularSeasonRank < 3:
                    self.byeWeekFinishesDeadball += 1
        else:
            self.wins += team.wins
            self.wins += team.winsConsol
            self.losses += team.losses
            self.losses += team.lossesConsol
            if team.year <= fflconstants.LAST_COMPLETE_YEAR and team.regularSeasonRank < 7:
                self.playoffAppearances += 1
                if team.regularSeasonRank < 3:
                    self.byeWeekFinishes += 1

        self.winsPlayoff += team.winsPlayoff
        self.lossesPlayoff += team.lossesPlayoff
        if team.year <= fflconstants.LAST_COMPLETE_YEAR:
            if team.year < fflconstants.LAST_COMPLETE_YEAR or (team.year == fflconstants.LAST_COMPLETE_YEAR and fflconstants.THIS_WEEK == 16):
                if team.finalRank == 1:
                    self.crowns += 1
                elif team.finalRank == 10 or (team.year == 2006 and team.finalRank == 7):
                    self.toilets += 1

            if self.worstRecord is None and self.bestRecord is None:
                if self.wins >= 7:
                    self.bestRecord = [team.wins, team.losses, team.year]
                else:
                    self.worstRecord = [team.wins, team.losses, team.year]
            elif self.worstRecord is None:
                if self.bestRecord[0] > team.wins:
                    self.worstRecord = [team.wins, team.losses, team.year]
                else:
                    self.worstRecord = [self.bestRecord[0], self.bestRecord[1], self.bestRecord[2]]
                    self.bestRecord = [team.wins, team.losses, team.year]
            elif self.bestRecord is None:
                if self.worstRecord[0] < team.wins:
                    self.bestRecord = [team.wins, team.losses, team.year]
                else:
                    self.bestRecord = [self.worstRecord[0], self.worstRecord[1], self.worstRecord[2]]
                    self.worstRecord = [team.wins, team.losses, team.year]
            else:
                if team.wins >= self.bestRecord[0]:
                    self.bestRecord = [team.wins, team.losses, team.year]
                elif team.wins <= self.worstRecord[0]:
                    self.worstRecord = [team.wins, team.losses, team.year]


def read_manager_file():
    managers = OrderedDict()
    with open(r'C:\Users\clewi\eclipse-workspace\ttv2\src\com\l5m\ttv2\engine\worker\FFL_MGR.csv') as csvFileMgr:
        # dictMgr = csv.reader(csvFileMgr, delimiter=',')
        dictMgr = csv.DictReader(csvFileMgr)
        for row in sorted(dictMgr, key=lambda mgr: int(mgr["MGR_ORDER"])):
            managers.update({int(row["MGR_ID"]): Manager(int(row["MGR_ID"]), row["MGR_NAME"],
                                                         "Y" == row["IS_ACT"], "Y" == row["IS_DEADBALL_ONLY"])})
    return managers


class FranchisesSheet:
    def __init__(self):
        self.franchiseHeader = [[], []]  # new String[2][][]
        self.franchiseMetricsList = []

    def __str__(self):
        return self.franchiseMetricsList.__str__()


def submit_handler_franchises(mgr_map_original, yr_to_tm_map, gamelog_list_original, year_week_list):
    franchisesSheet = FranchisesSheet()

    if True:  # scope
        for i in range(21):
            franchisesSheet.franchiseHeader[0].append([[], [], []])  # = new String[21][3]
        franchisesSheet.franchiseHeader[0][0][0] = "Owner"
        franchisesSheet.franchiseHeader[0][0][1] = "2"
        franchisesSheet.franchiseHeader[0][0][2] = "1"
        franchisesSheet.franchiseHeader[0][1][0] = "Modern Era"
        franchisesSheet.franchiseHeader[0][1][1] = "1"
        franchisesSheet.franchiseHeader[0][1][2] = "5"
        franchisesSheet.franchiseHeader[0][2][0] = "Dead Ball Era"
        franchisesSheet.franchiseHeader[0][2][1] = "1"
        franchisesSheet.franchiseHeader[0][2][2] = "5"
        franchisesSheet.franchiseHeader[0][3][0] = "Overall"
        franchisesSheet.franchiseHeader[0][3][1] = "1"
        franchisesSheet.franchiseHeader[0][3][2] = "5"
        franchisesSheet.franchiseHeader[0][4][0] = "Playoff Record"
        franchisesSheet.franchiseHeader[0][4][1] = "1"
        franchisesSheet.franchiseHeader[0][4][2] = "3"
        franchisesSheet.franchiseHeader[0][5][0] = "Lewis Memorial Crowns"
        franchisesSheet.franchiseHeader[0][5][1] = "2"
        franchisesSheet.franchiseHeader[0][5][2] = "1"
        franchisesSheet.franchiseHeader[0][6][0] = "Toilets"
        franchisesSheet.franchiseHeader[0][6][1] = "2"
        franchisesSheet.franchiseHeader[0][6][2] = "1"
        franchisesSheet.franchiseHeader[0][7][0] = "Best Record (Year)"
        franchisesSheet.franchiseHeader[0][7][1] = "2"
        franchisesSheet.franchiseHeader[0][7][2] = "1"
        franchisesSheet.franchiseHeader[0][8][0] = "Worst Record (Year)"
        franchisesSheet.franchiseHeader[0][8][1] = "2"
        franchisesSheet.franchiseHeader[0][8][2] = "1"
        franchisesSheet.franchiseHeader[0][9][0] = "Average Score"
        franchisesSheet.franchiseHeader[0][9][1] = "2"
        franchisesSheet.franchiseHeader[0][9][2] = "1"
        franchisesSheet.franchiseHeader[0][10][0] = "Median Score"
        franchisesSheet.franchiseHeader[0][10][1] = "2"
        franchisesSheet.franchiseHeader[0][10][2] = "1"
        franchisesSheet.franchiseHeader[0][11][0] = "Max Score"
        franchisesSheet.franchiseHeader[0][11][1] = "2"
        franchisesSheet.franchiseHeader[0][11][2] = "1"
        franchisesSheet.franchiseHeader[0][12][0] = "Min Score"
        franchisesSheet.franchiseHeader[0][12][1] = "2"
        franchisesSheet.franchiseHeader[0][12][2] = "1"
        franchisesSheet.franchiseHeader[0][13][0] = "Score Deviation"
        franchisesSheet.franchiseHeader[0][13][1] = "2"
        franchisesSheet.franchiseHeader[0][13][2] = "1"
        franchisesSheet.franchiseHeader[0][14][0] = "Average Margin of Victory"
        franchisesSheet.franchiseHeader[0][14][1] = "2"
        franchisesSheet.franchiseHeader[0][14][2] = "1"
        franchisesSheet.franchiseHeader[0][15][0] = "Average Margin of Defeat"
        franchisesSheet.franchiseHeader[0][15][1] = "2"
        franchisesSheet.franchiseHeader[0][15][2] = "1"
        franchisesSheet.franchiseHeader[0][16][0] = "200+ Points Percentage"
        franchisesSheet.franchiseHeader[0][16][1] = "2"
        franchisesSheet.franchiseHeader[0][16][2] = "1"
        franchisesSheet.franchiseHeader[0][17][0] = "Blowout of Week"
        franchisesSheet.franchiseHeader[0][17][1] = "1"
        franchisesSheet.franchiseHeader[0][17][2] = "2"
        franchisesSheet.franchiseHeader[0][18][0] = "High Score of Week"
        franchisesSheet.franchiseHeader[0][18][1] = "1"
        franchisesSheet.franchiseHeader[0][18][2] = "2"
        franchisesSheet.franchiseHeader[0][19][0] = "Low Score of Week"
        franchisesSheet.franchiseHeader[0][19][1] = "1"
        franchisesSheet.franchiseHeader[0][19][2] = "2"
        franchisesSheet.franchiseHeader[0][20][0] = "Standings..."
        franchisesSheet.franchiseHeader[0][20][1] = "1"
        franchisesSheet.franchiseHeader[0][20][2] = "4"
        for i in range(41):
            franchisesSheet.franchiseHeader[1].append([[], [], []])  # = new String[41][1]
        franchisesSheet.franchiseHeader[1][0][0] = ""
        franchisesSheet.franchiseHeader[1][1][0] = "Wins"
        franchisesSheet.franchiseHeader[1][2][0] = "Losses"
        franchisesSheet.franchiseHeader[1][3][0] = "Pct (%)"
        franchisesSheet.franchiseHeader[1][4][0] = "Bye Week Finishes"
        franchisesSheet.franchiseHeader[1][5][0] = "Playoff Appearances"
        franchisesSheet.franchiseHeader[1][6][0] = "Wins"
        franchisesSheet.franchiseHeader[1][7][0] = "Losses"
        franchisesSheet.franchiseHeader[1][8][0] = "Pct (%)"
        franchisesSheet.franchiseHeader[1][9][0] = "Bye Week Finishes"
        franchisesSheet.franchiseHeader[1][10][0] = "Playoff Appearances"
        franchisesSheet.franchiseHeader[1][11][0] = "Wins"
        franchisesSheet.franchiseHeader[1][12][0] = "Losses"
        franchisesSheet.franchiseHeader[1][13][0] = "Pct (%)"
        franchisesSheet.franchiseHeader[1][14][0] = "Bye Week Finishes"
        franchisesSheet.franchiseHeader[1][15][0] = "Playoff Appearances"
        franchisesSheet.franchiseHeader[1][16][0] = "Wins"
        franchisesSheet.franchiseHeader[1][17][0] = "Losses"
        franchisesSheet.franchiseHeader[1][18][0] = "Pct (%)"
        franchisesSheet.franchiseHeader[1][19][0] = ""
        franchisesSheet.franchiseHeader[1][20][0] = ""
        franchisesSheet.franchiseHeader[1][21][0] = ""
        franchisesSheet.franchiseHeader[1][22][0] = ""
        franchisesSheet.franchiseHeader[1][23][0] = ""
        franchisesSheet.franchiseHeader[1][24][0] = ""
        franchisesSheet.franchiseHeader[1][25][0] = ""
        franchisesSheet.franchiseHeader[1][26][0] = ""
        franchisesSheet.franchiseHeader[1][27][0] = ""
        franchisesSheet.franchiseHeader[1][28][0] = ""
        franchisesSheet.franchiseHeader[1][29][0] = ""
        franchisesSheet.franchiseHeader[1][30][0] = ""
        franchisesSheet.franchiseHeader[1][31][0] = "Victor"
        franchisesSheet.franchiseHeader[1][32][0] = "Loser"
        franchisesSheet.franchiseHeader[1][33][0] = "For"
        franchisesSheet.franchiseHeader[1][34][0] = "Against"
        franchisesSheet.franchiseHeader[1][35][0] = "For"
        franchisesSheet.franchiseHeader[1][36][0] = "Against"
        franchisesSheet.franchiseHeader[1][37][0] = "Weeks in 1st"
        franchisesSheet.franchiseHeader[1][38][0] = "Weeks in Last"
        franchisesSheet.franchiseHeader[1][39][0] = "Most Common Place"
        franchisesSheet.franchiseHeader[1][40][0] = "Average Place"

    for manager in mgr_map_original.values():
        array = []  # new String[41]
        for i in range(41):
            array.append("")
        array[0] = manager.name
        array[31] = '0'
        array[32] = '0'
        array[33] = '0'
        array[34] = '0'
        array[35] = '0'
        array[36] = '0'
        franchisesSheet.franchiseMetricsList.append(array)

    if True:  # // Basic win/loss stats
        for idx, manager in enumerate(mgr_map_original.values()):
            array = franchisesSheet.franchiseMetricsList[idx]
            if (manager.wins + manager.losses) > 0:
                array[1] = str(manager.wins)
                array[2] = str(manager.losses)
                # array[3] = round(manager.wins / (manager.wins + manager.losses), 3)
                array[3] = "{}%".format(round(manager.wins / (manager.wins + manager.losses) * 100, 1))
                array[4] = str(manager.byeWeekFinishes) if manager.byeWeekFinishes > 0 else ""
                array[5] = str(manager.playoffAppearances) if manager.playoffAppearances > 0 else ""
            if (manager.winsDeadball + manager.lossesDeadball) > 0:
                array[6] = str(manager.winsDeadball)
                array[7] = str(manager.lossesDeadball)
                # array[8] = round(manager.winsDeadball / (manager.winsDeadball + manager.lossesDeadball), 3)
                array[8] = "{}%".format(round(manager.winsDeadball / (manager.winsDeadball + manager.lossesDeadball) * 100, 1))
                array[9] = str(manager.byeWeekFinishesDeadball) if manager.byeWeekFinishesDeadball > 0 else ""
                array[10] = str(manager.playoffAppearancesDeadball) if manager.playoffAppearancesDeadball > 0 else ""
            array[11] = str(manager.wins + manager.winsDeadball)
            array[12] = str(manager.losses + manager.lossesDeadball)
            # array[13] = round((manager.wins + manager.winsDeadball) / (manager.wins + manager.losses + manager.winsDeadball + manager.lossesDeadball), 3)
            array[13] = "{}%".format(round((manager.wins + manager.winsDeadball) / (manager.wins + manager.losses + manager.winsDeadball + manager.lossesDeadball) * 100, 1))
            array[14] = str(manager.byeWeekFinishes + manager.byeWeekFinishesDeadball) if (manager.byeWeekFinishes + manager.byeWeekFinishesDeadball > 0) else ""
            array[15] = str(manager.playoffAppearances + manager.playoffAppearancesDeadball) if (manager.playoffAppearances + manager.playoffAppearancesDeadball > 0) else ""
            if (manager.winsPlayoff + manager.lossesPlayoff) > 0:
                array[16] = str(manager.winsPlayoff)
                array[17] = str(manager.lossesPlayoff)
                # array[18] = round(manager.winsPlayoff / (manager.winsPlayoff + manager.lossesPlayoff), 3)
                array[18] = "{}%".format(round(manager.winsPlayoff / (manager.winsPlayoff + manager.lossesPlayoff) * 100, 1))
            array[19] = str(manager.crowns) if manager.crowns > 0 else ""
            array[20] = str(manager.toilets) if manager.toilets > 0 else ""
            if manager.bestRecord is None:
                array[21] = ""
            else:
                prefix = ''  # fflconstants.generatePrefix(manager.bestRecord[2] == 2006, manager.bestRecord[2] == 2007)
                postfix = ''  # fflconstants.generatePostfix(manager.bestRecord[2] == 2006, manager.bestRecord[2] == 2007)
                array[21] = "{}-{} ({}{}{})".format(manager.bestRecord[0], manager.bestRecord[1], prefix, manager.bestRecord[2], postfix)
            if manager.worstRecord is None:
                array[22] = ""
            else:
                prefix = ''  # fflconstants.generatePrefix(manager.worstRecord[2] == 2006, manager.worstRecord[2] == 2007)
                postfix = ''  # fflconstants.generatePostfix(manager.worstRecord[2] == 2006, manager.worstRecord[2] == 2007)
                array[22] = "{}-{} ({}{}{})".format(manager.worstRecord[0], manager.worstRecord[1], prefix, manager.worstRecord[2], postfix)
    if True:  # // Count on places
        mgrMap = {}  # new HashMap<String, int[]>()
        if True:  # scope
            mgrToCumeInfoMap = {}
            gamelogList = sorted(gamelog_list_original, key=lambda gm: [gm.year, gm.week, gm.teamManager1])
            currYr = -1
            currWk = -1
            for gamelog in gamelogList:
                if gamelog.playoffs or gamelog.consolation or gamelog.is3rdString():
                    continue
                if (currYr < 0) or (currYr != gamelog.year):
                    if mgrToCumeInfoMap:  # ??
                        tmpList = mgrToCumeInfoMap.values()
                        tmpList = sorted(tmpList, key=lambda item: [item[1], item[2]], reverse=True)
                        for place in range(len(tmpList)):
                            tmpArray = tmpList[place]
                            mgrName = tmpArray[0]
                            if mgrName not in mgrMap:
                                mgrMap[mgrName] = []
                            if currYr == 2006 and place == 6:  # only 7 teams in league this year
                                mgrMap[mgrName][9] = mgrMap[mgrName][9] + 1
                            else:
                                mgrMap[mgrName][place] = mgrMap[mgrName][place] + 1
                        mgrToCumeInfoMap.clear()
                    currYr = gamelog.year
                    currWk = -1
                if currWk < 0:
                    currWk = gamelog.week
                elif currWk != gamelog.week:
                    tmpList = mgrToCumeInfoMap.values()
                    tmpList = sorted(tmpList, key=lambda item: [item[1], item[2]], reverse=True)
                    for place in range(len(tmpList)):
                        tmpArray = tmpList[place]
                        mgrName = tmpArray[0]
                        if mgrName not in mgrMap:
                            mgrMap[mgrName] = []
                            for p in range(10):
                                mgrMap[mgrName].append(0)
                        if currYr == 2006 and place == 6:  # only 7 teams in league this year
                            mgrMap[mgrName][9] += 1
                        else:
                            mgrMap[mgrName][place] += 1
                    currWk = gamelog.week

                if gamelog.teamManagerName1 not in mgrToCumeInfoMap:
                    mgrToCumeInfoMap[gamelog.teamManagerName1] = [gamelog.teamManagerName1, 0, 0]  # new Object[3]
                if "W" == gamelog.result:
                    mgrToCumeInfoMap[gamelog.teamManagerName1][1] += 1
                mgrToCumeInfoMap[gamelog.teamManagerName1][2] += gamelog.points1
            if True:  # // process last week
                if currWk > 0:
                    tmpList = mgrToCumeInfoMap.values()
                    tmpList = sorted(tmpList, key=lambda item: [item[1], item[2]], reverse=True)
                    for place in range(len(tmpList)):
                        tmpArray = tmpList[place]
                        mgrName = tmpArray[0]
                        if mgrName not in mgrMap:
                            mgrMap[mgrName] = []
                        if currYr == 2006 and place == 6:  # only 7 teams in league this year
                            mgrMap[mgrName][9] = mgrMap[mgrName][9] + 1
                        else:
                            mgrMap[mgrName][place] = mgrMap[mgrName][place] + 1

        for idx, manager in enumerate(mgr_map_original.values()):
            if manager.name in mgrMap:  # needed?
                array = franchisesSheet.franchiseMetricsList[idx]
                array[37] = str(mgrMap[manager.name][0])
                array[38] = str(mgrMap[manager.name][9])
                cume = 0
                ctr = 0
                mode = [0, 0]  # new int[2]
                for x in range(10):
                    if mgrMap[manager.name][x] > mode[0]:
                        mode[0] = mgrMap[manager.name][x]
                        mode[1] = x
                    cume += mgrMap[manager.name][x] * x
                    ctr += mgrMap[manager.name][x]
                array[39] = str(mode[1] + 1)
                array[40] = round((cume / ctr) + 1, 2)
    if True:  # // mean / median / dev, margin of victory / loss, and 200 % stats
        for idx, manager in enumerate(mgr_map_original.values()):
            ptsList = []
            movList = []
            molList = []
            ctr200Pts = 0
            for gamelog in gamelog_list_original:
                if gamelog.teamManager1 != manager.idManager:
                    continue
                ptsList.append(gamelog.points1)
                if gamelog.points1 >= 200:
                    ctr200Pts += 1
                if "W" == gamelog.result:
                    movList.append(gamelog.getPointDifferential())
                else:
                    molList.append(gamelog.getPointDifferential())
            ptsList = sorted(ptsList)

            array = franchisesSheet.franchiseMetricsList[idx]
            array[23] = round(statistics.mean(ptsList), 2)
            array[24] = round(statistics.median(ptsList), 2)
            array[25] = round(ptsList[len(ptsList) - 1], 2)
            array[26] = round(ptsList[0], 2)
            array[27] = round(statistics.stdev(ptsList), 2)
            array[28] = round(statistics.mean(movList), 2) if movList else 0
            array[29] = round(statistics.mean(molList), 2) if molList else 0
            array[30] = "{}%".format(round(ctr200Pts / len(ptsList) * 100, 1))
    if True:  # // blowoutOfWeek, highScoreOfWeek, and lowScoreOfWeek stats
        weeklyMap = {}
        for idx, manager in enumerate(mgr_map_original.values()):
            weeklyMap[manager.idManager] = [0, 0, 0, 0, 0, 0]
        for yrWkBean in year_week_list:
            # // blowout
            mgrBeanBlowoutWinner = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.blowoutOfWeekTmIdWinner).manager
            weeklyMap[mgrBeanBlowoutWinner.idManager][0] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanBlowoutWinner.order - 1][31] += 1
            mgrBeanBlowoutLoser = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.blowoutOfWeekTmIdLoser).manager
            weeklyMap[mgrBeanBlowoutLoser.idManager][1] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanBlowoutLoser.order - 1][32] += 1

            # // high score
            mgrBeanHighScore = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.highScoreTmId).manager
            weeklyMap[mgrBeanHighScore.idManager][2] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanHighScore.order - 1][33] += 1
            mgrBeanHighScoreAgainst = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.highScoreTmIdLoser).manager if yrWkBean.highScoreTmIdLoser >= 0 else yr_to_tm_map.get(yrWkBean.year).get(fflconstants.TM_ID_3RD_STRING).manager
            weeklyMap[mgrBeanHighScoreAgainst.idManager][3] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanHighScoreAgainst.order - 1][34] += 1

            # // low score
            mgrBeanLowScore = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.lowScoreTmId).manager
            weeklyMap[mgrBeanLowScore.idManager][4] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanLowScore.order - 1][35] += 1
            mgrBeanLowScoreAgainst = yr_to_tm_map.get(yrWkBean.year).get(yrWkBean.lowScoreTmIdWinner).manager if yrWkBean.lowScoreTmIdWinner >= 0 else yr_to_tm_map.get(yrWkBean.year).get(fflconstants.TM_ID_3RD_STRING).manager
            weeklyMap[mgrBeanLowScoreAgainst.idManager][5] += 1
            # franchisesSheet.franchiseMetricsList[mgrBeanLowScoreAgainst.order - 1][36] += 1
        for idx, manager in enumerate(mgr_map_original.values()):
            array = franchisesSheet.franchiseMetricsList[idx]
            array[31] = str(weeklyMap[manager.idManager][0])
            array[32] = str(weeklyMap[manager.idManager][1])
            array[33] = str(weeklyMap[manager.idManager][2])
            array[34] = str(weeklyMap[manager.idManager][3])
            array[35] = str(weeklyMap[manager.idManager][4])
            array[36] = str(weeklyMap[manager.idManager][5])

    return franchisesSheet
