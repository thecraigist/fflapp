import csv
import statistics
import fflconstants


class Game:
    def __init__(self, idGame, year, week, playoffs, consolation, toilet,
                 team1, points1, team2, points2, rivalId):
        self.idGame = idGame
        self.year = year
        self.week = week
        self.playoffs = playoffs
        self.consolation = consolation
        self.toilet = toilet

        self.team1 = team1
        self.points1 = points1
        self.team2 = team2
        self.points2 = points2
        self.rival = rivalId

        self.rankPointsScored = -1
        self.rankMarginOfVictory = -1

    def __str__(self):
        if self.playoffs:
            return "{}-{} over {} {}-{} (P)".format(self.idGame, self.team1, self.team2, self.points1, self.points2)
        elif self.consolation:
            if self.toilet:
                return "{}-{} over {} {}-{} (T)".format(self.idGame, self.team1, self.team2, self.points1, self.points2)
            else:
                return "{}-{} over {} {}-{} (C)".format(self.idGame, self.team1, self.team2, self.points1, self.points2)
        else:
            return "{}-{} over {} {}-{}".format(self.idGame, self.team1, self.team2, self.points1, self.points2)

    def __lt__(self, other):
        return self.idGame < other.idGame

    def printOutCsvFormatAsList(self):
        if self.playoffs:
            return [self.idGame, self.year, self.week, 'Y', self.team1, self.points1, self.team2, self.points2, '', self.rival, '']
        elif self.toilet:
            return [self.idGame, self.year, self.week, '', self.team1, self.points1, self.team2, self.points2, 'Y', self.rival, 'Y']
        elif self.consolation:
            return [self.idGame, self.year, self.week, '', self.team1, self.points1, self.team2, self.points2, 'Y', self.rival, '']
        else:
            return [self.idGame, self.year, self.week, '', self.team1, self.points1, self.team2, self.points2, '', self.rival, '']

    def is3rdString(self):
        return self.team2 == fflconstants.TM_ID_3RD_STRING

    def getMOV(self):
        return round(self.points1 - self.points2, 2)

    def getTotalPoints(self):
        return self.points1 + self.points2


def read_game_file():
    maxWkIdThisYear = -1

    thisYearTemp = fflconstants.THIS_YEAR

    games = []
    with open(r'C:\Users\clewi\eclipse-workspace\ttv2\src\com\l5m\ttv2\engine\worker\FFL_GM.csv') as csvFileGm:
        # dictGm = csv.reader(csvFileGm, delimiter=',')
        dictGm = csv.DictReader(csvFileGm)
        for row in dictGm:
            tmpYr = int(row["YR_ID"])
            tmpWk = int(row["WK_ID"])
            if tmpYr == thisYearTemp and tmpWk > maxWkIdThisYear:
                maxWkIdThisYear = tmpWk
            games.append(Game(int(row["GM_ID"]), tmpYr, tmpWk,
                              "Y" == row["PLAY_FLAG"], "Y" == row["CONSOL_FLAG"], "Y" == row["TOILET_FLAG"],
                              int(row["TM_ID_1"]), float(row["PTS_1"]), int(row["TM_ID_2"]), float(row["PTS_2"]),
                              int(row["RIVAL_ID"])))
    fflconstants.initialize_this_week_constant(maxWkIdThisYear)

    return games


def write_game_file(games):
    with open(r'C:\Users\clewi\eclipse-workspace\ttv2\src\com\l5m\ttv2\engine\worker\FFL_GM.csv', mode='w', newline='') as new_game_file:
        game_file_writer = csv.writer(new_game_file, delimiter=',')
        game_file_writer.writerow(['GM_ID', 'YR_ID', 'WK_ID', 'PLAY_FLAG', 'TM_ID_1', 'PTS_1', 'TM_ID_2', 'PTS_2',
                                   'CONSOL_FLAG', 'RIVAL_ID', 'TOILET_FLAG'])
        for game in sorted(games, reverse=True):
            game_file_writer.writerow(game.printOutCsvFormatAsList())


def set_ranks_game(games):
    rankableGames = []
    for game in games:
        # //?if (!game.isPlayoffs & & !game.isConsolation)
        if not game.is3rdString():
            rankableGames.append(game)
    numRankableGames = len(rankableGames)
    # print("numRankableGames={}".format(numRankableGames))

    # Collections.sort(rankableGames, new GameComparator(GameComparator.MARGIN_OF_VICTORY))
    rankableGamesMOV = sorted(rankableGames, key=lambda gm: float(gm.getMOV()), reverse=True)
    for idx, game in enumerate(rankableGamesMOV):
        rankableGamesMOV[idx].rankMarginOfVictory = (numRankableGames - idx)

    # Collections.sort(rankableGames, new GameComparator(GameComparator.POINTS_SCORED))
    rankableGamesPoints = sorted(rankableGames, key=lambda gm: float(gm.getTotalPoints()), reverse=True)
    for idx, game in enumerate(rankableGamesPoints):
        rankableGamesPoints[idx].rankPointsScored = (idx + 1)


class Gamelog:
    def __init__(self, idGame, year, week, playoffs, consolation, toilet,
                 team1, teamName1, teamManager1, teamManagerName1,
                 points1, points2, result, rivalId, team2):
        self.idGame = idGame
        self.year = year
        self.week = week
        self.playoffs = playoffs
        self.consolation = consolation
        self.toilet = toilet

        self.team1 = team1
        self.teamName1 = teamName1
        self.teamManager1 = teamManager1
        self.teamManagerName1 = teamManagerName1

        self.points1 = points1
        self.points2 = points2
        self.result = result
        self.rival = rivalId
        self.team2 = team2

        self.tmScore = -1
        self.rank = -1
        self.rankAgainst = -1

    def __str__(self):
        if self.playoffs:
            return "{} - {} ({}) {}-{} (P)".format(self.idGame, self.teamName1, self.result, self.points1, self.points2)
        elif self.consolation:
            if self.toilet:
                return "{} - {} ({}) {}-{} (T)".format(self.idGame, self.teamName1, self.result, self.points1, self.points2)
            else:
                return "{} - {} ({}) {}-{} (C)".format(self.idGame, self.teamName1, self.result, self.points1, self.points2)
        else:
            return "{} - {} ({}) {}-{}, {}, {}, {}".format(self.idGame, self.teamName1, self.result, self.points1, self.points2, self.tmScore, self.rank, self.rankAgainst)

    def is3rdString(self):
        return self.team1 == fflconstants.TM_ID_3RD_STRING

    def isOpponent3rdString(self):
        return self.team2 == fflconstants.TM_ID_3RD_STRING

    def getPointDifferential(self):
        if "W" == self.result:
            return self.points1 - self.points2
        else:
            return self.points2 - self.points1


def generate_gamelog_list(games, year_to_teams):
    gamelogs = []

    wklyScoreMap = {}
    for game in games:
        yrWk = str(game.year) + "_" + str(game.week)
        if yrWk not in wklyScoreMap:
            wklyScoreMap[yrWk] = [game.points1]
        else:
            wklyScoreMap[yrWk].append(game.points1)
        if not game.is3rdString():
            wklyScoreMap[yrWk].append(game.points2)

        teamBeanWinner = year_to_teams.get(game.year).get(game.team1)
        teamBeanLoser = year_to_teams.get(game.year).get(game.team2)

        gamelogs.append(Gamelog(game.idGame, game.year, game.week, game.playoffs, game.consolation, game.toilet,
                                game.team1, teamBeanWinner.name, teamBeanWinner.manager.idManager, teamBeanWinner.manager.name,
                                game.points1, game.points2, "W", game.rival, game.team2))
        gamelogs.append(Gamelog(game.idGame, game.year, game.week, game.playoffs, game.consolation, game.toilet,
                                game.team2, teamBeanLoser.name, teamBeanLoser.manager.idManager, teamBeanLoser.manager.name,
                                game.points2, game.points1, "L", game.rival, game.team1))

    for yrWkKey in wklyScoreMap.keys():
        wklyScoreMap[yrWkKey] = sorted(wklyScoreMap[yrWkKey])
    for gamelog in gamelogs:
        if gamelog.is3rdString() or gamelog.year == 2007:  # only 8 teams in league
            continue
        elif gamelog.playoffs or gamelog.consolation:
            continue
        tmScore = -1  # Double.MIN_VALUE;
        ptsRank = -1
        ptsAgstRank = -1
        if gamelog.is3rdString():
            continue
        gamelogYrWk = str(gamelog.year) + "_" + str(gamelog.week)
        if gamelogYrWk in wklyScoreMap:  # necessary...?
            scores = wklyScoreMap[gamelogYrWk].copy()
            ptsRank = scores.index(gamelog.points1) + 1
            if gamelog.isOpponent3rdString():
                ptsAgstRank = -1
            else:
                ptsAgstRank = scores.index(gamelog.points2) + 1
            scores.remove(gamelog.points1)

            mean = statistics.mean(scores)
            stdev = statistics.stdev(scores)
            tmScore = (gamelog.points1 - mean) / stdev
        gamelog.tmScore = tmScore
        gamelog.rank = ptsRank
        gamelog.rankAgainst = ptsAgstRank
    # for gamelog in gamelogs:
        # print(gamelog)
    return gamelogs
