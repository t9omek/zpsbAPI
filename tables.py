from db_connection import Base
from sqlalchemy import Column, Integer, String, Decimal, TIMESTAMP, Boolean, text

class Pracownik(Base):
    __tablename__ = "Pracownik"
    id_pracownika = Column(Integer, primary_key=True, nullable=False)
    imie = Column(String, nullable=False)
    nazwisko = Column(String, nullable=False)
    stanowisko = Column(String, nullable=False)

class Status(Base):
    __tablename__ = "Status"
    id_statusu = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)
    
class Dostawa(Base):
    __tablename__ = "Dostawa"
    id_dostawy = Column(Integer, primary_key=True, nullable=False)
    id_formy_dostawy = Column(Integer, nullable=False)
    id_firmy = Column(Integer, nullable=False)

class FirmaDostawcza(Base):
    __tablename__ = "FirmaDostawcza"
    id_firmy = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)
    
class FormaDostawy(Base):
    __tablename__ = "FormaDostawy"
    id_formy_dostawy = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)
    

class Zamowienia(Base):
    __tablename__ = "Zamowienia"
    id_zamowienia = Column(Integer, primary_key=True, nullable=False)
    data_zamowienia = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    id_statusu = Column(Integer, nullable=False)
    id_pracownika = Column(Integer, nullable=False)
    id_klienta = Column(Integer, nullable=False)
    id_formy_platnosci = Column(Integer, nullable=False)
    id_dostawy = Column(Integer, nullable=False)

class FormaPlatnosci(Base):
    __tablename__ = "FormaPlatnosci"
    id_formy_platnosci = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)

class PozycjaZamowienia(Base):
    __tablename__ = "PozycjaZamowienia"
    id_pozycji = Column(Integer, primary_key=True, nullable=False)
    id_zamowienia = Column(Integer, nullable=False)
    id_produktu = Column(Integer, nullable=False)
    ilosc = Column(Integer, nullable=False)
    cena = Column(Decimal(10, 2), nullable=False)

class Produkt(Base):
    __tablename__ = "Produkt"
    id_produktu = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)
    cena = Column(Decimal(10, 2), nullable=False)

class ProduktMagazyn(Base):
    __tablename__ = "ProduktMagazyn"
    id_produktMagazyn = Column(Integer, primary_key=True, nullable=False)
    id_produktu = Column(Integer,nullable=False)
    id_magazynu = Column(Integer, nullable=False)
    ilosc = Column(Integer, nullable=False)

class Magazyn(Base):
    __tablename__ = "Magazyn"
    id_magazynu = Column(Integer, primary_key=True, nullable=False)
    nazwa = Column(String, nullable=False)

class Klient(Base):
    __tablename__ = "Klient"
    id_klienta = Column(Integer, primary_key=True, nullable=False)
    imie = Column(String, nullable=True)
    telefon = Column(String, nullable=True)
    nazwisko = Column(String, nullable=True)
    email = Column(String, nullable=True)

class Adres(Base):
    __tablename__ = "Adres"
    id_adresu = Column(Integer, primary_key=True, nullable=False)
    id_klienta = Column(Integer, nullable=False)
    miasto = Column(String, nullable=False)
    ulica = Column(String, nullable=False)
    kod_pocztowy = Column(String, nullable=False)