from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DECIMAL,
    Date
)

from sqlalchemy.orm import relationship

from db_connection import Base


class Klient(Base):
    __tablename__ = "Klient"

    id_klienta = Column(Integer, primary_key=True)
    imie = Column(String(100), nullable=False)
    nazwisko = Column(String(100), nullable=False)
    telefon = Column(String(30))
    email = Column(String(150))

    adresy = relationship("Adres", back_populates="klient")
    zamowienia = relationship("Zamowienie", back_populates="klient")


class Adres(Base):
    __tablename__ = "Adres"

    id_adresu = Column(Integer, primary_key=True)

    id_klienta = Column(
        Integer,
        ForeignKey("Klient.id_klienta", ondelete="CASCADE"),
        nullable=False
    )

    miasto = Column(String(100), nullable=False)
    ulica = Column(String(150), nullable=False)
    kod_pocztowy = Column(String(20), nullable=False)

    klient = relationship("Klient", back_populates="adresy")


class Pracownik(Base):
    __tablename__ = "Pracownik"

    id_pracownika = Column(Integer, primary_key=True)
    imie = Column(String(100), nullable=False)
    nazwisko = Column(String(100), nullable=False)
    stanowisko = Column(String(100))

    zamowienia = relationship("Zamowienie", back_populates="pracownik")


class Status(Base):
    __tablename__ = "Status"

    id_statusu = Column(Integer, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    zamowienia = relationship("Zamowienie", back_populates="status")


class FormaPlatnosci(Base):
    __tablename__ = "FormaPlatnosci"

    id_formy_platnosci = Column(Integer, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    zamowienia = relationship("Zamowienie", back_populates="forma_platnosci")


class FormaDostawy(Base):
    __tablename__ = "FormaDostawy"

    id_formy_dostawy = Column(Integer, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    dostawy = relationship("Dostawa", back_populates="forma_dostawy")


class FirmaDostawcza(Base):
    __tablename__ = "FirmaDostawcza"

    id_firmy = Column(Integer, primary_key=True)
    nazwa = Column(String(100), nullable=False)

    dostawy = relationship("Dostawa", back_populates="firma")


class Dostawa(Base):
    __tablename__ = "Dostawa"

    id_dostawy = Column(Integer, primary_key=True)

    id_formy_dostawy = Column(
        Integer,
        ForeignKey("FormaDostawy.id_formy_dostawy"),
        nullable=False
    )

    id_firmy = Column(
        Integer,
        ForeignKey("FirmaDostawcza.id_firmy"),
        nullable=False
    )

    forma_dostawy = relationship("FormaDostawy", back_populates="dostawy")
    firma = relationship("FirmaDostawcza", back_populates="dostawy")

    zamowienia = relationship("Zamowienie", back_populates="dostawa")


class Produkt(Base):
    __tablename__ = "Produkt"

    id_produktu = Column(Integer, primary_key=True)
    nazwa = Column(String(150), nullable=False)
    cena = Column(DECIMAL(10, 2), nullable=False)

    pozycje_zamowienia = relationship(
        "PozycjaZamowienia",
        back_populates="produkt"
    )

    magazyny = relationship(
        "ProduktMagazyn",
        back_populates="produkt"
    )


class Magazyn(Base):
    __tablename__ = "Magazyn"

    id_magazynu = Column(Integer, primary_key=True)
    nazwa = Column(String(100), nullable=False)

    produkty = relationship(
        "ProduktMagazyn",
        back_populates="magazyn"
    )


class ProduktMagazyn(Base):
    __tablename__ = "ProduktMagazyn"

    id = Column(Integer, primary_key=True)

    id_produktu = Column(
        Integer,
        ForeignKey("Produkt.id_produktu", ondelete="CASCADE"),
        nullable=False
    )

    id_magazynu = Column(
        Integer,
        ForeignKey("Magazyn.id_magazynu", ondelete="CASCADE"),
        nullable=False
    )

    ilosc = Column(Integer, nullable=False)

    produkt = relationship("Produkt", back_populates="magazyny")
    magazyn = relationship("Magazyn", back_populates="produkty")


class Zamowienie(Base):
    __tablename__ = "Zamowienie"

    id_zamowienia = Column(Integer, primary_key=True)

    data = Column(Date, nullable=False)

    id_statusu = Column(
        Integer,
        ForeignKey("Status.id_statusu"),
        nullable=False
    )

    id_pracownika = Column(
        Integer,
        ForeignKey("Pracownik.id_pracownika"),
        nullable=False
    )

    id_klienta = Column(
        Integer,
        ForeignKey("Klient.id_klienta"),
        nullable=False
    )

    id_formy_platnosci = Column(
        Integer,
        ForeignKey("FormaPlatnosci.id_formy_platnosci"),
        nullable=False
    )

    id_dostawy = Column(
        Integer,
        ForeignKey("Dostawa.id_dostawy"),
        nullable=False
    )

    status = relationship("Status", back_populates="zamowienia")
    pracownik = relationship("Pracownik", back_populates="zamowienia")
    klient = relationship("Klient", back_populates="zamowienia")
    forma_platnosci = relationship(
        "FormaPlatnosci",
        back_populates="zamowienia"
    )
    dostawa = relationship("Dostawa", back_populates="zamowienia")

    pozycje = relationship(
        "PozycjaZamowienia",
        back_populates="zamowienie"
    )


class PozycjaZamowienia(Base):
    __tablename__ = "PozycjaZamowienia"

    id = Column(Integer, primary_key=True)

    id_zamowienia = Column(
        Integer,
        ForeignKey("Zamowienie.id_zamowienia", ondelete="CASCADE"),
        nullable=False
    )

    id_produktu = Column(
        Integer,
        ForeignKey("Produkt.id_produktu"),
        nullable=False
    )

    ilosc = Column(Integer, nullable=False)

    cena_zakupu = Column(DECIMAL(10, 2), nullable=False)

    zamowienie = relationship(
        "Zamowienie",
        back_populates="pozycje"
    )

    produkt = relationship(
        "Produkt",
        back_populates="pozycje_zamowienia"
    )