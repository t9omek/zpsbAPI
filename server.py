from fastapi import FastAPI, Header, HTTPException, Depends

# Do db ###################
from db_connection import get_db
from tables import Pracownik, Status,Dostawa,FirmaDostawcza
from sqlalchemy.orm import Session
from pydantic import BaseModel
###########################

app = FastAPI()

API_KEY = "tajny-klucz-123"

def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Brak lub błędny klucz API")

@app.get("/")
def home():
    return {"message": "API działa"}

@app.post("/orders", dependencies=[Depends(check_api_key)])
def create_order():
    return {"message": "Dodano zamówienie"}

@app.put("/orders/{id}", dependencies=[Depends(check_api_key)])
def update_order(id: int):
    return {"message": f"Edytowano zamówienie {id}"}

@app.delete("/orders/{id}", dependencies=[Depends(check_api_key)])
def delete_order(id: int):
    return {"message": f"Usunięto zamówienie {id}"}


####################
# API PRAWA STRONA #

class Pracownik_Change(BaseModel):
    imie: str
    nazwisko: str
    stanowisko:str


@app.get("/pracownicy", dependencies=[Depends(check_api_key)])
def pracownicy(db: Session = Depends(get_db)):
    response = db.query(Pracownik).all()
    return response

@app.get("/pracownik/{id}",dependencies=[Depends(check_api_key)])
def get_pracownik(id:int, db: Session = Depends(get_db)):
    response = db.query(Pracownik).filter(Pracownik.id_pracownika == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak pracownika o takim id")
    return response

@app.post("/add_pracownik",status_code=201,dependencies=[Depends(check_api_key)])
def add_pracownik(pracownik:Pracownik_Change, db: Session = Depends(get_db)):
    pracownik_db=Pracownik(imie=pracownik.imie, nazwisko=pracownik.nazwisko)
    db.add(pracownik_db)
    db.commit()
    db.refresh(pracownik_db)
    return pracownik_db

@app.delete("/del_pracownik/{id}",dependencies=[Depends(check_api_key)],responses={404: {'description': 'Brak pracownika o takim id'}})
def del_pracownik(id:int, db: Session = Depends(get_db)):
    response= db.query(Pracownik).filter(Pracownik.id_pracownika == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak pracownika o takim id")
    db.delete(response)
    db.commit()
    return {"message": f"Usunięto pracownika {id}"}

@app.put("/edit_pracownik/{id}", dependencies=[Depends(check_api_key)])
def edit_pracownik(id: int, pracownik:Pracownik_Change, db: Session = Depends(get_db)):
    pracownik_db=db.query(Pracownik).filter(Pracownik.id_pracownika == id).first()
    if pracownik_db is None:
        raise HTTPException(status_code=404, detail="Brak pracownika o takim id")
    pracownik_db.imie=pracownik.imie
    pracownik_db.nazwisko=pracownik.nazwisko
    db.commit()
    return pracownik_db


class Status_Change(BaseModel):
    nazwa: str


@app.get("/statusy", dependencies=[Depends(check_api_key)])
def statusy(db: Session = Depends(get_db)):
    response = db.query(Status).all()
    return response

@app.get("/status/{id}",dependencies=[Depends(check_api_key)])
def get_status(id:int, db: Session = Depends(get_db)):
    response = db.query(Status).filter(Status.id_statusu == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak statusu o takim id")
    return response

@app.post("/add_status",status_code=201,dependencies=[Depends(check_api_key)])
def add_status(status:Status_Change, db: Session = Depends(get_db)):
    status_db=Status(nazwa=status.nazwa)
    db.add(status_db)
    db.commit()
    db.refresh(status_db)
    return status_db

@app.delete("/del_status/{id}",dependencies=[Depends(check_api_key)],responses={404: {'description': 'Brak statusa o takim id'}})
def del_status(id:int, db: Session = Depends(get_db)):
    response= db.query(Status).filter(Status.id_statusu == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak statusu o takim id")
    db.delete(response)
    db.commit()
    return {"message": f"Usunięto statusu {id}"}

@app.put("/edit_status/{id}", dependencies=[Depends(check_api_key)])
def edit_status(id: int, status:Status_Change, db: Session = Depends(get_db)):
    status_db=db.query(Status).filter(Status.id_statusu == id).first()
    if status_db is None:
        raise HTTPException(status_code=404, detail="Brak statusu o takim id")
    status_db.nazwa=status.nazwa
    db.commit()
    return status_db
    
    
class Dostawa_Change(BaseModel):
    id_formy_dostawy: int
    id_firmy: int


@app.get("/dostawy", dependencies=[Depends(check_api_key)])
def dostawy(db: Session = Depends(get_db)):
    response = db.query(Dostawa).all()
    return response

@app.get("/dostawa/{id}",dependencies=[Depends(check_api_key)])
def get_dostawa(id:int, db: Session = Depends(get_db)):
    response = db.query(Dostawa).filter(Dostawa.id_dostawy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak dostawy o takim id")
    return response

@app.post("/add_dostawa",status_code=201,dependencies=[Depends(check_api_key)])
def add_dostawa(dostawa:Dostawa_Change, db: Session = Depends(get_db)):
    dostawa_db=Dostawa(id_firmy=dostawa.id_firmy,id_formy_dostawy=dostawa.id_formy_dostawy)
    db.add(dostawa_db)
    db.commit()
    db.refresh(dostawa_db)
    return dostawa_db

@app.delete("/del_dostawa/{id}",dependencies=[Depends(check_api_key)],responses={404: {'description': 'Brak dostawy o takim id'}})
def del_dostawa(id:int, db: Session = Depends(get_db)):
    response= db.query(Dostawa).filter(Dostawa.id_dostawy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak dostawy o takim id")
    db.delete(response)
    db.commit()
    return {"message": f"Usunięto dostawau {id}"}

@app.put("/edit_dostawa/{id}", dependencies=[Depends(check_api_key)])
def edit_dostawa(id: int, dostawa:Dostawa_Change, db: Session = Depends(get_db)):
    dostawa_db=db.query(Dostawa).filter(Dostawa.id_dostawy == id).first()
    if dostawa_db is None:
        raise HTTPException(status_code=404, detail="Brak dostawy o takim id")
    dostawa_db.nazwa=dostawa.nazwa
    db.commit()
    return dostawa_db


class FirmaDostawcza_Change(BaseModel):
    nazwa: str
    

@app.get("/firmyDostawczee", dependencies=[Depends(check_api_key)])
def firmyDostawczee(db: Session = Depends(get_db)):
    response = db.query(FirmaDostawcza).all()
    return response

@app.get("/firmaDostawcza/{id}",dependencies=[Depends(check_api_key)])
def get_firmaDostawcza(id:int, db: Session = Depends(get_db)):
    response = db.query(FirmaDostawcza).filter(FirmaDostawcza.id_firmy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak firmy dostawczej o takim id")
    return response

@app.post("/add_firmaDostawcza",status_code=201,dependencies=[Depends(check_api_key)])
def add_firmaDostawcza(firmaDostawcza:FirmaDostawcza_Change, db: Session = Depends(get_db)):
    firmaDostawcza_db=FirmaDostawcza(nazwa=firmaDostawcza.nazwa)
    db.add(firmaDostawcza_db)
    db.commit()
    db.refresh(firmaDostawcza_db)
    return firmaDostawcza_db

@app.delete("/del_firmaDostawcza/{id}",dependencies=[Depends(check_api_key)],responses={404: {'description': 'Brak firmy dostawczej o takim id'}})
def del_firmaDostawcza(id:int, db: Session = Depends(get_db)):
    response= db.query(FirmaDostawcza).filter(FirmaDostawcza.id_firmy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak firmy dostawczej o takim id")
    db.delete(response)
    db.commit()
    return {"message": f"Usunięto firmy dostawczej {id}"}

@app.put("/edit_firmaDostawcza/{id}", dependencies=[Depends(check_api_key)])
def edit_firmaDostawcza(id: int, firmaDostawcza:FirmaDostawcza_Change, db: Session = Depends(get_db)):
    firmaDostawcza_db=db.query(FirmaDostawcza).filter(FirmaDostawcza.id_firmy == id).first()
    if firmaDostawcza_db is None:
        raise HTTPException(status_code=404, detail="Brak firmy dostawczej o takim id")
    firmaDostawcza_db.imie=firmaDostawcza.imie
    firmaDostawcza_db.nazwisko=firmaDostawcza.nazwisko
    db.commit()
    return firmaDostawcza_db
    
    
    class FormaDostawy_Change(BaseModel):
    nazwa: str
    

@app.get("/formyDostawy", dependencies=[Depends(check_api_key)])
def formyDostawy(db: Session = Depends(get_db)):
    response = db.query(FormaDostawy).all()
    return response

@app.get("/formaDostawy/{id}",dependencies=[Depends(check_api_key)])
def get_formaDostawy(id:int, db: Session = Depends(get_db)):
    response = db.query(FormaDostawy).filter(FormaDostawy.id_formy_dostawy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak formy dostawy o takim id")
    return response

@app.post("/add_formaDostawy",status_code=201,dependencies=[Depends(check_api_key)])
def add_formaDostawy(formaDostawy:FormaDostawy_Change, db: Session = Depends(get_db)):
    formaDostawy_db=FormaDostawy(nazwa=formaDostawy.nazwa)
    db.add(formaDostawy_db)
    db.commit()
    db.refresh(formaDostawy_db)
    return formaDostawy_db

@app.delete("/del_formaDostawy/{id}",dependencies=[Depends(check_api_key)],responses={404: {'description': 'Brak formy dostawyo takim id'}})
def del_formaDostawy(id:int, db: Session = Depends(get_db)):
    response= db.query(FormaDostawy).filter(FormaDostawy.id_formy_dostawy == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Brak formy dostawy o takim id")
    db.delete(response)
    db.commit()
    return {"message": f"Usunięto formy dostawy {id}"}

@app.put("/edit_formaDostawy/{id}", dependencies=[Depends(check_api_key)])
def edit_formaDostawy(id: int, formaDostawy:FormaDostawy_Change, db: Session = Depends(get_db)):
    formaDostawy_db=db.query(FormaDostawy).filter(FormaDostawy.id_formy_dostawy == id).first()
    if formaDostawy_db is None:
        raise HTTPException(status_code=404, detail="Brak formy dostawy o takim id")
    formaDostawy_db.imie=formaDostawy.imie
    formaDostawy_db.nazwisko=formaDostawy.nazwisko
    db.commit()
    return formaDostawy_db