from db_connection import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text

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
    
