-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS shop_status;

CREATE TABLE IF NOT EXISTS shop_status (
    bid         BIGINT UNSIGNED PRIMARY KEY,
    description VARCHAR(64)
) ENGINE=InnoDB;

INSERT INTO shop_status VALUES ('1','canceld');
INSERT INTO shop_status VALUES ('2','out of stock');
INSERT INTO shop_status VALUES ('3','pending');
INSERT INTO shop_status VALUES ('4','complete');
INSERT INTO shop_status VALUES ('5','payed');

