#!/usr/bin/python
# Copyright(c) gert.cuykens@gmail.com

print "HTTP/1.0 200 OK\n"
print "Content-Type: text/html\n\n"

import sys,os,MySQLdb
print sys.stdin.read(os.environ.get('CONTENT_LENGTH',0))
conn = MySQLdb.connect (host = "localhost",
                        user = "root",
                        passwd = "root",
                        db = "")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]
cursor.close ()
conn.close ()

