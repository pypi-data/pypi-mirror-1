-- Copyright(c) gert.cuykens@gmail.com

DROP DATABASE IF EXISTS www;

CREATE DATABASE IF NOT EXISTS www CHARACTER SET utf8;

GRANT ALL ON www TO 'www'@'localhost' IDENTIFIED BY 'www';

FLUSH PRIVILEGES;

