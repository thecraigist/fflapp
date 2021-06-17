from yahoo_oauth import OAuth2
import xml.etree.ElementTree as elementtree
import re
import fflconstants
import fflgame
import fflteam

# TODO figure out how to commit fflapp to git (benchmark)
# TODO find key for 2021 season, update url/etc and test 2021_01 loading
# ??? https://football.fantasysports.yahoo.com/f1/65334
# 399 https://football.fantasysports.yahoo.com/2020/f1/14226
# 390 https://football.fantasysports.yahoo.com/2019/f1/196720
# 380 https://football.fantasysports.yahoo.com/2018/f1/787604
# 371 https://football.fantasysports.yahoo.com/2017/f1/6337
# App ID 5Dyon09L (billyboy)
# Client ID (Consumer Key)
#       dj0yJmk9R091eGVRQ2FDS01NJmQ9WVdrOU5VUjViMjR3T1V3bWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWJl
# Client Secret (Consumer Secret) f9237f29eec4f94884557854a34ebdfa5c070a84

# urlGame = "https://fantasysports.yahooapis.com/fantasy/v2/game/nfl;season=2019"
# league/settings ... league/scoreboard;week=2 ...
# https://fantasysports.yahooapis.com/fantasy/v2/team/223.l.431.t.1/matchups;weeks=1,5
# https://fantasysports.yahooapis.com/fantasy/v2/team/223.l.431.t.1/stats;type=season
# https://fantasysports.yahooapis.com/fantasy/v2/team/253.l.102614.t.10/roster/players
# https://fantasysports.yahooapis.com/fantasy/v2/team/253.l.102614.t.10/roster;week=10
# urlLeague = "https://fantasysports.yahooapis.com/fantasy/v2/league/" + league_key
# urlStandings = "https://fantasysports.yahooapis.com/fantasy/v2/league/"+league_key+"/standings"
# urlScoreboard = "https://fantasysports.yahooapis.com/fantasy/v2/league/" + league_key + "/scoreboard"

league_key = "399.l.14226"
team_key_danmarinos = "399.l.14226.t.5"


def _generate_connection():
    oauth: OAuth2 = OAuth2(None, None, from_file='json/private2.json')
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    return oauth


# leave managers as parameter in case needed later
def yahoo_api_loadweek(managers, games, teams_map, is_generate_new_file=True):
    oauth = _generate_connection()

    urlScoreboard = "https://fantasysports.yahooapis.com/fantasy/v2/league/" + league_key + "/scoreboard"
    responseScoreboard = oauth.session.get(urlScoreboard)

    xml = re.sub(' xmlns="[^"]+"', '', responseScoreboard.text, count=1)
    root = elementtree.fromstring(xml)

    yrId = fflconstants.THIS_YEAR
    wkId = int(root.find('./league/scoreboard/week').text)  # fflconstants.THIS_WEEK
    is_reload = True if wkId == fflconstants.THIS_WEEK else False
    if not is_reload:
        fflconstants.THIS_WEEK = wkId

    # TODO how to determine championship game and toilet bowl?  Any better way?
    team_keys_toilet = []
    team_keys_playoffs = []
    if wkId >= 15:
        urlStandings = "https://fantasysports.yahooapis.com/fantasy/v2/league/" + league_key + "/standings"
        responseStandings = oauth.session.get(urlStandings)
        xmlStandings = re.sub(' xmlns="[^"]+"', '', responseStandings.text, count=1)
        rootStandings = elementtree.fromstring(xmlStandings)
        for team in rootStandings.findall('./league/standings/teams/team'):
            cur_team_key = team.find('team_key').text
            cur_team_rank = int(team.find('team_standings/rank').text)
            if wkId == 16 and cur_team_rank >= 9:
                team_keys_toilet.append(cur_team_key)
            elif wkId == 16 and cur_team_rank <= 2:
                team_keys_playoffs.append(cur_team_key)
            elif wkId == 15 and cur_team_rank <= 4:
                team_keys_playoffs.append(cur_team_key)
    # print(team_keys_toilet)
    # print(team_keys_playoffs)

    teams = sorted(teams_map.get(yrId).values())
    recent_games = []
    return_list = []
    for matchup in root.findall('./league/scoreboard/matchups/matchup'):
        is_playoffs = matchup.find('is_playoffs').text
        is_consolation = matchup.find('is_consolation').text
        win_team_key = matchup.find('winner_team_key').text
        for team in matchup.findall('teams/team'):
            cur_key = team.find('team_key').text
            if cur_key == win_team_key:
                winner = team.find('name').text
                winner_score = team.find('team_points/total').text
                winner_manager = team.find('managers/manager/nickname').text
            else:
                loser = team.find('name').text
                loser_score = team.find('team_points/total').text
                loser_manager = team.find('managers/manager/nickname').text
        # printout just informational
        game_info_str = "{}-{}, winner: {}({}: {}), loser: {}({}) ({}-{})".format(winner_score, loser_score,
                                                                                  winner, winner_manager, win_team_key,
                                                                                  loser, loser_manager,
                                                                                  is_playoffs, is_consolation)
        print(game_info_str)
        return_list.append(game_info_str)

        if not team_keys_playoffs:
            play_flag = is_playoffs == '1' and is_consolation != '1'
        else:
            play_flag = win_team_key in team_keys_playoffs
        if not team_keys_playoffs:
            consol_flag = is_consolation == '1'
        else:
            consol_flag = win_team_key not in team_keys_playoffs
        if team_keys_toilet and win_team_key in team_keys_toilet:
            toilet_flag = True
        else:
            toilet_flag = False

        # TODO better way to do? dealing w/ team name change? any way to link yahoo teamId to tm_id, and/or mgrName?
        searchTm1 = [idx for idx, team in enumerate(teams) if winner in team.name]
        if not searchTm1:
            searchTm1 = [idx for idx, team in enumerate(teams) if team.manager.name.split()[0].upper() in winner_manager.upper()]
        tm1Idx = int(searchTm1[0])
        tm1Score = float(winner_score)
        searchTm2 = [idx for idx, team in enumerate(teams) if loser in team.name]
        if not searchTm2:
            searchTm2 = [idx for idx, team in enumerate(teams) if team.manager.name.split()[0].upper() in loser_manager.upper()]
        tm2Idx = int(searchTm2[0])
        tm2Score = float(loser_score)

        if wkId > 9:
            gmId = "{}{}{}{}".format(yrId, wkId, min(tm1Idx, tm2Idx), max(tm1Idx, tm2Idx))
        else:
            gmId = "{}0{}{}{}".format(yrId, wkId, min(tm1Idx, tm2Idx), max(tm1Idx, tm2Idx))

        selMgrId1 = str(teams[tm1Idx].manager.idManager)
        selMgrId2 = str(teams[tm2Idx].manager.idManager)

        if int(selMgrId1) > int(selMgrId2):
            rivalId = selMgrId2 + selMgrId1
        else:
            rivalId = selMgrId1 + selMgrId2

        # printout just informational
        print("{},{},{},{},{},{},{},{},{},{},{}".format(gmId, yrId, wkId, "Y" if play_flag else "",
                                                        teams[tm1Idx].idTeam, tm1Score, teams[tm2Idx].idTeam, tm2Score,
                                                        "Y" if consol_flag else "", rivalId,
                                                        "Y" if toilet_flag else ""))
        teams[tm1Idx].accumulateGame(True, play_flag, consol_flag, tm1Score, tm2Score)
        teams[tm2Idx].accumulateGame(False, play_flag, consol_flag, tm2Score, tm1Score)

        newGame = fflgame.Game(int(gmId), yrId, wkId, play_flag, consol_flag, toilet_flag,
                               teams[tm1Idx].idTeam, tm1Score, teams[tm2Idx].idTeam, tm2Score, int(rivalId))
        recent_games.append(newGame)

    if wkId <= fflconstants.WEEKS_PER_YEAR:
        teams = sorted(teams, key=lambda tm: [int(tm.wins), float(tm.pointsFor)])
        for idx, team in enumerate(teams):
            team.regularSeasonRank = 10 - idx
        fflteam.create_tm_scores_handler(teams_map, yrId, is_generate_new_file)

    if is_generate_new_file:
        if is_reload:
            for game in games:
                if game.year != yrId or game.week != wkId:
                    recent_games.append(game)
            fflgame.write_game_file(recent_games)
        else:
            games.extend(recent_games)
            fflgame.write_game_file(games)

    return return_list
