#!/bin/bash
# Copyright(c) gert.cuykens@gmail.com

openssl genrsa 1024 > key.pem
openssl req -new -x509 -key key.pem > ca.pem
#ln -sf ca.pem `openssl x509 -noout -hash < ca.pem`.0

cd /etc/apache2
su www-data
ssh-keygen -t rsa
cat .ssh/id_rsa.pub | ssh root@127.0.0.1 'cat >> .ssh/authorized_keys'
