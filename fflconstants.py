FIRST_YEAR = 2006
FIRST_YEAR_MODERN_ERA = 2008
THIS_YEAR = 2020
LAST_COMPLETE_YEAR = 2020
WEEKS_PER_YEAR = 13
THIS_WEEK = -1

ASTERISK_2006 = "**"
COLOR_STR_2006 = "red"

ASTERISK_2007 = "*"
COLOR_STR_2007 = "blue"

TM_ID_3RD_STRING = 49


def initialize_this_week_constant(week):
    global THIS_WEEK
    if THIS_WEEK < 0:
        THIS_WEEK = week


def generate_prefix(is2006, is2007):
    if is2006:
        return "<font color=\"" + COLOR_STR_2006 + "\">"
    elif is2007:
        return "<font color=\"" + COLOR_STR_2007 + "\">"
    else:
        return ""


def generate_postfix(is2006, is2007):
    if is2006 or is2007:
        return "</font>"
    else:
        return ""


def generate_asterisk(is2006, is2007):
    if is2006:
        return ASTERISK_2006
    elif is2007:
        return ASTERISK_2007
    else:
        return ""


def generate_active_string(year, week):
    if year == THIS_YEAR and week == THIS_WEEK:
        return " (Active)"
    else:
        return ""


def generate_schedule_string(year, week, is_playoffs, is_consolation, is_toilet):
    if is_playoffs:
        if week == 16:
            scheduleStr = "Championship, {}".format(year)
        elif week == 15:
            scheduleStr = "Semi-Finals, {}".format(year)
        else:
            scheduleStr = "1st Round Playoffs, {}".format(year)
    elif is_consolation:
        if is_toilet:
            scheduleStr = "Toilet Bowl, {}".format(year)
        else:
            scheduleStr = "Consolation Game, {}".format(year)
    else:
        scheduleStr = "Week {}, {}".format(week, year)
    return scheduleStr


def generate_placement_string(place):
    if place != 11 and place % 10 == 1:
        return "st"
    elif place != 12 and place % 10 == 2:
        return "nd"
    elif place != 13 and place % 10 == 3:
        return "rd"
    else:
        return "th"


def flatten_team_dict_into_list(year_to_team):
    ret = []
    for teams in year_to_team.values():
        ret.extend(teams.values())
    return ret
