import jsons
from flask import Flask, render_template, request, session, json, jsonify, g, flash, url_for, redirect
from fflconstants import flatten_team_dict_into_list
import fflmanager
import fflgame
import fflteam
from yahoo import yahoo_api_loadweek


app = Flask(__name__)
app.secret_key = b'_5#y2L"F6R8z\n\xec]/'


IS_STORE_IN_SESSION = False
IS_PRINT_SESSION_VARIABLES = False


@app.route("/")
def index():
    return redirect(url_for('home'))


@app.route("/home", methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        return redirect(url_for('load'))

    for tmp in session:
        print(tmp)
    # return "Welcome to the League of Extraordinary Cheapness"
    return render_template('home.html')


@app.route("/load")
def load():
    managers_dict = fflmanager.read_manager_file()
    games_list = fflgame.read_game_file()
    year_to_team = fflteam.read_team_file(managers_dict, games_list)
    return_item = yahoo_api_loadweek(managers_dict, games_list, year_to_team)
    # return json.dumps(return_item)
    flash('Load was successful!')
    return render_template('loadweek.html', games=return_item)


@app.route("/managers")
def managers():
    if IS_STORE_IN_SESSION:
        return session['managers_dict']
    else:
        managers_dict = fflmanager.read_manager_file()
        fflteam.read_team_file(managers_dict, fflgame.read_game_file())  # just call to populate records
        # print(jsons.dump(managers_dict))
        managers_list = []
        for manager in managers_dict.values():
            managers_list.append(manager)  # managers_list.append(manager.__str__())
        return render_template('managers.html', managers=managers_list)


@app.route("/games")
def games():
    if IS_STORE_IN_SESSION:
        return session['games_list']
    else:
        games_list = fflgame.read_game_file()
        # print(json.dumps([game.__dict__ for game in games_list]))
        return render_template('games.html', games=games_list)


@app.route("/teams")
def teams():
    if IS_STORE_IN_SESSION:
        return session['year_to_team']
    else:
        managers_dict = fflmanager.read_manager_file()
        games_list = fflgame.read_game_file()
        year_to_team = fflteam.read_team_file(managers_dict, games_list)
        # print jsons.dump(year_to_team)
        teams_list = []
        for team in flatten_team_dict_into_list(year_to_team):
            teams_list.append(team)
        return render_template('teams.html', teams=reversed(teams_list))


@app.before_first_request
def initialize_session_variables():
    print('initializing session variables...')  # sanity check
    session.clear()
    # TODO set up persistent/server-side storage, ?sqlite3? SQLAlchemy?
    if IS_STORE_IN_SESSION:
        managers_dict = fflmanager.read_manager_file()
        games_list = fflgame.read_game_file()
        year_to_team = fflteam.read_team_file(managers_dict, games_list)
        if IS_PRINT_SESSION_VARIABLES:
            for manager in managers_dict.values():
                print(manager)
            for game in games_list:
                print(game)
            for team in flatten_team_dict_into_list(year_to_team):
                print(team)
        session['managers_dict'] = jsons.dump(managers_dict)
        session['games_list'] = json.dumps([game.__dict__ for game in games_list])
        session['year_to_team'] = jsons.dump(year_to_team)


if __name__ == "__main__":
    app.run()
