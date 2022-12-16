from csv import DictReader
import sqlite3
import urllib.request
import os

#file_path = 'merged_gw.csv'
#os.remove(file_path)

urllib.request.urlretrieve("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/gws/merged_gw.csv", "merged_gw1.csv")

db1 = sqlite3.connect("fpl.db")
db = db1.cursor()
db.execute("DROP TABLE merged_gw")
db.execute("CREATE TABLE merged_gw (name TEXT, position TEXT, team TEXT, expected_goals FLOAT, expected_assists FLOAT, minutes INT, goals_scored INT, assists INT, yellow_cards INT, red_cards INT, influence FLOAT, total_points INT, goals_conceded INT, opponent_team INT, GW INT, value FLOAT)")

with open('merged_gw1.csv', 'r') as file:
    reader = DictReader(file)
    to_db = [(i['name'], i['position'], i['team'], i['expected_goals'], i['expected_assists'], i['minutes'], i['goals_scored'], i['assists'], i['yellow_cards'], i['red_cards'], i['influence'], i['total_points'], i['goals_conceded'], i['opponent_team'], i['GW']) for i in reader]

db.executemany("INSERT INTO merged_gw (name, position, team, expected_goals, expected_assists, minutes, goals_scored, assists, yellow_cards, red_cards, influence, total_points, goals_conceded, opponent_team, GW) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_db)
db1.commit()
db1.close()