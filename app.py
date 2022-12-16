import os

from csv import DictReader
from flask import json, Flask, flash, redirect, render_template, request, session
from helpers import apology
from sql import SQL

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fpl.db")


#opens player data and creates a gameweek list
with open('merged_gw1.csv', 'r', encoding="utf8") as file:
    reader = DictReader(file)
    list1 = []
    for line in reader:
        list1.append(int(line['GW']))

#gets current gameweek number
GW = [max(list1)]

#gets the previous two gameweek numbers
for i in range(2):
    new_list = set(list1)
    new_list.remove(max(new_list))
    GW.append(max(new_list))
    list1 = new_list

#opens fixtures.csv and creates a fixture week list
with open("fixtures.csv", "r") as file2:
    reader2 = DictReader(file2)
    list2 = []
    for line2 in reader2:
       list2.append(line2['event'])

#removes non numeric values and creates an ordered int list
list2 = [x for x in list2 if x.isdigit()]
list2 = [eval(i) for i in list2]
list2 = list(set(list2))

#gets the next three gameweek numbers
event = []
for z in range(38):
    m = int(GW[0])
    if z == m:
        event.append(list2[z + 1])
        event.append(list2[z + 2])
        event.append(list2[z + 3])
        break

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    index = render_template("index.html")
    topcurrentplayers = db.execute("SELECT position, name, team, SUM(minutes) AS 'totalminutes', ROUND(AVG(total_points)) AS 'averagepoints', SUM(total_points) AS 'overallpoints', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC LIMIT 10", 16, 15, 14)
    topcurrentforwards = db.execute("SELECT position, name, team, SUM(minutes) AS 'totalminutes', ROUND(AVG(total_points)) AS 'averagepoints', SUM(total_points) AS 'overallpoints',value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE position = 'FWD' AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC LIMIT 5", int(GW[0]), int(GW[1]), int(GW[2]))
    topcurrentmidfielders = db.execute("SELECT position, name, team, SUM(minutes) AS 'totalminutes', ROUND(AVG(total_points)) AS 'averagepoints', SUM(total_points) AS 'overallpoints', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE position = 'MID' AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC LIMIT 5", int(GW[0]), int(GW[1]), int(GW[2]))
    topcurrentdefenders = db.execute("SELECT position, name, team, SUM(minutes) AS 'totalminutes', ROUND(AVG(total_points)) AS 'averagepoints', ROUND(AVG(goals_conceded), 2) AS 'goals_conceded', SUM(total_points) AS 'overallpoints', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE position = 'DEF' AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC LIMIT 5", int(GW[0]), int(GW[1]), int(GW[2]))
    topcurrentgoalkeepers = db.execute("SELECT position, name, team, SUM(minutes) AS 'totalminutes', ROUND(AVG(total_points)) AS 'averagepoints', ROUND(AVG(goals_conceded), 2) AS 'goals_conceded', SUM(total_points) AS 'overallpoints', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE position = 'GK' AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC LIMIT 5", int(GW[0]), int(GW[1]), int(GW[2]))

    return render_template("index.html", GW1 = GW[0], topcurrentplayers = topcurrentplayers, topcurrentforwards = topcurrentforwards, topcurrentmidfielders = topcurrentmidfielders, topcurrentdefenders = topcurrentdefenders, topcurrentgoalkeepers = topcurrentgoalkeepers, index=index)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        positions = ["All", "FWD", "MID", "DEF", "GK"]
        teams = ["All", "Arsenal", "Aston Villa", "Bournemouth","Brentford", "Brighton", "Chelsea", "Crystal Palace", "Everton", "Fulham",
        "Leeds", "Liverpool", "Leicester", "Man City", "Man Utd", "Newcastle", "Nott'm Forest", "Southampton", "Spurs",
        "West Ham", "Wolves"]
        CFWF = ["Current Form", "Whole Season"]
        search = render_template("search.html")
        return render_template("search.html", search = search, positions = positions, teams = teams, CFWF = CFWF)
    elif request.method == "POST":
        minavgpoints = request.form.get("minavgpoints")
        if not minavgpoints:
            minavgpoints = 0
        min_FDR = request.form.get('FDR')
        if not min_FDR:
            min_FDR = 100
        team = request.form.get('team')
        position = request.form.get('position')
        if request.form.get('form') == "Current Form":
            if position == "All" and team == "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC", int(GW[0]), int(GW[1]), int(GW[2]))
            elif team == "All" and position != "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE position LIKE ? AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC", position, int(GW[0]), int(GW[1]), int(GW[2]))
            elif team != "All" and position == "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE team = ? AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC", team, int(GW[0]), int(GW[1]), int(GW[2]))
            elif team != "All" and position != "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', ROUND(AVG(expected_goals), 2) AS xG, ROUND(AVG(expected_assists), 2) AS expected_assists FROM merged_gw WHERE team = ? AND position = ? AND (GW = ? OR GW = ? OR GW = ?) GROUP BY name ORDER BY (AVG(total_points)) DESC", team, position, int(GW[0]), int(GW[1]), int(GW[2]))
            else:
                return apology("error", 400)
            playerlist = []
            finallist = {}
            rows2 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 16)
            rows3 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 17)
            rows4 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 18)

            for row in rows:
                for line in rows2:
                    if line["Team Name"] == row["team"]:
                        FDR = int(line["Fixture Difficulty"])
                        for line2 in rows3:
                            if line2["Team Name"] == row["team"]:
                                FDR = FDR + int(line2["Fixture Difficulty"])
                                for line3 in rows4:
                                    if line3["Team Name"] == row["team"]:
                                        FDR = FDR + int(line3["Fixture Difficulty"])

                                        #checks if FDR rating is below or equal to the users input
                                        if FDR <= int(min_FDR) and row["average points"] > int(minavgpoints):
                                            finallist["position"] = (row["position"])
                                            finallist["name"] = (row["name"])
                                            finallist["team"] = (row["team"])
                                            finallist["averagepoints"] = int(row["average points"])
                                            finallist["FDR"] = int(FDR)
                                            finallist["value"] = row["value"]
                                            finallist["pointspermili"] = row["pointspermili"]
                                            copy = finallist.copy()
                                            playerlist.append(copy)

            return render_template("results.html", playerlist = playerlist)

        else:
            if position == "All" and team == "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', AVG(expected_goals) AS xG, AVG(expected_assists) AS expected_assists FROM merged_gw GROUP BY name ORDER BY (AVG(total_points)) DESC")
            elif team != "All" and position == "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', AVG(expected_goals) AS xG, AVG(expected_assists) AS expected_assists FROM merged_gw WHERE team LIKE ? GROUP BY name ORDER BY (AVG(total_points)) DESC", team)
            elif team == "All" and position != "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', AVG(expected_goals) AS xG, AVG(expected_assists) AS expected_assists FROM merged_gw WHERE position LIKE ? GROUP BY name ORDER BY (AVG(total_points)) DESC", position)
            elif team != "All" and position != "All":
                rows = db.execute("SELECT position, name, team, SUM(minutes) AS 'total minutes', ROUND(AVG(total_points)) AS 'average points', ROUND(AVG(influence)) AS 'average influence', SUM(total_points) AS 'overall points', value, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili', AVG(expected_goals) AS xG, AVG(expected_assists) AS expected_assists FROM merged_gw WHERE team LIKE ? AND position LIKE ? GROUP BY name ORDER BY (AVG(total_points)) DESC",team, position)
            playerlist = []
            finallist = {}
            rows2 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 16)
            rows3 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 17)
            rows4 = db.execute("SELECT name1 AS 'Team Name', CASE WHEN (fix.team_a = teams.id1) THEN (fix.team_a_difficulty) WHEN (fix.team_h = teams.id1) THEN (fix.team_h_difficulty) END AS 'Fixture Difficulty', event FROM teams, fix WHERE (teams.id1 = fix.team_a  OR teams.id1 = fix.team_h) AND (fix.event LIKE ?) GROUP BY name1", 18)

            for row in rows:
                for line in rows2:
                    if line["Team Name"] == row["team"]:
                        FDR = int(line["Fixture Difficulty"])
                        for line2 in rows3:
                            if line2["Team Name"] == row["team"]:
                                FDR = FDR + int(line2["Fixture Difficulty"])
                                for line3 in rows4:
                                    if line3["Team Name"] == row["team"]:
                                        FDR = FDR + int(line3["Fixture Difficulty"])

                                        #checks if FDR rating is below or equal to the users input
                                        if FDR <= int(min_FDR) and row["average points"] > int(minavgpoints):
                                            finallist["position"] = (row["position"])
                                            finallist["name"] = (row["name"])
                                            finallist["team"] = (row["team"])
                                            finallist["averagepoints"] = int(row["average points"])
                                            finallist["FDR"] = int(FDR)
                                            finallist["value"] = row["value"]
                                            finallist["pointspermili"] = row["pointspermili"]
                                            copy = finallist.copy()
                                            playerlist.append(copy)


            return render_template("results.html", playerlist = playerlist)


@app.route("/results", methods=["GET", "POST"])
def results():
        return render_template("results.html")

@app.route("/playerstats", methods=["GET", "POST"])
def playerstats():
    if request.method == "GET":
        playernames = []
        stat = db.execute("SELECT name FROM merged_gw GROUP BY name")
        for line in stat:
            playernames.append(line["name"])
        playerstats = render_template("playerstats.html")
        return render_template("playerstats.html", playernames = playernames, playerstats = playerstats)
    else:
        nameweb = request.form.get("nameweb")
        maxgoals = []
        maxgoalsgw = []
        maxpointtotal = []
        maxpointtotalgw = []
        stat = db.execute("SELECT name, minutes, goals_scored, assists, yellow_cards, red_cards, influence, total_points, GW, value, name1 FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? AND GW < ? ORDER BY GW", nameweb, GW[0] + 1)
        hipointstotals = db.execute("SELECT MAX(total_points) AS 'total_points', goals_scored, assists, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY total_points ",nameweb)
        higoalscoredtotal = db.execute("SELECT MAX(goals_scored) AS 'goals_scored', assists, total_points, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY goals_scored", nameweb)
        pointspermili = db.execute("SELECT name, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili' FROM merged_gw WHERE name LIKE ? GROUP BY name", nameweb)
        price = []
        for line in stat:
            name = line["name"]
            price.append(line["value"])

        price = set(price)
        for line in price:
            price = float(line)

        for line in higoalscoredtotal:
            maxgoals = (line["goals_scored"])
            maxgoalsgw = (line["GW"])
            maxgoalopp = line["opposition"]
        for line in hipointstotals:
            maxpointtotal = (line["total_points"])
            maxpointtotalgw = (line["GW"])
            maxpointtotalopp = line["opposition"]

        return render_template("resultstats.html", pointspermili = pointspermili, maxpointtotalopp = maxpointtotalopp, stat = stat, price = price, maxgoalopp = maxgoalopp, namesql = name, maxgoals = maxgoals, maxgoalsgw = maxgoalsgw, maxpointtotal = maxpointtotal, maxpointtotalgw = maxpointtotalgw)

@app.route("/compareplayers", methods = ["GET", "POST"])
def compareplayer():
    if request.method == "GET":
        playernames = []
        stat = db.execute("SELECT name FROM merged_gw GROUP BY name")
        for line in stat:
            playernames.append(line["name"])
        compareplayer = render_template("compareplayers.html")
        return render_template("compareplayers.html", compareplayer = compareplayer, playernames = playernames)
    else:
        name1 = request.form.get("nameweb1")
        name2 = request.form.get("nameweb2")
        statp1 = db.execute("SELECT name, SUM(minutes) AS 'minutes', SUM(goals_scored) AS 'goals_scored', SUM(assists) AS 'assists', SUM(yellow_cards) AS 'yellow_cards', SUM(red_cards) AS 'red_cards', ROUND(AVG(influence), 2) AS 'average_influence', SUM(total_points) AS 'total_points', value FROM merged_gw WHERE name LIKE ? AND GW < ? GROUP BY name", name1, GW[0] + 1)
        statp2 = db.execute("SELECT name, SUM(minutes) AS minutes, SUM(goals_scored) AS goals_scored, SUM(assists) AS assists, SUM(yellow_cards) AS yellow_cards, SUM(red_cards) AS red_cards, ROUND(AVG(influence), 2) average_influence, SUM(total_points) AS total_points, value FROM merged_gw WHERE name LIKE ? AND GW < ? GROUP BY name", name2, GW[0] + 1)
        #player 1 points and goals
        pricep1 = []
        for line in statp1:
            name1 = line["name"]
            pricep1.append(line["value"])

        pricep1 = set(pricep1)
        for line in pricep1:
            pricep1 = float(line)
        hipointstotal1 = db.execute("SELECT MAX(total_points) AS 'total_points', goals_scored, assists, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY total_points ",name1)
        higoalscoredtotal1 = db.execute("SELECT MAX(goals_scored) AS 'goals_scored', assists, total_points, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY goals_scored", name1)
        pointspermili1 = db.execute("SELECT name, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili' FROM merged_gw WHERE name LIKE ? GROUP BY name", name1)
        #player 2 points and goals
        pricep2 = []
        hipointstotal2 = db.execute("SELECT MAX(total_points) AS 'total_points', goals_scored, assists, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY total_points ",name2)
        higoalscoredtotal2 = db.execute("SELECT MAX(goals_scored) AS 'goals_scored', assists, total_points, GW, name1 AS 'opposition' FROM merged_gw, teams WHERE id1 = opponent_team AND name LIKE ? GROUP BY goals_scored", name2)
        pointspermili2 = db.execute("SELECT name, ROUND(AVG(total_points)/CAST(value AS float), 2) AS 'pointspermili' FROM merged_gw WHERE name LIKE ? GROUP BY name", name2)
        pricep2 = []
        for line in statp2:
            name2 = line["name"]
            pricep2.append(line["value"])

        pricep2 = set(pricep2)
        for line in pricep2:
            pricep2 = float(line)
        return render_template("compareresults.html", statp1 = statp1, name1 = name1, pricep1 = pricep1, pointspermili1 = pointspermili1, statp2 = statp2, name2 = name2, pricep2 = pricep2, pointspermili2 = pointspermili2)

