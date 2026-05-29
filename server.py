import os
from datetime import date
from decimal import Decimal
from typing import Optional, Type

from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from db_connection import get_db
from tables import (
    Adres,
    Dostawa,
    FirmaDostawcza,
    FormaDostawy,
    FormaPlatnosci,
    Klient,
    Magazyn,
    PozycjaZamowienia,
    Pracownik,
    Produkt,
    ProduktMagazyn,
    Status,
    Zamowienie,
)

load_dotenv(find_dotenv())

tags_metadata = [
    {
        "name": "Działanie strony + API",
        "description": "Endpointy związane z działaniem strony i API."
    },
    {
        "name": "Pracownicy",
        "description": "Operacje związane z pracownikami."
    },
    {
        "name": "Statusy",
        "description": "Operacje na statusach zamówień."
    },
    {
        "name": "Dostawy",
        "description": "Zarządzanie dostawami."
    },
    {
        "name": "Firmy Dostawcze",
        "description": "Zarządzanie firmami dostawczymi."
    },
    {
        "name": "Formy Dostawy",
        "description": "Zarządzanie formami dostawy."
    },
    {
        "name": "Zamówienia",
        "description": "Operacje na zamówieniach."
    },
    {
        "name": "Formy Płatności",
        "description": "Zarządzanie formami płatności."
    },
    {
        "name": "Pozycje Zamówienia",
        "description": "Zarządzanie pozycjami zamówień."
    },
    {
        "name": "Produkty",
        "description": "Zarządzanie produktami."
    },
    {
        "name": "Produkty w Magazynie",
        "description": "Zarządzanie stanem produktów w magazynie."
    },
    {
        "name": "Magazyny",
        "description": "Zarządzanie magazynami."
    },
    {
        "name": "Klienci",
        "description": "Zarządzanie klientami."
    },
    {
        "name": "Adresy",
        "description": "Zarządzanie adresami klientów."
    }
]

app = FastAPI(
    title="zpsbAPI",
    description="API do obsługi zamówień",
    version="1.0.0",
    openapi_tags=tags_metadata
)

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("Brak wymaganej zmiennej środowiskowej: API_KEY")


def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Brak lub błędny klucz API")


def object_to_dict(obj):
    """Zwraca tylko kolumny SQLAlchemy, bez relacji i pól technicznych."""
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


def list_objects(db: Session, model: Type):
    return [object_to_dict(item) for item in db.query(model).all()]


def get_or_404(db: Session, model: Type, id_column, item_id: int, message: str):
    item = db.query(model).filter(id_column == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail=message)
    return item


def safe_commit(db: Session, error_detail: str = "Nie udało się zapisać zmian w bazie."):
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print("BŁĄD INTEGRALNOŚCI BAZY:", repr(e))
        raise HTTPException(
            status_code=400,
            detail="Nie udało się zapisać danych. Sprawdź, czy podane ID istnieją i czy dane są poprawne.",
        )
    except SQLAlchemyError as e:
        db.rollback()
        print("BŁĄD BAZY:", repr(e))
        raise HTTPException(status_code=500, detail=error_detail)


class PracownikChange(BaseModel):
    imie: str
    nazwisko: str
    stanowisko: Optional[str] = None


class StatusChange(BaseModel):
    nazwa: str


class DostawaChange(BaseModel):
    id_formy_dostawy: int = Field(..., gt=0)
    id_firmy: int = Field(..., gt=0)


class FirmaDostawczaChange(BaseModel):
    nazwa: str


class FormaDostawyChange(BaseModel):
    nazwa: str


class ZamowienieChange(BaseModel):
    data: date
    id_statusu: int = Field(..., gt=0)
    id_pracownika: int = Field(..., gt=0)
    id_klienta: int = Field(..., gt=0)
    id_formy_platnosci: int = Field(..., gt=0)
    id_dostawy: int = Field(..., gt=0)


class FormaPlatnosciChange(BaseModel):
    nazwa: str


class PozycjaZamowieniaChange(BaseModel):
    id_zamowienia: int = Field(..., gt=0)
    id_produktu: int = Field(..., gt=0)
    ilosc: int = Field(..., gt=0)
    cena_zakupu: Decimal = Field(..., gt=0)


class ProduktChange(BaseModel):
    nazwa: str
    cena: Decimal = Field(..., gt=0)


class ProduktMagazynChange(BaseModel):
    id_produktu: int = Field(..., gt=0)
    id_magazynu: int = Field(..., gt=0)
    ilosc: int = Field(..., ge=0)


class MagazynChange(BaseModel):
    nazwa: str


class KlientChange(BaseModel):
    imie: str
    nazwisko: str
    telefon: Optional[str] = None
    email: Optional[str] = None


class AdresChange(BaseModel):
    id_klienta: int = Field(..., gt=0)
    miasto: str
    ulica: str
    kod_pocztowy: str


@app.get(
        "/",
        tags=["Działanie strony + API"],
        summary="Strona główna",
        description="Strona informująca, czy API działa poprawnie."
    )
def home():
    return {"message": "API działa"}


@app.get(
        "/db-test",
        tags=["Działanie strony + API"],
        summary="Test połącznenia z bazą danych",
        description="Sprawdza poprawność połączenia z bazą danych." 
    )
    
def db_test(db: Session = Depends(get_db)):
    try:
        row = db.execute(text("SELECT current_database() AS database_name;")).mappings().first()
        return {"message": "Połączenie z bazą działa", "database": row["database_name"]}
    except SQLAlchemyError as e:
        print("BŁĄD POŁĄCZENIA Z BAZĄ:", repr(e))
        raise HTTPException(status_code=500, detail="Nie udało się połączyć z bazą danych.")


@app.get(
        "/dictionary-data", 
        dependencies=[Depends(check_api_key)],
        tags=["Działanie strony + API"],
    )
def get_dictionary_data(db: Session = Depends(get_db)):
    try:
        rows = db.execute(
            text(
                """
                SELECT 'status' AS tabela, id_statusu AS id, nazwa
                FROM integration.status

                UNION ALL
                SELECT 'pracownik' AS tabela, id_pracownika AS id, imie || ' ' || nazwisko AS nazwa
                FROM integration.pracownik

                UNION ALL
                SELECT 'klient' AS tabela, id_klienta AS id, imie || ' ' || nazwisko AS nazwa
                FROM integration.klient

                UNION ALL
                SELECT 'forma_platnosci' AS tabela, id_formy_platnosci AS id, nazwa
                FROM integration.formaplatnosci

                UNION ALL
                SELECT 'dostawa' AS tabela, id_dostawy AS id, 'Dostawa #' || id_dostawy AS nazwa
                FROM integration.dostawa

                ORDER BY tabela, id;
                """
            )
        ).mappings().all()
        return {"data": [dict(row) for row in rows]}
    except SQLAlchemyError as e:
        print("BŁĄD POBIERANIA DANYCH SŁOWNIKOWYCH:", repr(e))
        raise HTTPException(status_code=500, detail="Nie udało się pobrać danych słownikowych.")


@app.get("/pracownicy", dependencies=[Depends(check_api_key)], tags=["Pracownicy"],
        summary="Lista pracowników", description="Zwraca listę wszystkich pracowników w bazie danych.")
def get_pracownicy(db: Session = Depends(get_db)):
    return list_objects(db, Pracownik)


@app.get("/pracownik/{id}", dependencies=[Depends(check_api_key)], tags=["Pracownicy"],
        summary="Szczegóły pracownika", description="Zwraca szczegółowe informacje o pracowniku o podanym ID.")
def get_pracownik(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Pracownik, Pracownik.id_pracownika, id, "Brak pracownika o takim id"))


@app.post("/add_pracownik", status_code=201, dependencies=[Depends(check_api_key)], tags=["Pracownicy"], 
        summary="Dodaj pracownika", description="Tworzy nowego pracownika w bazie danych.")
def add_pracownik(pracownik: PracownikChange, db: Session = Depends(get_db)):
    item = Pracownik(**pracownik.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/edit_pracownik/{id}", dependencies=[Depends(check_api_key)], tags=["Pracownicy"],  
        summary="Edytuj pracownika", description="Aktualizuje dane istniejącego pracownika o podanym ID.")  
def edit_pracownik(id: int, pracownik: PracownikChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Pracownik, Pracownik.id_pracownika, id, "Brak pracownika o takim id")
    for key, value in pracownik.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/del_pracownik/{id}", dependencies=[Depends(check_api_key)], tags=["Pracownicy"],
        summary="Usuń pracownika", description="Usuwa pracownika o podanym ID z bazy danych.")
def delete_pracownik(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Pracownik, Pracownik.id_pracownika, id, "Brak pracownika o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto pracownika {id}"}


@app.get("/statusy", dependencies=[Depends(check_api_key)], tags=["Statusy"],
        summary="Lista statusów", description="Zwraca listę wszystkich statusów zamówień w bazie danych.")
def get_statusy(db: Session = Depends(get_db)):
    return list_objects(db, Status)


@app.get("/status/{id}", dependencies=[Depends(check_api_key)], tags=["Statusy"],
        summary="Szczegóły statusu", description="Zwraca szczegółowe informacje o statusie o podanym ID.")
def get_status(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Status, Status.id_statusu, id, "Brak statusu o takim id"))


@app.post("/add_status", status_code=201, dependencies=[Depends(check_api_key)], tags=["Statusy"],
        summary="Dodaj status", description="Tworzy nowy status zamówienia w bazie danych.")
def add_status(status: StatusChange, db: Session = Depends(get_db)):
    item = Status(**status.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/edit_status/{id}", dependencies=[Depends(check_api_key)], tags=["Statusy"],
        summary="Edytuj status", description="Aktualizuje dane istniejącego statusu o podanym ID.")
def edit_status(id: int, status: StatusChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Status, Status.id_statusu, id, "Brak statusu o takim id")
    item.nazwa = status.nazwa
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/del_status/{id}", dependencies=[Depends(check_api_key)], tags=["Statusy"],
        summary="Usuń status", description="Usuwa status o podanym ID z bazy danych.")
def delete_status(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Status, Status.id_statusu, id, "Brak statusu o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto status {id}"}


@app.get("/dostawy", dependencies=[Depends(check_api_key)], tags=["Dostawy"],
        summary="Lista dostaw", description="Zwraca listę wszystkich dostaw w bazie danych.")
def get_dostawy(db: Session = Depends(get_db)):
    return list_objects(db, Dostawa)


@app.get("/dostawa/{id}", dependencies=[Depends(check_api_key)], tags=["Dostawy"],
        summary="Szczegóły dostawy", description="Zwraca szczegółowe informacje o dostawie o podanym ID.")
def get_dostawa(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Dostawa, Dostawa.id_dostawy, id, "Brak dostawy o takim id"))


@app.post("/add_dostawa", status_code=201, dependencies=[Depends(check_api_key)], tags=["Dostawy"],
        summary="Dodaj dostawę", description="Tworzy nową dostawę w bazie danych.")
def add_dostawa(dostawa: DostawaChange, db: Session = Depends(get_db)):
    item = Dostawa(**dostawa.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/edit_dostawa/{id}", dependencies=[Depends(check_api_key)], tags=["Dostawy"],
        summary="Edytuj dostawę", description="Aktualizuje dane istniejącej dostawy o podanym ID.")
def edit_dostawa(id: int, dostawa: DostawaChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Dostawa, Dostawa.id_dostawy, id, "Brak dostawy o takim id")
    item.id_formy_dostawy = dostawa.id_formy_dostawy
    item.id_firmy = dostawa.id_firmy
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/del_dostawa/{id}", dependencies=[Depends(check_api_key)], tags=["Dostawy"],
        summary="Usuń dostawę", description="Usuwa dostawę o podanym ID z bazy danych.")
def delete_dostawa(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Dostawa, Dostawa.id_dostawy, id, "Brak dostawy o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto dostawę {id}"}


@app.get("/firmyDostawcze", dependencies=[Depends(check_api_key)], tags=["Firmy Dostawcze"],
        summary="Lista firm dostawczych", description="Zwraca listę wszystkich firm dostawczych w bazie danych.")
def get_firmy_dostawcze(db: Session = Depends(get_db)):
    return list_objects(db, FirmaDostawcza)


@app.get("/firmaDostawcza/{id}", dependencies=[Depends(check_api_key)], tags=["Firmy Dostawcze"],
        summary="Szczegóły firmy dostawczej", description="Zwraca szczegółowe informacje o firmie dostawczej o podanym ID.")
def get_firma_dostawcza(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, FirmaDostawcza, FirmaDostawcza.id_firmy, id, "Brak firmy dostawczej o takim id"))


@app.post("/add_firmaDostawcza", status_code=201, dependencies=[Depends(check_api_key)], tags=["Firmy Dostawcze"],
        summary="Dodaj firmę dostawczą", description="Tworzy nową firmę dostawczą w bazie danych.")
def add_firma_dostawcza(firma: FirmaDostawczaChange, db: Session = Depends(get_db)):
    item = FirmaDostawcza(**firma.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/edit_firmaDostawcza/{id}", dependencies=[Depends(check_api_key)], tags=["Firmy Dostawcze"],
        summary="Edytuj firmę dostawczą", description="Aktualizuje dane istniejącej firmy dostawczej o podanym ID.")
def edit_firma_dostawcza(id: int, firma: FirmaDostawczaChange, db: Session = Depends(get_db)):
    item = get_or_404(db, FirmaDostawcza, FirmaDostawcza.id_firmy, id, "Brak firmy dostawczej o takim id")
    item.nazwa = firma.nazwa
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/del_firmaDostawcza/{id}", dependencies=[Depends(check_api_key)], tags=["Firmy Dostawcze"],
        summary="Usuń firmę dostawczą", description="Usuwa firmę dostawczą o podanym ID z bazy danych.")
def delete_firma_dostawcza(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, FirmaDostawcza, FirmaDostawcza.id_firmy, id, "Brak firmy dostawczej o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto firmę dostawczą {id}"}


@app.get("/formyDostawy", dependencies=[Depends(check_api_key)], tags=["Formy Dostawy"],
        summary="Lista form dostawy", description="Zwraca listę wszystkich form dostawy w bazie danych.")
def get_formy_dostawy(db: Session = Depends(get_db)):
    return list_objects(db, FormaDostawy)


@app.get("/formaDostawy/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Dostawy"],
        summary="Szczegóły formy dostawy", description="Zwraca szczegółowe informacje o formie dostawy o podanym ID.")
def get_forma_dostawy(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, FormaDostawy, FormaDostawy.id_formy_dostawy, id, "Brak formy dostawy o takim id"))


@app.post("/add_formaDostawy", status_code=201, dependencies=[Depends(check_api_key)], tags=["Formy Dostawy"],
        summary="Dodaj formę dostawy", description="Tworzy nową formę dostawy w bazie danych.")
def add_forma_dostawy(forma: FormaDostawyChange, db: Session = Depends(get_db)):
    item = FormaDostawy(**forma.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/edit_formaDostawy/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Dostawy"],
        summary="Edytuj formę dostawy", description="Aktualizuje dane istniejącej formy dostawy o podanym ID.")
def edit_forma_dostawy(id: int, forma: FormaDostawyChange, db: Session = Depends(get_db)):
    item = get_or_404(db, FormaDostawy, FormaDostawy.id_formy_dostawy, id, "Brak formy dostawy o takim id")
    item.nazwa = forma.nazwa
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/del_formaDostawy/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Dostawy"],
        summary="Usuń formę dostawy", description="Usuwa formę dostawy o podanym ID z bazy danych.")
def delete_forma_dostawy(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, FormaDostawy, FormaDostawy.id_formy_dostawy, id, "Brak formy dostawy o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto formę dostawy {id}"}


@app.get("/zamowienia", dependencies=[Depends(check_api_key)], tags=["Zamówienia"],
        summary="Lista zamówień", description="Zwraca listę wszystkich zamówień w bazie danych.")
def get_zamowienia(db: Session = Depends(get_db)):
    return list_objects(db, Zamowienie)


@app.get("/zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Zamówienia"],
        summary="Szczegóły zamówienia", description="Zwraca szczegółowe informacje o zamówieniu o podanym ID.")
def get_zamowienie(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Zamowienie, Zamowienie.id_zamowienia, id, "Brak zamówienia o takim id"))


@app.post("/zamowienia", status_code=201, dependencies=[Depends(check_api_key)], tags=["Zamówienia"],
        summary="Dodaj zamówienie", description="Tworzy nowe zamówienie.")
def add_zamowienie(zam: ZamowienieChange, db: Session = Depends(get_db)):
    item = Zamowienie(**zam.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Zamówienia"],
        summary="Edytuj zamówienie", description="Aktualizuje dane istniejącego zamówienia o podanym ID.")
def edit_zamowienie(id: int, zam: ZamowienieChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Zamowienie, Zamowienie.id_zamowienia, id, "Brak zamówienia o takim id")
    for key, value in zam.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Zamówienia"],
        summary="Usuń zamówienie", description="Usuwa zamówienie o podanym ID z bazy danych.")
def delete_zamowienie(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Zamowienie, Zamowienie.id_zamowienia, id, "Brak zamówienia o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto zamówienie {id}"}


@app.get("/formy_platnosci", dependencies=[Depends(check_api_key)], tags=["Formy Płatności"],
        summary="Lista form płatności", description="Zwraca listę dostępnych form płatności.")
def get_formy_platnosci(db: Session = Depends(get_db)):
    return list_objects(db, FormaPlatnosci)


@app.get("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Płatności"],
        summary="Szczegóły formy płatności", description="Zwraca szczegółowe informacje o formie płatności o podanym ID.")
def get_forma_platnosci(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, FormaPlatnosci, FormaPlatnosci.id_formy_platnosci, id, "Brak formy płatności o takim id"))


@app.post("/formy_platnosci", status_code=201, dependencies=[Depends(check_api_key)], tags=["Formy Płatności"],
        summary="Dodaj formę płatności", description="Tworzy nową formę płatności w bazie danych.")
def add_forma_platnosci(forma: FormaPlatnosciChange, db: Session = Depends(get_db)):
    item = FormaPlatnosci(**forma.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Płatności"],
        summary="Edytuj formę płatności", description="Aktualizuje dane istniejącej formy płatności o podanym ID.")
def edit_forma_platnosci(id: int, forma: FormaPlatnosciChange, db: Session = Depends(get_db)):
    item = get_or_404(db, FormaPlatnosci, FormaPlatnosci.id_formy_platnosci, id, "Brak formy płatności o takim id")
    item.nazwa = forma.nazwa
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)], tags=["Formy Płatności"],
        summary="Usuń formę płatności", description="Usuwa formę płatności o podanym ID z bazy danych.")
def delete_forma_platnosci(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, FormaPlatnosci, FormaPlatnosci.id_formy_platnosci, id, "Brak formy płatności o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto formę płatności {id}"}


@app.get("/pozycje_zamowienia", dependencies=[Depends(check_api_key)], tags=["Pozycje Zamówienia"],
        summary="Lista pozycji zamówienia", description="Zwraca listę wszystkich pozycji zamówień w bazie danych.")
def get_pozycje_zamowienia(db: Session = Depends(get_db)):
    return list_objects(db, PozycjaZamowienia)


@app.get("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Pozycje Zamówienia"],
        summary="Szczegóły pozycji zamówienia", description="Zwraca szczegółowe informacje o pozycji zamówienia o podanym ID.")
def get_pozycja_zamowienia(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, PozycjaZamowienia, PozycjaZamowienia.id, id, "Brak pozycji o takim id"))


@app.post("/pozycje_zamowienia", status_code=201, dependencies=[Depends(check_api_key)], tags=["Pozycje Zamówienia"],
        summary="Dodaj pozycję zamówienia", description="Tworzy nową pozycję zamówienia w bazie danych.")
def add_pozycja_zamowienia(poz: PozycjaZamowieniaChange, db: Session = Depends(get_db)):
    item = PozycjaZamowienia(**poz.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Pozycje Zamówienia"],
        summary="Edytuj pozycję zamówienia", description="Aktualizuje dane istniejącej pozycji zamówienia o podanym ID.")
def edit_pozycja_zamowienia(id: int, poz: PozycjaZamowieniaChange, db: Session = Depends(get_db)):
    item = get_or_404(db, PozycjaZamowienia, PozycjaZamowienia.id, id, "Brak pozycji o takim id")
    for key, value in poz.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)], tags=["Pozycje Zamówienia"],
        summary="Usuń pozycję zamówienia", description="Usuwa pozycję zamówienia o podanym ID z bazy danych.")
def delete_pozycja_zamowienia(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, PozycjaZamowienia, PozycjaZamowienia.id, id, "Brak pozycji o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto pozycję {id}"}


@app.get("/produkty", dependencies=[Depends(check_api_key)], tags=["Produkty"],
        summary="Lista produktów", description="Zwraca listę wszystkich produktów w bazie danych.")
def get_produkty(db: Session = Depends(get_db)):
    return list_objects(db, Produkt)


@app.get("/produkty/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty"],
        summary="Szczegóły produktu", description="Zwraca szczegółowe informacje o produkcie o podanym ID.")
def get_produkt(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Produkt, Produkt.id_produktu, id, "Brak produktu o takim id"))


@app.post("/produkty", status_code=201, dependencies=[Depends(check_api_key)], tags=["Produkty"],
        summary="Dodaj produkt", description="Tworzy nowy produkt w bazie danych.")
def add_produkt(prod: ProduktChange, db: Session = Depends(get_db)):
    item = Produkt(**prod.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/produkty/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty"],
        summary="Edytuj produkt", description="Aktualizuje dane istniejącego produktu o podanym ID.")
def edit_produkt(id: int, prod: ProduktChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Produkt, Produkt.id_produktu, id, "Brak produktu o takim id")
    item.nazwa = prod.nazwa
    item.cena = prod.cena
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/produkty/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty"],
        summary="Usuń produkt", description="Usuwa produkt o podanym ID z bazy danych.")
def delete_produkt(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Produkt, Produkt.id_produktu, id, "Brak produktu o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto produkt {id}"}


@app.get("/produktMagazyn", dependencies=[Depends(check_api_key)], tags=["Produkty w Magazynie"],
        summary="Lista produktów w magazynie", description="Zwraca listę wszystkich produktów w magazynie.")
def get_produkty_magazyn(db: Session = Depends(get_db)):
    return list_objects(db, ProduktMagazyn)


@app.get("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty w Magazynie"],
        summary="Szczegóły produktu w magazynie", description="Zwraca szczegółowe informacje o produkcie w magazynie o podanym ID.")
def get_produkt_magazyn(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, ProduktMagazyn, ProduktMagazyn.id, id, "Brak produktu w magazynie o takim id"))


@app.post("/produktMagazyn", status_code=201, dependencies=[Depends(check_api_key)], tags=["Produkty w Magazynie"],
        summary="Dodaj produkt do magazynu", description="Tworzy nowy produkt w magazynie.")
def add_produkt_magazyn(mag: ProduktMagazynChange, db: Session = Depends(get_db)):
    item = ProduktMagazyn(**mag.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty w Magazynie"],
        summary="Edytuj produkt w magazynie", description="Aktualizuje dane istniejącego produktu w magazynie o podanym ID.")
def edit_produkt_magazyn(id: int, mag: ProduktMagazynChange, db: Session = Depends(get_db)):
    item = get_or_404(db, ProduktMagazyn, ProduktMagazyn.id, id, "Brak produktu w magazynie o takim id")
    for key, value in mag.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)], tags=["Produkty w Magazynie"],
        summary="Usuń produkt z magazynu", description="Usuwa produkt o podanym ID z magazynu.")
def delete_produkt_magazyn(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, ProduktMagazyn, ProduktMagazyn.id, id, "Brak produktu w magazynie o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto produkt z magazynu {id}"}


@app.get("/magazyny", dependencies=[Depends(check_api_key)], tags=["Magazyny"],
        summary="Lista magazynów", description="Zwraca listę wszystkich magazynów.")
def get_magazyny(db: Session = Depends(get_db)):
    return list_objects(db, Magazyn)


@app.get("/magazyny/{id}", dependencies=[Depends(check_api_key)], tags=["Magazyny"],
        summary="Szczegóły magazynu", description="Zwraca szczegółowe informacje o magazynie o podanym ID.")
def get_magazyn(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Magazyn, Magazyn.id_magazynu, id, "Brak magazynu o takim id"))


@app.post("/magazyny", status_code=201, dependencies=[Depends(check_api_key)], tags=["Magazyny"],
        summary="Dodaj magazyn", description="Tworzy nowy magazyn.")
def add_magazyn(mag: MagazynChange, db: Session = Depends(get_db)):
    item = Magazyn(**mag.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/magazyny/{id}", dependencies=[Depends(check_api_key)], tags=["Magazyny"],
        summary="Edytuj magazyn", description="Aktualizuje dane istniejącego magazynu o podanym ID.")
def edit_magazyn(id: int, mag: MagazynChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Magazyn, Magazyn.id_magazynu, id, "Brak magazynu o takim id")
    item.nazwa = mag.nazwa
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/magazyny/{id}", dependencies=[Depends(check_api_key)], tags=["Magazyny"],
        summary="Usuń magazyn", description="Usuwa magazyn o podanym ID.")
def delete_magazyn(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Magazyn, Magazyn.id_magazynu, id, "Brak magazynu o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto magazyn {id}"}


@app.get("/klienci", dependencies=[Depends(check_api_key)], tags=["Klienci"],
        summary="Lista klientów", description="Zwraca listę wszystkich klientów w bazie danych.")
def get_klienci(db: Session = Depends(get_db)):
    return list_objects(db, Klient)


@app.get("/klienci/{id}", dependencies=[Depends(check_api_key)], tags=["Klienci"],
        summary="Szczegóły klienta", description="Zwraca szczegółowe informacje o kliencie o podanym ID.")
def get_klient(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Klient, Klient.id_klienta, id, "Brak klienta o takim id"))


@app.post("/klienci", status_code=201, dependencies=[Depends(check_api_key)], tags=["Klienci"],
        summary="Dodaj klienta", description="Tworzy nowego klienta.")
def add_klient(klient: KlientChange, db: Session = Depends(get_db)):
    item = Klient(**klient.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/klienci/{id}", dependencies=[Depends(check_api_key)], tags=["Klienci"],
        summary="Edytuj klienta", description="Aktualizuje dane istniejącego klienta o podanym ID.")
def edit_klient(id: int, klient: KlientChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Klient, Klient.id_klienta, id, "Brak klienta o takim id")
    for key, value in klient.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/klienci/{id}", dependencies=[Depends(check_api_key)], tags=["Klienci"],
        summary="Usuń klienta", description="Usuwa klienta o podanym ID.")
def delete_klient(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Klient, Klient.id_klienta, id, "Brak klienta o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto klienta {id}"}


@app.get("/adresy", dependencies=[Depends(check_api_key)], tags=["Adresy"],
        summary="Lista adresów", description="Zwraca listę wszystkich adresów w bazie danych.")
def get_adresy(db: Session = Depends(get_db)):
    return list_objects(db, Adres)


@app.get("/adresy/{id}", dependencies=[Depends(check_api_key)], tags=["Adresy"],
        summary="Szczegóły adresu", description="Zwraca szczegółowe informacje o adresie o podanym ID.")
def get_adres(id: int, db: Session = Depends(get_db)):
    return object_to_dict(get_or_404(db, Adres, Adres.id_adresu, id, "Brak adresu o takim id"))


@app.post("/adresy", status_code=201, dependencies=[Depends(check_api_key)], tags=["Adresy"],
        summary="Dodaj adres", description="Tworzy nowy adres.")
def add_adres(adres: AdresChange, db: Session = Depends(get_db)):
    item = Adres(**adres.model_dump())
    db.add(item)
    safe_commit(db)
    db.refresh(item)
    return object_to_dict(item)


@app.put("/adresy/{id}", dependencies=[Depends(check_api_key)], tags=["Adresy"],
        summary="Edytuj adres", description="Aktualizuje dane istniejącego adresu o podanym ID.")
def edit_adres(id: int, adres: AdresChange, db: Session = Depends(get_db)):
    item = get_or_404(db, Adres, Adres.id_adresu, id, "Brak adresu o takim id")
    for key, value in adres.model_dump().items():
        setattr(item, key, value)
    safe_commit(db)
    return object_to_dict(item)


@app.delete("/adresy/{id}", dependencies=[Depends(check_api_key)], tags=["Adresy"],
        summary="Usuń adres", description="Usuwa adres o podanym ID.")
def delete_adres(id: int, db: Session = Depends(get_db)):
    item = get_or_404(db, Adres, Adres.id_adresu, id, "Brak adresu o takim id")
    db.delete(item)
    safe_commit(db)
    return {"message": f"Usunięto adres {id}"}
