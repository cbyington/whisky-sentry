CREATE TABLE IF NOT EXISTS alerts 
  (date timestamp with time zone, 
   sku INTEGER, 
   name VARCHAR, 
   price FLOAT, 
   quantity_on_hand INTEGER, 
   allocation INTEGER);
   
ALTER TABLE alerts ADD PRIMARY KEY (sku, date);
CREATE INDEX ON alerts (sku);
CREATE INDEX ON alerts (date);
