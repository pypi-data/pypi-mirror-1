#!/bin/sh
openssl dsaparam -rand -genkey -out ca.key 1024
openssl gendsa -des3 -out ca.key ca.key
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

