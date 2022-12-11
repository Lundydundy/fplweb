import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
db = SQL("sqlite:///fpl.db")

names = db.execute("SELECT first_name, second_name, now_cost FROM players")

player = {}
finalist = []
for line in names:
    fname = line["first_name"]
    sname = line["second_name"]
    player["name"] = (fname + " " + sname)
    player["value"] = float(line["now_cost"])/10
    copy = player.copy()
    finalist.append(copy)
for line in finalist:
    name = line["name"]
    cost = line["value"]
    db.execute("UPDATE fpl SET value = ? WHERE name LIKE ?", cost, "%" + name + "%")