#!/bin/sh
# Copyright(c) gert.cuykens@gmail.com
# shell script for removing expired files

TIME=$(date +%s)
TIME=`expr $TIME - 3600`
FILES=(`ls *.tmp 2>/dev/null`)
TIMES=(`ls *.tmp 2>/dev/null -l --time-style=+%s | awk '{print $6}'`)
I=0
for FILE in ${FILES[@]}; do
if [ ${TIMES[$I]} -lt $TIME ]; then
rm $FILE
fi
I=`expr $I + 1`
done
exit 0
