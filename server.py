from fastapi import FastAPI, Header, HTTPException, Depends

# Do db ###################
from db_connection import get_db
from tables import Pracownik, Status,Dostawa,FirmaDostawcza, FormaDostawy, Zamowienia, FormaPlatnosci, PozycjaZamowienia, Produkt, Magazyn, Klient, Adres, ProduktMagazyn
from sqlalchemy.orm import Session
from sqlalchemy import decimal
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
    firmaDostawcza_db.nazwa=firmaDostawcza.nazwa
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
    formaDostawy_db.nazwa=formaDostawy.nazwa
    db.commit()
    return formaDostawy_db

#     Lewa strona API    #
##########################

class Zamowienie_Change(BaseModel):
    id_statusu: int
    id_pracownika: int
    id_klienta: int
    id_formy_platnosci: int
    id_dostawy: int
    

@app.get("/zamowienia", dependencies=[Depends(check_api_key)])
def get_zamowienia(db: Session = Depends(get_db)):
    return db.query(Zamowienia).all()


@app.get("/zamowienie/{id}", dependencies=[Depends(check_api_key)])
def get_zamowienie(id: int, db: Session = Depends(get_db)):
    zam = db.query(Zamowienia).filter(Zamowienia.id_zamowienia == id).first()
    if zam is None:
        raise HTTPException(status_code=404, detail="Brak zamówienia o takim id")
    return zam


@app.post("/zamowienie", status_code=201, dependencies=[Depends(check_api_key)])
def add_zamowienie(zam: Zamowienie_Change, db: Session = Depends(get_db)):
    zam_db = Zamowienia(**zam.dict())
    db.add(zam_db)
    db.commit()
    db.refresh(zam_db)
    return zam_db


@app.put("/zamowienie/{id}", dependencies=[Depends(check_api_key)])
def edit_zamowienie(id: int, zam: Zamowienie_Change, db: Session = Depends(get_db)):
    zam_db = db.query(Zamowienia).filter(Zamowienia.id_zamowienia == id).first()
    if zam_db is None:
        raise HTTPException(status_code=404, detail="Brak zamówienia o takim id")
    for k, v in zam.dict().items():
        setattr(zam_db, k, v)
    db.commit()
    return zam_db


@app.delete("/zamowienie/{id}", dependencies=[Depends(check_api_key)])
def delete_zamowienie(id: int, db: Session = Depends(get_db)):
    zam = db.query(Zamowienia).filter(Zamowienia.id_zamowienia == id).first()
    if zam is None:
        raise HTTPException(status_code=404, detail="Brak zamówienia o takim id")
    db.delete(zam)
    db.commit()
    return {"message": f"Usunięto zamówienie {id}"}


class FormaPlatnosci_Change(BaseModel):
    nazwa: str


@app.get("/formy_platnosci", dependencies=[Depends(check_api_key)])
def get_formy(db: Session = Depends(get_db)):
    return db.query(FormaPlatnosci).all()


@app.get("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)])
def get_forma(id: int, db: Session = Depends(get_db)):
    f = db.query(FormaPlatnosci).filter(FormaPlatnosci.id_formy_platnosci == id).first()
    if f is None:
        raise HTTPException(status_code=404, detail="Brak formy płatności o takim id")
    return f


@app.post("/formy_platnosci", status_code=201, dependencies=[Depends(check_api_key)])
def add_forma(forma: FormaPlatnosci_Change, db: Session = Depends(get_db)):
    f = FormaPlatnosci(**forma.dict())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@app.put("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)])
def edit_forma(id: int, forma: FormaPlatnosci_Change, db: Session = Depends(get_db)):
    f = db.query(FormaPlatnosci).filter(FormaPlatnosci.id_formy_platnosci == id).first()
    if f is None:
        raise HTTPException(status_code=404, detail="Brak formy płatności o takim id")
    f.nazwa = forma.nazwa
    db.commit()
    return f


@app.delete("/formy_platnosci/{id}", dependencies=[Depends(check_api_key)])
def delete_forma(id: int, db: Session = Depends(get_db)):
    f = db.query(FormaPlatnosci).filter(FormaPlatnosci.id_formy_platnosci == id).first()
    if f is None:
        raise HTTPException(status_code=404, detail="Brak formy płatności o takim id")
    db.delete(f)
    db.commit()
    return {"message": f"Usunięto formę płatności {id}"}


class PozycjaZamowienia_Change(BaseModel):
    id_zamowienia: int
    id_produktu: int
    ilosc: int
    cena: decimal


@app.get("/pozycje_zamowienia", dependencies=[Depends(check_api_key)])
def get_pozycje(db: Session = Depends(get_db)):
    return db.query(PozycjaZamowienia).all()


@app.get("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)])
def get_pozycja(id: int, db: Session = Depends(get_db)):
    p = db.query(PozycjaZamowienia).filter(PozycjaZamowienia.id_pozycji == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak pozycji o takim id")
    return p


@app.post("/pozycje_zamowienia", status_code=201, dependencies=[Depends(check_api_key)])
def add_pozycja(poz: PozycjaZamowienia_Change, db: Session = Depends(get_db)):
    p = PozycjaZamowienia(**poz.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)])
def edit_pozycja(id: int, poz: PozycjaZamowienia_Change, db: Session = Depends(get_db)):
    p = db.query(PozycjaZamowienia).filter(PozycjaZamowienia.id_pozycji == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak pozycji o takim id")
    for k, v in poz.dict().items():
        setattr(p, k, v)
    db.commit()
    return p


@app.delete("/pozycje_zamowienia/{id}", dependencies=[Depends(check_api_key)])
def delete_pozycja(id: int, db: Session = Depends(get_db)):
    p = db.query(PozycjaZamowienia).filter(PozycjaZamowienia.id_pozycji == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak pozycji o takim id")
    db.delete(p)
    db.commit()
    return {"message": f"Usunięto pozycję {id}"}



class Produkt_Change(BaseModel):
    nazwa: str
    cena: decimal


@app.get("/produkty", dependencies=[Depends(check_api_key)])
def get_produkty(db: Session = Depends(get_db)):
    return db.query(Produkt).all()


@app.get("/produkty/{id}", dependencies=[Depends(check_api_key)])
def get_produkt(id: int, db: Session = Depends(get_db)):
    p = db.query(Produkt).filter(Produkt.id_produktu == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak produktu o takim id")
    return p


@app.post("/produkty", status_code=201, dependencies=[Depends(check_api_key)])
def add_produkt(prod: Produkt_Change, db: Session = Depends(get_db)):
    p = Produkt(**prod.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/produkty/{id}", dependencies=[Depends(check_api_key)])
def edit_produkt(id: int, prod: Produkt_Change, db: Session = Depends(get_db)):
    p = db.query(Produkt).filter(Produkt.id_produktu == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak produktu o takim id")
    p.nazwa = prod.nazwa
    p.cena = prod.cena
    db.commit()
    return p


@app.delete("/produkty/{id}", dependencies=[Depends(check_api_key)])
def delete_produkt(id: int, db: Session = Depends(get_db)):
    p = db.query(Produkt).filter(Produkt.id_produktu == id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Brak produktu o takim id")
    db.delete(p)
    db.commit()
    return {"message": f"Usunięto produkt {id}"}


class ProduktMagazyn_Change(BaseModel):
    id_produktu: int
    id_magazynu: int
    ilosc: int



@app.get("/produktMagazyn", dependencies=[Depends(check_api_key)])
def get_produktMagazyn(db: Session = Depends(get_db)):
    return db.query(ProduktMagazyn).all()


@app.get("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)])
def get_produktMagazyn(id: int, db: Session = Depends(get_db)):
    m = db.query(ProduktMagazyn).filter(ProduktMagazyn.id_produktMagazyn == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak Produkt Magazynu o takim id")
    return m

@app.post("/produktMagazyn", status_code=201, dependencies=[Depends(check_api_key)])
def add_produktMagazyn(mag: ProduktMagazyn_Change, db: Session = Depends(get_db)):
    m = ProduktMagazyn(**mag.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@app.put("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)])
def edit_produktMagazyn(id: int, mag: ProduktMagazyn_Change, db: Session = Depends(get_db)):
    m = db.query(ProduktMagazyn).filter(ProduktMagazyn.id_produktMagazyn == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak Produkt Magazynu o takim id")
    m.id_produktu = mag.id_produktu
    m.id_magazynu = mag.id_magazynu
    m.ilosc = mag.ilosc
    db.commit()
    return m

@app.delete("/produktMagazyn/{id}", dependencies=[Depends(check_api_key)])
def delete_produktMagazyn(id: int, db: Session = Depends(get_db)):
    m = db.query(ProduktMagazyn).filter(ProduktMagazyn.id_produktMagazyn == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak Produkt Magazynu o takim id")
    db.delete(m)
    db.commit()
    return {"message": f"Usunięto Produkt Magazynu {id}"}


class Magazyn_Change(BaseModel):
    nazwa: str


@app.get("/magazyny", dependencies=[Depends(check_api_key)])
def get_magazyny(db: Session = Depends(get_db)):
    return db.query(Magazyn).all()


@app.get("/magazyny/{id}", dependencies=[Depends(check_api_key)])
def get_magazyn(id: int, db: Session = Depends(get_db)):
    m = db.query(Magazyn).filter(Magazyn.id_magazynu == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak magazynu o takim id")
    return m


@app.post("/magazyny", status_code=201, dependencies=[Depends(check_api_key)])
def add_magazyn(mag: Magazyn_Change, db: Session = Depends(get_db)):
    m = Magazyn(**mag.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@app.put("/magazyny/{id}", dependencies=[Depends(check_api_key)])
def edit_magazyn(id: int, mag: Magazyn_Change, db: Session = Depends(get_db)):
    m = db.query(Magazyn).filter(Magazyn.id_magazynu == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak magazynu o takim id")
    m.nazwa = mag.nazwa
    db.commit()
    return m


@app.delete("/magazyny/{id}", dependencies=[Depends(check_api_key)])
def delete_magazyn(id: int, db: Session = Depends(get_db)):
    m = db.query(Magazyn).filter(Magazyn.id_magazynu == id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="Brak magazynu o takim id")
    db.delete(m)
    db.commit()
    return {"message": f"Usunięto magazyn {id}"}


class Klient_Change(BaseModel):
    imie: str | None
    nazwisko: str | None
    telefon: str | None
    email: str | None


@app.get("/klienci", dependencies=[Depends(check_api_key)])
def get_klienci(db: Session = Depends(get_db)):
    return db.query(Klient).all()


@app.get("/klienci/{id}", dependencies=[Depends(check_api_key)])
def get_klient(id: int, db: Session = Depends(get_db)):
    k = db.query(Klient).filter(Klient.id_klienta == id).first()
    if k is None:
        raise HTTPException(status_code=404, detail="Brak klienta o takim id")
    return k


@app.post("/klienci", status_code=201, dependencies=[Depends(check_api_key)])
def add_klient(kl: Klient_Change, db: Session = Depends(get_db)):
    k = Klient(**kl.dict())
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


@app.put("/klienci/{id}", dependencies=[Depends(check_api_key)])
def edit_klient(id: int, kl: Klient_Change, db: Session = Depends(get_db)):
    k = db.query(Klient).filter(Klient.id_klienta == id).first()
    if k is None:
        raise HTTPException(status_code=404, detail="Brak klienta o takim id")
    for key, value in kl.dict().items():
        setattr(k, key, value)
    db.commit()
    return k


@app.delete("/klienci/{id}", dependencies=[Depends(check_api_key)])
def delete_klient(id: int, db: Session = Depends(get_db)):
    k = db.query(Klient).filter(Klient.id_klienta == id).first()
    if k is None:
        raise HTTPException(status_code=404, detail="Brak klienta o takim id")
    db.delete(k)
    db.commit()
    return {"message": f"Usunięto klienta {id}"}



class Adres_Change(BaseModel):
    id_klienta: int
    miasto: str
    ulica: str
    kod_pocztowy: str


@app.get("/adresy", dependencies=[Depends(check_api_key)])
def get_adresy(db: Session = Depends(get_db)):
    return db.query(Adres).all()


@app.get("/adresy/{id}", dependencies=[Depends(check_api_key)])
def get_adres(id: int, db: Session = Depends(get_db)):
    a = db.query(Adres).filter(Adres.id_adresu == id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Brak adresu o takim id")
    return a


@app.post("/adresy", status_code=201, dependencies=[Depends(check_api_key)])
def add_adres(ad: Adres_Change, db: Session = Depends(get_db)):
    a = Adres(**ad.dict())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@app.put("/adresy/{id}", dependencies=[Depends(check_api_key)])
def edit_adres(id: int, ad: Adres_Change, db: Session = Depends(get_db)):
    a = db.query(Adres).filter(Adres.id_adresu == id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Brak adresu o takim id")
    for k, v in ad.dict().items():
        setattr(a, k, v)
    db.commit()
    return a


@app.delete("/adresy/{id}", dependencies=[Depends(check_api_key)])
def delete_adres(id: int, db: Session = Depends(get_db)):
    a = db.query(Adres).filter(Adres.id_adresu == id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Brak adresu o takim id")
    db.delete(a)
    db.commit()
    return {"message": f"Usunięto adres {id}"}
