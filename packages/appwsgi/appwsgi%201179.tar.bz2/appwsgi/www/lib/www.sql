-- Copyright(c) gert.cuykens@gmail.com

CREATE TABLE users (
    uid     VARCHAR(64) PRIMARY KEY,
    name    VARCHAR(64) DEFAULT '',
    adress  VARCHAR(64) DEFAULT '',
    city    VARCHAR(64) DEFAULT '',
    country VARCHAR(64) DEFAULT '',
    phone   VARCHAR(64) DEFAULT '',
    picture BLOB
);

CREATE TABLE groups (
    gid     VARCHAR(64),
    uid     VARCHAR(64),
    PRIMARY KEY(gid,uid),
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE sessions (
    uid     VARCHAR(64) UNIQUE,
    pwd     VARCHAR(64) DEFAULT '',
    sid     VARCHAR(64) PRIMARY KEY,
    exp     DATETIME,
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE appointments (
    uid         VARCHAR(64),
    aid         INTEGER PRIMARY KEY,
    calendar    DATETIME,
    appointment VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE forum_topics(
    uid   VARCHAR(64),
    hid   INTEGER PRIMARY KEY,
    topic VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE forum_threads (
    uid     VARCHAR(64),
    hid     BIGINT UNSIGNED,
    tid     INTEGER PRIMARY KEY,
    thread  VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(hid) REFERENCES forum_topics(hid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE forum_messages ( 
    uid     VARCHAR(64),
    tid     BIGINT UNSIGNED,
    mid     INTEGER PRIMARY KEY,
    time    DATETIME,
    message VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(tid) REFERENCES forum_threads(tid) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE shop_products (
    pid         INTEGER PRIMARY KEY,
    description VARCHAR(64),
    price       BIGINT UNSIGNED,
    qty         BIGINT
);

CREATE TABLE shop_status (
    bid         BIGINT UNSIGNED PRIMARY KEY,
    description VARCHAR(64)
);

INSERT INTO shop_status VALUES ('1','canceld');
INSERT INTO shop_status VALUES ('2','out of stock');
INSERT INTO shop_status VALUES ('3','pending');
INSERT INTO shop_status VALUES ('4','complete');
INSERT INTO shop_status VALUES ('5','payed');

CREATE TABLE shop_orders (
    uid      VARCHAR(64),
    oid      INTEGER PRIMARY KEY,
    bid      BIGINT UNSIGNED,    
    time     DATETIME,
    products VARCHAR(1024) DEFAULT '',
    comments VARCHAR(1024) DEFAULT '',
    FOREIGN KEY(uid) REFERENCES users(uid) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(bid) REFERENCES shop_status(bid) ON UPDATE CASCADE ON DELETE CASCADE
);

