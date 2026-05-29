from sqlalchemy import BigInteger, Column, Date, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db_connection import Base

SCHEMA = "integration"


class Klient(Base):
    __tablename__ = "klient"
    __table_args__ = {"schema": SCHEMA}

    id_klienta = Column(BigInteger, primary_key=True)
    imie = Column(String(100), nullable=False)
    nazwisko = Column(String(100), nullable=False)
    telefon = Column(String(30))
    email = Column(String(150))

    adresy = relationship("Adres", back_populates="klient")
    zamowienia = relationship("Zamowienie", back_populates="klient")


class Adres(Base):
    __tablename__ = "adres"
    __table_args__ = {"schema": SCHEMA}

    id_adresu = Column(BigInteger, primary_key=True)
    id_klienta = Column(
        BigInteger,
        ForeignKey("integration.klient.id_klienta", ondelete="CASCADE"),
        nullable=False,
    )
    miasto = Column(String(100), nullable=False)
    ulica = Column(String(150), nullable=False)
    kod_pocztowy = Column(String(20), nullable=False)

    klient = relationship("Klient", back_populates="adresy")


class Pracownik(Base):
    __tablename__ = "pracownik"
    __table_args__ = {"schema": SCHEMA}

    id_pracownika = Column(BigInteger, primary_key=True)
    imie = Column(String(100), nullable=False)
    nazwisko = Column(String(100), nullable=False)
    stanowisko = Column(String(100))

    zamowienia = relationship("Zamowienie", back_populates="pracownik")


class Status(Base):
    __tablename__ = "status"
    __table_args__ = {"schema": SCHEMA}

    id_statusu = Column(BigInteger, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    zamowienia = relationship("Zamowienie", back_populates="status")


class FormaPlatnosci(Base):
    __tablename__ = "formaplatnosci"
    __table_args__ = {"schema": SCHEMA}

    id_formy_platnosci = Column(BigInteger, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    zamowienia = relationship("Zamowienie", back_populates="forma_platnosci")


class FormaDostawy(Base):
    __tablename__ = "formadostawy"
    __table_args__ = {"schema": SCHEMA}

    id_formy_dostawy = Column(BigInteger, primary_key=True)
    nazwa = Column(String(50), nullable=False)

    dostawy = relationship("Dostawa", back_populates="forma_dostawy")


class FirmaDostawcza(Base):
    __tablename__ = "firmadostawcza"
    __table_args__ = {"schema": SCHEMA}

    id_firmy = Column(BigInteger, primary_key=True)
    nazwa = Column(String(100), nullable=False)

    dostawy = relationship("Dostawa", back_populates="firma")


class Dostawa(Base):
    __tablename__ = "dostawa"
    __table_args__ = {"schema": SCHEMA}

    id_dostawy = Column(BigInteger, primary_key=True)
    id_formy_dostawy = Column(
        BigInteger,
        ForeignKey("integration.formadostawy.id_formy_dostawy"),
        nullable=False,
    )
    id_firmy = Column(
        BigInteger,
        ForeignKey("integration.firmadostawcza.id_firmy"),
        nullable=False,
    )

    forma_dostawy = relationship("FormaDostawy", back_populates="dostawy")
    firma = relationship("FirmaDostawcza", back_populates="dostawy")
    zamowienia = relationship("Zamowienie", back_populates="dostawa")


class Produkt(Base):
    __tablename__ = "produkt"
    __table_args__ = {"schema": SCHEMA}

    id_produktu = Column(BigInteger, primary_key=True)
    nazwa = Column(String(150), nullable=False)
    cena = Column(DECIMAL(10, 2), nullable=False)

    pozycje_zamowienia = relationship("PozycjaZamowienia", back_populates="produkt")
    magazyny = relationship("ProduktMagazyn", back_populates="produkt")


class Magazyn(Base):
    __tablename__ = "magazyn"
    __table_args__ = {"schema": SCHEMA}

    id_magazynu = Column(BigInteger, primary_key=True)
    nazwa = Column(String(100), nullable=False)

    produkty = relationship("ProduktMagazyn", back_populates="magazyn")


class ProduktMagazyn(Base):
    __tablename__ = "produktmagazyn"
    __table_args__ = {"schema": SCHEMA}

    id = Column(BigInteger, primary_key=True)
    id_produktu = Column(
        BigInteger,
        ForeignKey("integration.produkt.id_produktu", ondelete="CASCADE"),
        nullable=False,
    )
    id_magazynu = Column(
        BigInteger,
        ForeignKey("integration.magazyn.id_magazynu", ondelete="CASCADE"),
        nullable=False,
    )
    ilosc = Column(Integer, nullable=False)

    produkt = relationship("Produkt", back_populates="magazyny")
    magazyn = relationship("Magazyn", back_populates="produkty")


class Zamowienie(Base):
    __tablename__ = "zamowienie"
    __table_args__ = {"schema": SCHEMA}

    id_zamowienia = Column(BigInteger, primary_key=True)
    data = Column(Date, nullable=False)
    id_statusu = Column(
        BigInteger,
        ForeignKey("integration.status.id_statusu"),
        nullable=False,
    )
    id_pracownika = Column(
        BigInteger,
        ForeignKey("integration.pracownik.id_pracownika"),
        nullable=False,
    )
    id_klienta = Column(
        BigInteger,
        ForeignKey("integration.klient.id_klienta"),
        nullable=False,
    )
    id_formy_platnosci = Column(
        BigInteger,
        ForeignKey("integration.formaplatnosci.id_formy_platnosci"),
        nullable=False,
    )
    id_dostawy = Column(
        BigInteger,
        ForeignKey("integration.dostawa.id_dostawy"),
        nullable=False,
    )

    status = relationship("Status", back_populates="zamowienia")
    pracownik = relationship("Pracownik", back_populates="zamowienia")
    klient = relationship("Klient", back_populates="zamowienia")
    forma_platnosci = relationship("FormaPlatnosci", back_populates="zamowienia")
    dostawa = relationship("Dostawa", back_populates="zamowienia")
    pozycje = relationship("PozycjaZamowienia", back_populates="zamowienie")


class PozycjaZamowienia(Base):
    __tablename__ = "pozycjazamowienia"
    __table_args__ = {"schema": SCHEMA}

    id = Column(BigInteger, primary_key=True)
    id_zamowienia = Column(
        BigInteger,
        ForeignKey("integration.zamowienie.id_zamowienia", ondelete="CASCADE"),
        nullable=False,
    )
    id_produktu = Column(
        BigInteger,
        ForeignKey("integration.produkt.id_produktu"),
        nullable=False,
    )
    ilosc = Column(Integer, nullable=False)
    cena_zakupu = Column(DECIMAL(10, 2), nullable=False)

    zamowienie = relationship("Zamowienie", back_populates="pozycje")
    produkt = relationship("Produkt", back_populates="pozycje_zamowienia")
