import csv
import statistics
import fflconstants


class Team:
    def __init__(self, id_team, name, year, manager, team_score, regular_season_rank, final_rank):
        self.idTeam = id_team
        self.name = name
        self.year = year
        self.manager = manager

        self.teamScore = team_score
        self.regularSeasonRank = regular_season_rank
        self.finalRank = final_rank

        self.wins = 0
        self.losses = 0
        self.pointsFor = 0
        self.pointsAgainst = 0
        self.winsPlayoff = 0
        self.lossesPlayoff = 0
        self.winsConsol = 0
        self.lossesConsol = 0

        self.maxScore = -1
        self.minScore = -1

        self.weeklyTmScoreCume = 0
        self.weeklyPointsForRankCume = 0
        self.weeklyPointsAgainstRankCume = 0

        self.rankWeeklyTmScore = -1
        self.rankSeasonTmScore = -1

    def __str__(self):
        return "{} {} ({}), {}-{}({}) {}".format(self.year, self.name, self.manager.name, self.wins, self.losses,
                                                 self.pointsFor, self.teamScore)

    def __lt__(self, other):
        return self.name < other.name

    def printOutCsvFormat(self):
        if self.finalRank > 0:
            return "{},{},{},{},{},{},{}".format(self.idTeam, self.name, self.year, self.manager.idManager,
                                                 self.teamScore, self.finalRank, self.regularSeasonRank)
        else:
            return "{},{},{},{},{},{},{}".format(self.idTeam, self.name, self.year, self.manager.idManager,
                                                 self.teamScore, '', self.regularSeasonRank)

    def printOutCsvFormatAsList(self):
        if self.finalRank > 0:
            return [self.idTeam, self.name, self.year, self.manager.idManager, self.teamScore, self.finalRank,
                    self.regularSeasonRank]
        else:
            return [self.idTeam, self.name, self.year, self.manager.idManager, self.teamScore, '',
                    self.regularSeasonRank]

    def accumulateGame(self, is_win, is_playoffs, is_consolation, pts, pts_opponent):
        if is_playoffs:
            if is_win:
                self.winsPlayoff += 1
            else:
                self.lossesPlayoff += 1
        elif is_consolation:
            if is_win:
                self.winsConsol += 1
            else:
                self.lossesConsol += 1
        else:
            if is_win:
                self.wins += 1
            else:
                self.losses += 1
            self.pointsFor = round(self.pointsFor + pts, 2)
            self.pointsAgainst = round(self.pointsAgainst + pts_opponent, 2)

        if self.maxScore < 0 or self.maxScore < pts:
            self.maxScore = pts
        if self.minScore < 0 or self.minScore > pts:
            self.minScore = pts

    def is3rdString(self):
        return self.idTeam == fflconstants.TM_ID_3RD_STRING

    def getNumGames(self):
        return self.wins + self.losses

    def getPointsForAvg(self):
        numGames = self.getNumGames()
        if numGames > 0:
            return self.pointsFor / numGames
        else:
            return 0

    def getPointsAgainstAvg(self):
        numGames = self.getNumGames()
        if numGames > 0:
            return self.pointsAgainst / numGames
        else:
            return 0

    def getAvgWeeklyTmScore(self):
        return self.weeklyTmScoreCume / self.getNumGames()

    def getAvgWeeklyPointsForRank(self):
        return self.weeklyPointsForRankCume / self.getNumGames()

    def getAvgWeeklyPointsAgainstRank(self):
        return self.weeklyPointsAgainstRankCume / self.getNumGames()


def read_team_file(managers, games) -> object:
    teams = {}
    for year in range(fflconstants.FIRST_YEAR, fflconstants.THIS_YEAR + 1):
        teams[year] = {}
    with open(r'C:\Users\clewi\eclipse-workspace\ttv2\src\com\l5m\ttv2\engine\worker\FFL_TM.csv') as csvFileTm:
        # dictTm = csv.reader(csvFileTm, delimiter=',')
        dictTm = csv.DictReader(csvFileTm)
        for row in dictTm:
            year = int(row["YR_ID"])
            if year <= fflconstants.LAST_COMPLETE_YEAR:
                teams[year].update({int(row["TM_ID"]): Team(int(row["TM_ID"]), row["TM_NAME"], int(row["YR_ID"]),
                                                            managers.get(int(row["MGR_ID"])), float(row["TM_SCORE"]),
                                                            int(row["REG_SEA_RK"]), int(row["FINAL_RK"]))})
            else:
                teams[year].update({int(row["TM_ID"]): Team(int(row["TM_ID"]), row["TM_NAME"], int(row["YR_ID"]),
                                                            managers.get(int(row["MGR_ID"])), float(row["TM_SCORE"]),
                                                            int(row["REG_SEA_RK"]), -1)})

    # accumulate each game into each team
    for game in games:
        winningTeam = teams.get(game.year).get(game.team1)
        losingTeam = teams.get(game.year).get(game.team2)
        winningTeam.accumulateGame(True, game.playoffs, game.consolation, game.points1, game.points2)
        losingTeam.accumulateGame(False, game.playoffs, game.consolation, game.points2, game.points1)

    # accumulate each team into manager
    for year in teams.keys():
        for team in teams.get(year).values():
            team.manager.accumulate_team(team)
    return teams


def create_tm_scores_handler(year_to_teams, selected_year_id, is_generate_new_file=False):
    teams = year_to_teams.get(selected_year_id).values()

    totalTmScores = []
    for team in teams:
        if not team.is3rdString():
            totalTmScores.append(team.pointsFor)

    for team in teams:
        # print(team)
        scores = totalTmScores.copy()
        scores.remove(team.pointsFor)

        mean = statistics.mean(scores)
        stdev = statistics.stdev(scores)
        team.teamScore = (team.pointsFor - mean) / stdev

        # Just informational printout
        if is_generate_new_file:
            print(team.printOutCsvFormat())
        else:
            print("{}   {}".format(team.name, team.teamScore))

    if is_generate_new_file:
        write_team_file(year_to_teams)


def write_team_file(yrToTmMap):
    with open(r'C:\Users\clewi\eclipse-workspace\ttv2\src\com\l5m\ttv2\engine\worker\FFL_TM.csv', mode='w', newline='') as new_team_file:
        team_file_writer = csv.writer(new_team_file, delimiter=',')
        team_file_writer.writerow(['TM_ID', 'TM_NAME', 'YR_ID', 'MGR_ID', 'TM_SCORE', 'FINAL_RK', 'REG_SEA_RK'])
        for year in sorted(yrToTmMap.keys(), reverse=True):
            for team in yrToTmMap.get(year).values():
                team_file_writer.writerow(team.printOutCsvFormatAsList())


def __set_ranks(teams, gamelogs):
    tmIdToTmScoreMap = {}
    tmIdToPointsForRankMap = {}
    tmIdToPointsAgainstRankMap = {}
    for gamelog in gamelogs:
        if gamelog.playoffs or gamelog.consolation:
            continue
        mapKey = "{}_{}".format(gamelog.year, gamelog.team1)
        # TODO ?if mapKey not in tmIdToTmScoreMap.keys()?
        if mapKey not in tmIdToTmScoreMap:
            tmIdToTmScoreMap[mapKey] = []
            tmIdToPointsForRankMap[mapKey] = []
            tmIdToPointsAgainstRankMap[mapKey] = []
        tmIdToTmScoreMap[mapKey].append(gamelog.tmScore)
        tmIdToPointsForRankMap[mapKey].append(gamelog.rank)
        tmIdToPointsAgainstRankMap[mapKey].append(gamelog.rankAgainst)

    rankableTeams = []
    for team in teams:
        if not team.is3rdString():  # just in case
            mapKey = "{}_{}".format(team.year, team.idTeam)
            for wklyTmScore in tmIdToTmScoreMap[mapKey]:
                team.weeklyTmScoreCume += wklyTmScore
            for pointsForRank in tmIdToPointsForRankMap[mapKey]:
                team.weeklyPointsForRankCume += pointsForRank
            for pointsAgainstRank in tmIdToPointsAgainstRankMap[mapKey]:
                team.weeklyPointsAgainstRankCume += pointsAgainstRank
            if team.year <= fflconstants.LAST_COMPLETE_YEAR:
                rankableTeams.append(team)

    # Collections.sort(rankableTeams, new TeamComparator(TeamComparator.WEEKLY_AVG_TM_SCORE))
    rankableTeamsWklyTmScore = sorted(rankableTeams, key=lambda tm: tm.getAvgWeeklyTmScore(), reverse=True)
    for idx, team in enumerate(rankableTeamsWklyTmScore):
        team.rankWeeklyTmScore = (idx + 1)

    # Collections.sort(rankableTeams, new TeamComparator(TeamComparator.SEASON_TM_SCORE))
    rankableTeamsTmScore = sorted(rankableTeams, key=lambda tm: tm.teamScore, reverse=True)
    for idx, team in enumerate(rankableTeamsTmScore):
        team.rankSeasonTmScore = (idx + 1)


class TeamRanksSheet:
    def __init__(self):
        self.teamRankList = []  # new ArrayList<String[]>()

    def __str__(self):
        return self.teamRankList.__str__()


def submit_handler_team_ranks(year_to_teams, gamelogs_original):
    teamRanksSheet = TeamRanksSheet()

    tmListComplete = fflconstants.flatten_team_dict_into_list(year_to_teams)
    __set_ranks(tmListComplete, gamelogs_original)

    tmList = []  # new ArrayList<TeamBean>()
    for team in tmListComplete:
        if (not team.is3rdString()) and team.year <= fflconstants.LAST_COMPLETE_YEAR:
            tmList.append(team)
    numTeams = len(tmList)

    # team season scores
    notesMap = {
        "Craig Lewis2011": "Perfect Score; On average was over 1.6 times better than league norm each week and almost 4 times better over whole season",
        "Carl Slabicki2009": "5th best season score, but Carl doesn't know how to win championships",
        "Craig Lewis2014": "Most disappointing team of all time? - 7th in weekly, 2nd in season, yet 4th place finish",
        "Tom Wargacki2008": "Most disappointing team of all time? - 3rd in weekly, 7th in season, yet 6th place finish",
        "Eddie Schultz2016": "Best team to not win championship; Most disappointing team of all time? - 2nd in weekly, 4th in season, yet lost in Championship",
        "Billy Flynn2013": "Best team of 2013 (**cough**choker**cough**)", "Tom Wargacki2013": "Just knows how to win",
        "Mark Bennett2010": "2nd best non-playoff team of all time (and better than Bennett's team from 2008 that won it all)",
        "Mark Bennett2019": "Best non-playoff team of all time",
        "Mark Bennett2008": "Worst championship team of all time - league average weekly and season scores and 4th highest team score for that season",
        "Carl Slabicki2008": "Luckiest team of all time", "Billy Flynn2009": "Worst 9 win team in history",
        "Art Kheyman2016": "Worst Modern Championship team of all time",
        "Tom Wargacki2017": "Worst Championship game participant of all-time",
        "Mark Bennett2012": "Best Toilet winner of all time",
        "Mark Bennett2017": "Most disappointing team of all time? - 4th in weekly, 3rd in season, yet 6th place finish",
        "Zach Rose2017": "Worst Modern team of all time",
        "Tarik Ammour2006": "Actually finished last, but only 7 teams in league this year; Lowest score possible"}

    teamRankListSpecial = []  # new ArrayList<String[]>()
    for team in tmList:
        # int idx = 0
        array = []  # new String[13]
        for i in range(13):
            array.append("")
        array[0] = team.manager.name
        array[1] = team.name
        array[2] = str(team.year)
        array[3] = round(team.getAvgWeeklyTmScore(), 3)
        array[4] = str(round(team.rankWeeklyTmScore, 0))
        array[5] = round(team.teamScore, 3)
        array[6] = str(round(team.rankSeasonTmScore, 0))
        array[7] = round(team.maxScore, 2)
        array[8] = round(team.minScore, 2)
        array[9] = str(team.regularSeasonRank)
        array[10] = str(team.finalRank)

        scoreTmScoreWeekly = (10 - ((team.rankWeeklyTmScore - 1) * (10 / (numTeams - 1))))
        scoreTmScoreSeason = (10 - ((team.rankSeasonTmScore - 1) * (10 / (numTeams - 1))))
        scoreStandings = (3 - ((team.finalRank - 1) * (3 / 6))) if team.finalRank <= 6 else (7 - team.finalRank)
        totalTmScore = scoreTmScoreWeekly + scoreTmScoreSeason + scoreStandings
        array[11] = round(totalTmScore, 3)
        noteMapKey = "{}{}".format(team.manager.name, team.year)
        array[12] = notesMap[noteMapKey] if noteMapKey in notesMap else ""
        if team.year == 2006 and "Tarik Ammour" == team.manager.name:
            array[11] = round(-3, 3)
            teamRankListSpecial.append(array)
        else:
            teamRanksSheet.teamRankList.append(array)

    teamRanksSheet.teamRankList = sorted(teamRanksSheet.teamRankList, key=lambda tm: [tm[11], tm[2]], reverse=True)
    for team in teamRankListSpecial:
        teamRanksSheet.teamRankList.append(team)
    if True:  # scope
        array = []  # new String[13]
        for i in range(13):
            array.append("")
        array[0] = "Manager Name"
        array[1] = "Team Name"
        array[2] = "Year"
        array[3] = "Average Weekly Team Score"
        array[4] = "Weekly Rank"
        array[5] = "Season Team Score"
        array[6] = "Season Rank"
        array[7] = "High Score"
        array[8] = "Low Score"
        array[9] = "Reg Season Finish"
        array[10] = "Final Place"
        array[11] = "Total Team Score"
        array[12] = "Notes"
        teamRanksSheet.teamRankList.insert(0, array)

    return teamRanksSheet
