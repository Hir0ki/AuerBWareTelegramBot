from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Angebot:
    scraped_at: datetime
    außenmaße: str
    artnr: str
    besonderheit1: str
    besonderheit2: str
    preis_b: float
    preis_neu: float
    währung: str
    stück_auf_palette: int
    preis_stück_pro_palette_b: float
    preis_stück_pro_palette_neu: float
    verfügbar: int
    versandfertig_link: str
    kategorie_id: str


@dataclass
class Kategorie:
    kategorie_id: int
    name: str
    url: str
    besonderheit_1_name: str
    besonderheit_2_name: str


