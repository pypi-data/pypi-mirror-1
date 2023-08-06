# Copyright(c) gert.cuykens@gmail.com
import sqlite3

v = ""
with open("www.sql") as f:
    for line in f:
        v += line 

con = sqlite3.connect("www.db")
cur = con.cursor()
cur.executescript(v)

