DROP SCHEMA IF EXISTS integration CASCADE;
CREATE SCHEMA integration;

SET search_path TO integration;

CREATE TABLE Klient (
    id_klienta BIGSERIAL PRIMARY KEY,
    imie VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    telefon VARCHAR(30),
    email VARCHAR(150)
);

CREATE TABLE Adres (
    id_adresu BIGSERIAL PRIMARY KEY,
    id_klienta BIGINT NOT NULL,
    miasto VARCHAR(100) NOT NULL,
    ulica VARCHAR(150) NOT NULL,
    kod_pocztowy VARCHAR(20) NOT NULL,

    CONSTRAINT fk_adres_klient
        FOREIGN KEY (id_klienta)
        REFERENCES Klient(id_klienta)
        ON DELETE CASCADE
);

CREATE TABLE Pracownik (
    id_pracownika BIGSERIAL PRIMARY KEY,
    imie VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    stanowisko VARCHAR(100)
);

CREATE TABLE Status (
    id_statusu BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(50) NOT NULL
);

CREATE TABLE FormaPlatnosci (
    id_formy_platnosci BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(50) NOT NULL
);

CREATE TABLE FormaDostawy (
    id_formy_dostawy BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(50) NOT NULL
);

CREATE TABLE FirmaDostawcza (
    id_firmy BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL
);

CREATE TABLE Dostawa (
    id_dostawy BIGSERIAL PRIMARY KEY,
    id_formy_dostawy BIGINT NOT NULL,
    id_firmy BIGINT NOT NULL,

    CONSTRAINT fk_dostawa_forma
        FOREIGN KEY (id_formy_dostawy)
        REFERENCES FormaDostawy(id_formy_dostawy),

    CONSTRAINT fk_dostawa_firma
        FOREIGN KEY (id_firmy)
        REFERENCES FirmaDostawcza(id_firmy)
);

CREATE TABLE Produkt (
    id_produktu BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(150) NOT NULL,
    cena DECIMAL(10,2) NOT NULL
);

CREATE TABLE Magazyn (
    id_magazynu BIGSERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL
);

CREATE TABLE ProduktMagazyn (
    id BIGSERIAL PRIMARY KEY,
    id_produktu BIGINT NOT NULL,
    id_magazynu BIGINT NOT NULL,
    ilosc INT NOT NULL,

    CONSTRAINT fk_pm_produkt
        FOREIGN KEY (id_produktu)
        REFERENCES Produkt(id_produktu)
        ON DELETE CASCADE,

    CONSTRAINT fk_pm_magazyn
        FOREIGN KEY (id_magazynu)
        REFERENCES Magazyn(id_magazynu)
        ON DELETE CASCADE
);

CREATE TABLE Zamowienie (
    id_zamowienia BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL,

    id_statusu BIGINT NOT NULL,
    id_pracownika BIGINT NOT NULL,
    id_klienta BIGINT NOT NULL,
    id_formy_platnosci BIGINT NOT NULL,
    id_dostawy BIGINT NOT NULL,

    CONSTRAINT fk_zamowienie_status
        FOREIGN KEY (id_statusu)
        REFERENCES Status(id_statusu),

    CONSTRAINT fk_zamowienie_pracownik
        FOREIGN KEY (id_pracownika)
        REFERENCES Pracownik(id_pracownika),

    CONSTRAINT fk_zamowienie_klient
        FOREIGN KEY (id_klienta)
        REFERENCES Klient(id_klienta),

    CONSTRAINT fk_zamowienie_platnosc
        FOREIGN KEY (id_formy_platnosci)
        REFERENCES FormaPlatnosci(id_formy_platnosci),

    CONSTRAINT fk_zamowienie_dostawa
        FOREIGN KEY (id_dostawy)
        REFERENCES Dostawa(id_dostawy)
);

CREATE TABLE PozycjaZamowienia (
    id BIGSERIAL PRIMARY KEY,
    id_zamowienia BIGINT NOT NULL,
    id_produktu BIGINT NOT NULL,
    ilosc INT NOT NULL,
    cena_zakupu DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_pz_zamowienie
        FOREIGN KEY (id_zamowienia)
        REFERENCES Zamowienie(id_zamowienia)
        ON DELETE CASCADE,

    CONSTRAINT fk_pz_produkt
        FOREIGN KEY (id_produktu)
        REFERENCES Produkt(id_produktu)
);

CREATE INDEX idx_zamowienie_klient
ON Zamowienie(id_klienta);

CREATE INDEX idx_pozycja_zamowienia
ON PozycjaZamowienia(id_zamowienia);

CREATE INDEX idx_pm_produkt
ON ProduktMagazyn(id_produktu);