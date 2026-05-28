import os
from datetime import date

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db_connection import get_db


load_dotenv(find_dotenv())


app = FastAPI(
    title="zpsbAPI",
    description="API do obsługi zamówień",
    version="1.0.0"
)


API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("Brak wymaganej zmiennej środowiskowej: API_KEY")


def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Brak lub błędny klucz API"
        )

class OrderCreate(BaseModel):
    data: date
    id_statusu: int = Field(..., gt=0)
    id_pracownika: int = Field(..., gt=0)
    id_klienta: int = Field(..., gt=0)
    id_formy_platnosci: int = Field(..., gt=0)
    id_dostawy: int = Field(..., gt=0)


@app.get("/")
def home():
    return {"message": "API działa"}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT current_database() AS database_name;"))
        row = result.mappings().first()

        return {
            "message": "Połączenie z bazą działa",
            "database": row["database_name"]
        }

    except SQLAlchemyError as e:
        print("BŁĄD POŁĄCZENIA Z BAZĄ:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Nie udało się połączyć z bazą danych."
        )


@app.get("/dictionary-data", dependencies=[Depends(check_api_key)])
def get_dictionary_data(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
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
            """)
        )

        rows = result.mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except SQLAlchemyError as e:
        print("BŁĄD POBIERANIA DANYCH SŁOWNIKOWYCH:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Nie udało się pobrać danych słownikowych."
        )


@app.post("/orders", dependencies=[Depends(check_api_key)])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                INSERT INTO integration.zamowienie (
                    data,
                    id_statusu,
                    id_pracownika,
                    id_klienta,
                    id_formy_platnosci,
                    id_dostawy
                )
                VALUES (
                    :data,
                    :id_statusu,
                    :id_pracownika,
                    :id_klienta,
                    :id_formy_platnosci,
                    :id_dostawy
                )
                RETURNING id_zamowienia;
            """),
            {
                "data": order.data,
                "id_statusu": order.id_statusu,
                "id_pracownika": order.id_pracownika,
                "id_klienta": order.id_klienta,
                "id_formy_platnosci": order.id_formy_platnosci,
                "id_dostawy": order.id_dostawy,
            }
        )

        new_order_id = result.scalar()
        db.commit()

        return {
            "message": "Dodano zamówienie do bazy",
            "id_zamowienia": new_order_id
        }

    except SQLAlchemyError as e:
        db.rollback()
        print("BŁĄD DODAWANIA ZAMÓWIENIA:", repr(e))
        raise HTTPException(
            status_code=400,
            detail="Nie udało się dodać zamówienia. Sprawdź terminal uvicorn."
        )


@app.get("/orders", dependencies=[Depends(check_api_key)])
def get_orders(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                SELECT
                    z.id_zamowienia,
                    z.data,
                    z.id_statusu,
                    s.nazwa AS status,
                    z.id_pracownika,
                    p.imie || ' ' || p.nazwisko AS pracownik,
                    z.id_klienta,
                    k.imie || ' ' || k.nazwisko AS klient,
                    z.id_formy_platnosci,
                    fp.nazwa AS forma_platnosci,
                    z.id_dostawy
                FROM integration.zamowienie z
                JOIN integration.status s
                    ON s.id_statusu = z.id_statusu
                JOIN integration.pracownik p
                    ON p.id_pracownika = z.id_pracownika
                JOIN integration.klient k
                    ON k.id_klienta = z.id_klienta
                JOIN integration.formaplatnosci fp
                    ON fp.id_formy_platnosci = z.id_formy_platnosci
                JOIN integration.dostawa d
                    ON d.id_dostawy = z.id_dostawy
                ORDER BY z.id_zamowienia;
            """)
        )

        orders = result.mappings().all()

        return {
            "orders": [dict(order) for order in orders]
        }

    except SQLAlchemyError as e:
        print("BŁĄD POBIERANIA ZAMÓWIEŃ:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Nie udało się pobrać zamówień."
        )


@app.get("/orders/{id}", dependencies=[Depends(check_api_key)])
def get_order(id: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                SELECT
                    z.id_zamowienia,
                    z.data,
                    z.id_statusu,
                    s.nazwa AS status,
                    z.id_pracownika,
                    p.imie || ' ' || p.nazwisko AS pracownik,
                    z.id_klienta,
                    k.imie || ' ' || k.nazwisko AS klient,
                    z.id_formy_platnosci,
                    fp.nazwa AS forma_platnosci,
                    z.id_dostawy
                FROM integration.zamowienie z
                JOIN integration.status s
                    ON s.id_statusu = z.id_statusu
                JOIN integration.pracownik p
                    ON p.id_pracownika = z.id_pracownika
                JOIN integration.klient k
                    ON k.id_klienta = z.id_klienta
                JOIN integration.formaplatnosci fp
                    ON fp.id_formy_platnosci = z.id_formy_platnosci
                JOIN integration.dostawa d
                    ON d.id_dostawy = z.id_dostawy
                WHERE z.id_zamowienia = :id;
            """),
            {"id": id}
        )

        order = result.mappings().first()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Nie znaleziono zamówienia"
            )

        return dict(order)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        print("BŁĄD POBIERANIA ZAMÓWIENIA:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Nie udało się pobrać zamówienia."
        )


@app.put("/orders/{id}", dependencies=[Depends(check_api_key)])
def update_order(id: int, order: OrderCreate, db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                UPDATE integration.zamowienie
                SET
                    data = :data,
                    id_statusu = :id_statusu,
                    id_pracownika = :id_pracownika,
                    id_klienta = :id_klienta,
                    id_formy_platnosci = :id_formy_platnosci,
                    id_dostawy = :id_dostawy
                WHERE id_zamowienia = :id
                RETURNING id_zamowienia;
            """),
            {
                "id": id,
                "data": order.data,
                "id_statusu": order.id_statusu,
                "id_pracownika": order.id_pracownika,
                "id_klienta": order.id_klienta,
                "id_formy_platnosci": order.id_formy_platnosci,
                "id_dostawy": order.id_dostawy,
            }
        )

        updated_id = result.scalar()

        if updated_id is None:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail="Nie znaleziono zamówienia"
            )

        db.commit()

        return {
            "message": "Edytowano zamówienie",
            "id_zamowienia": updated_id
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("BŁĄD EDYCJI ZAMÓWIENIA:", repr(e))
        raise HTTPException(
            status_code=400,
            detail="Nie udało się edytować zamówienia. Sprawdź terminal uvicorn."
        )


@app.delete("/orders/{id}", dependencies=[Depends(check_api_key)])
def delete_order(id: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                DELETE FROM integration.zamowienie
                WHERE id_zamowienia = :id
                RETURNING id_zamowienia;
            """),
            {"id": id}
        )

        deleted_id = result.scalar()

        if deleted_id is None:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail="Nie znaleziono zamówienia"
            )

        db.commit()

        return {
            "message": "Usunięto zamówienie",
            "id_zamowienia": deleted_id
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("BŁĄD USUWANIA ZAMÓWIENIA:", repr(e))
        raise HTTPException(
            status_code=400,
            detail="Nie udało się usunąć zamówienia. Sprawdź terminal uvicorn."
        )