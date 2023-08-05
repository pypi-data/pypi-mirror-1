-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS forum_messages;

CREATE TABLE IF NOT EXISTS forum_messages ( 
    uid     BIGINT UNSIGNED,
    tid     BIGINT UNSIGNED,
    mid     SERIAL PRIMARY KEY,
    time    DATETIME,
    message VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES register(uid)      ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(tid) REFERENCES forum_threads(tid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

