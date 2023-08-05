-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS forum_topics;

CREATE TABLE IF NOT EXISTS forum_topics(
    uid   BIGINT UNSIGNED,
    hid   SERIAL PRIMARY KEY,
    topic VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES register(uid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

