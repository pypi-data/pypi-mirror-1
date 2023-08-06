#!/bin/bash
# Copyright(c) gert.cuykens@gmail.com

echo "setup database"
mysql -u root -p < database.sql

echo "setup openssl"
cd /etc/apache2
su www-data
ssh-keygen -t rsa
cat .ssh/id_rsa.pub | ssh root@127.0.0.1 'cat >> .ssh/authorized_keys'

openssl genrsa 1024 > key.pem
openssl req -new -x509 -key key.pem > ca.pem
#ln -sf ca.pem `openssl x509 -noout -hash < ca.pem`.0

exit 0

#echo "setup file permission"
#chown -R www-data:www-data .
#chmod -R 600 .

#echo "remove all .svn"
#find . -name .svn -print0 | xargs -0 rm -rf

#FILES=(`ls sql/*.sql 2>/dev/null`)
#for FILE in ${FILES[@]}; do
#if [ "sql/database.sql" != $FILE ]; then
#echo $FILE
#mysql -u root www < $FILE
#fi
#done

