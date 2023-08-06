-- Copyright(c) gert.cuykens@gmail.com

DROP DATABASE IF EXISTS www;

CREATE DATABASE IF NOT EXISTS www CHARACTER SET utf8;

-- GRANT ALL ON www TO 'www'@'localhost' IDENTIFIED BY 'www';
-- REVOKE ALL PRIVILEGES, GRANT OPTION FROM www
-- FLUSH PRIVILEGES;

CREATE TABLE www.sessions (
    SID     VARCHAR(64) PRIMARY KEY,
    EXP     DATETIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE www.register (
    UID     SERIAL PRIMARY KEY,
    GID     BIGINT UNSIGNED DEFAULT 2,
    SID     VARCHAR(64) UNIQUE NOT NULL,
    email   VARCHAR(64) UNIQUE NOT NULL,
    pwd     VARCHAR(64) DEFAULT '',
    name    VARCHAR(64) DEFAULT '',
    adress  VARCHAR(64) DEFAULT '',
    city    VARCHAR(64) DEFAULT '',
    country VARCHAR(64) DEFAULT '',
    phone   VARCHAR(64) DEFAULT '',
    picture BLOB,
    FOREIGN KEY(sid) REFERENCES www.sessions(sid) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE www.appointments (
    uid         BIGINT UNSIGNED,
    aid         SERIAL PRIMARY KEY,
    calendar    DATETIME,
    appointment VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES www.register(uid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE www.forum_topics(
    uid   BIGINT UNSIGNED,
    hid   SERIAL PRIMARY KEY,
    topic VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES www.register(uid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE www.forum_threads (
    uid     BIGINT UNSIGNED,
    hid     BIGINT UNSIGNED,
    tid     SERIAL PRIMARY KEY,
    thread  VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES www.register(uid)     ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(hid) REFERENCES www.forum_topics(hid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE www.forum_messages ( 
    uid     BIGINT UNSIGNED,
    tid     BIGINT UNSIGNED,
    mid     SERIAL PRIMARY KEY,
    time    DATETIME,
    message VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES www.register(uid)      ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(tid) REFERENCES www.forum_threads(tid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE www.shop_products (
    pid         SERIAL PRIMARY KEY,
    description VARCHAR(64),
    price       BIGINT UNSIGNED,
    qty         BIGINT
) ENGINE=InnoDB;

CREATE TABLE www.shop_status (
    bid         BIGINT UNSIGNED PRIMARY KEY,
    description VARCHAR(64)
) ENGINE=InnoDB;

INSERT INTO www.shop_status VALUES ('1','canceld');
INSERT INTO www.shop_status VALUES ('2','out of stock');
INSERT INTO www.shop_status VALUES ('3','pending');
INSERT INTO www.shop_status VALUES ('4','complete');
INSERT INTO www.shop_status VALUES ('5','payed');

CREATE TABLE www.shop_orders (
    uid      BIGINT UNSIGNED,
    oid      SERIAL PRIMARY KEY,
    bid      BIGINT UNSIGNED,    
    time     DATETIME,
    products VARCHAR(1024),
    comments VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES www.register(uid)    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(bid) REFERENCES www.shop_status(bid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

