from csv import DictReader
import sqlite3
import urllib.request
import os

#file_path = 'merged_gw.csv'
#os.remove(file_path)

#urllib.request.urlretrieve("https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/cleaned_players.csv", "merged_gw.csv")

db1 = sqlite3.connect("fpl.db")
db = db1.cursor()
db.execute("DROP TABLE fpl")
db.execute("CREATE TABLE fpl (name TEXT, position TEXT, team TEXT, minutes INT, goals_scored INT, assists INT, yellow_cards INT, red_cards INT, influence FLOAT, total_points INT, opponent_team INT, GW INT)")

with open('merged_gw.csv', 'r') as file:
    reader = DictReader(file)
    to_db = [(i['name'], i['position'], i['team'], i['minutes'], i['goals_scored'], i['assists'], i['yellow_cards'], i['red_cards'], i['influence'], i['total_points'], i['opponent_team'], i['GW']) for i in reader]

db.executemany("INSERT INTO fpl (name, position, team, minutes, goals_scored, assists, yellow_cards, red_cards, influence, total_points, opponent_team, GW) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_db)
db1.commit()
db1.close()