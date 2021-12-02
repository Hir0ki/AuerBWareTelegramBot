CREATE TABLE IF NOT EXISTS artikel(
    artnr VARCHAR(32),
    außenmaße VARCHAR(50),
    besonderheit1 VARCHAR(80),
    besonderheit2 VARCHAR(80),
    stück_auf_palette INT,
    kategorie_id INT,
    versandfertig_link VARCHAR(500),
    PRIMARY KEY(artnr)
);


CREATE TABLE IF NOT EXISTS preise(
    preis_id SERIAL,
    created_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    artnr VARCHAR(32),
    preis_neu REAL,
    preis_b_ware REAL,
    preis_pro_stück_palatte_neu REAL,
    preis_pro_stück_palatte_b_ware REAL,
    währung VARCHAR(1)
);

SELECT create_hypertable('preise', 'created_datetime' );

CREATE INDEX ON  preise ( artnr, created_datetime DESC ); 


CREATE TABLE IF NOT EXISTS kategorien(
    kategorie_id SERIAL,
    name VARCHAR(80) NOT NULL,
    url VARCHAR(250) NOT NULL,
    besonderheit_1_name VARCHAR(40),
    besonderheit_2_name VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS bestand(
    created_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    artnr VARCHAR(32) NOT NUll,
    verfügbar INT
);

SELECT create_hypertable('bestand', 'created_datetime' );

CREATE INDEX ON  bestand ( artnr, created_datetime DESC ); 

CREATE TABLE IF NOT EXISTS clients(client_id VARCHAR(32), PRIMARY KEY(client_id));

