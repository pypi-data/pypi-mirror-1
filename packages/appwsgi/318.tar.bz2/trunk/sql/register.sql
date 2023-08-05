-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS register;

CREATE TABLE IF NOT EXISTS register (
    email   VARCHAR(64) UNIQUE,
    pwd     VARCHAR(64),
    name    VARCHAR(64),
    adress  VARCHAR(64),
    city    VARCHAR(64),
    country VARCHAR(64),
    phone   VARCHAR(64),
    picture BLOB,
    UID     SERIAL PRIMARY KEY,
    GID     INT UNSIGNED DEFAULT 0,
    SID     VARCHAR(64) UNIQUE,
    EXP     DATETIME
) ENGINE=InnoDB;

INSERT INTO register VALUES ('admin',SHA1(''),'gert cuykens','kleine doornstraat 1','wilrijk 2610','belgium','0486','',0,2,'',NOW());

