#!/bin/sh
# Copyright(c) gert.cuykens@gmail.com
gcc -g -o handler.cgi handler.c -lexpat -lmysqlclient
export CONTENT_LENGTH=1000
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
<root>\
 <user>www</user>\
 <password></password>\
 <database>www</database>\
 <sql>SHOW DATABASES;</sql>\
</root>" | ./handler.cgi

