#!/bin/bash
# Copyright(c) gert.cuykens@gmail.com

echo "setup file permission"
chown -R www-data:www-data .
chmod -R 700 .

echo "setup database"
mysql -u root -p < database.sql

exit 0

#FILES=(`ls sql/*.sql 2>/dev/null`)
#for FILE in ${FILES[@]}; do
#if [ "sql/database.sql" != $FILE ]; then
#echo $FILE
#mysql -u root www < $FILE
#fi
#done
