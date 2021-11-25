CREATE TABLE IF NOT EXISTS artikel(
    artnr VARCHAR(32),
    außenmaße VARCHAR(50),
    besonderheit1 VARCHAR(80),
    besonderheit2 VARCHAR(80),
    preis_alt REAL,
    preis_neu REAL,
    währung VARCHAR(10),
    stück_auf_palette INT,
    preis_stück_pro_palette_alt REAL,
    preis_stück_pro_palette_neu REAL,
    verfügbar INT,
    versandfertig_link VARCHAR(500),
    ist_aktive BOOLEAN,
    PRIMARY KEY(artnr)
);

CREATE TABLE IF NOT EXISTS clients(client_id VARCHAR(32), PRIMARY KEY(client_id));