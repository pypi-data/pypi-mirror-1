#!/bin/bash
echo "<a>http://code.google.com/p/appwsgi/downloads/list</a>"
echo "<h2>static</h2>" > htm/bench.htm
ab -n 10000 -w http://localhost:80/ >> htm/bench.htm
echo "<h2>mod wsgi embedded</h2>" >> htm/bench.htm
ab -n 10000 -w http://localhost:81/ >> htm/bench.htm
echo "<h2>mod wsgi deamon</h2>" >> htm/bench.htm
ab -n 10000 -w http://localhost:82/ >> htm/bench.htm
echo "<h2>fcgi with flup</h2>" >> htm/bench.htm
ab -n 10000 -w http://localhost:83/ >> htm/bench.htm
echo "<h2>scgi with flup</h2>" >> htm/bench.htm
ab -n 10000 -w http://localhost:84/ >> htm/bench.htm
echo "<h2>mod python</h2>" >> htm/bench.htm
ab -n 10000 -w http://localhost:85/ >> htm/bench.htm
