#!/bin/bash
# Copyright(c) gert.cuykens@gmail.com

chown -R www-data:www-data .
chmod -R 700 .

echo "sql/database.sql"
mysql mysql < sql/database.sql

echo "sql/register.sql"
mysql www < sql/register.sql

echo "sql/appointments.sql"
mysql www < sql/appointments.sql

echo "sql/forum-topics.sql"
mysql www < sql/forum-topics.sql

echo "sql/forum-threads.sql"
mysql www < sql/forum-threads.sql

echo "sql/forum-messages.sql"
mysql www < sql/forum-messages.sql

echo "sql/shop-products.sql"
mysql www < sql/shop-products.sql

echo "sql/shop-status.sql"
mysql www < sql/shop-status.sql

echo "sql/shop-orders.sql"
mysql www < sql/shop-orders.sql

#FILES=(`ls sql/*.sql 2>/dev/null`)
#for FILE in ${FILES[@]}; do
#if [ "sql/database.sql" != $FILE ]; then
#echo $FILE
#mysql -u root www < $FILE
#fi
#done

exit 0
