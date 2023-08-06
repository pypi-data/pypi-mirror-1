#!/bin/bash
# Copyright(c) gert.cuykens@gmail.com
openssl genrsa 1024 > key.pem
openssl req -new -x509 -key key.pem > ca.pem
#ln -sf ca.pem `openssl x509 -noout -hash < ca.pem`.0

