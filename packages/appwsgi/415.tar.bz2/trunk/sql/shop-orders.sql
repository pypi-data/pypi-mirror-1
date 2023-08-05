-- Copyright(c) gert.cuykens@gmail.com

DROP TABLE IF EXISTS shop_orders;

CREATE TABLE IF NOT EXISTS shop_orders (
    uid      BIGINT UNSIGNED,
    oid      SERIAL PRIMARY KEY,
    bid      BIGINT UNSIGNED,    
    time     DATETIME,
    products VARCHAR(1024),
    comments VARCHAR(1024),
    FOREIGN KEY(uid) REFERENCES register(uid)    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(bid) REFERENCES shop_status(bid) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO shop_orders VALUES ('1','1','1',NOW(),'<?xml version="1.0" encoding="UTF-8"?>
<root>
 <record index="0">
  <nr>101</nr>
  <description>apple</description>
  <prise>56</prise>
  <qty>1</qty>
 </record>
 <record index="1">
  <nr>102</nr>
  <description>banana</description>
  <prise>75</prise>
  <qty>1</qty>
 </record>
</root>');

