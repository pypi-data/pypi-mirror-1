-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS shop_products;

CREATE TABLE IF NOT EXISTS shop_products (
    pid         SERIAL PRIMARY KEY,
    description VARCHAR(64),
    price       BIGINT UNSIGNED,
    qty         BIGINT
) ENGINE=InnoDB;

INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
INSERT INTO shop_products VALUES (0, 'Bananas', '10', '100');
