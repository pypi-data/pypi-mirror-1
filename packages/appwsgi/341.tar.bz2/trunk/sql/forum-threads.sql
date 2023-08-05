-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS forum_threads;

CREATE TABLE IF NOT EXISTS forum_threads (
    uid     BIGINT UNSIGNED,
    hid     BIGINT UNSIGNED,
    tid     SERIAL PRIMARY KEY,
    thread  VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES register(uid)     ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(hid) REFERENCES forum_topics(hid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

