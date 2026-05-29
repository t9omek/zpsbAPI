import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SASession
from db_connection import engine, get_db
import tables
from server import app

KEY = "tajny-klucz-123"
H = {"x-api-key": KEY}


def log_req(method, url, resp):
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    print(f"{method} {url} -> {resp.status_code} | {body}")


@pytest.fixture
def db_session():
    conn = engine.connect()
    tx = conn.begin()
    sess = SASession(conn, join_transaction_mode="create_savepoint")
    yield sess
    sess.close()
    tx.rollback()
    conn.close()


@pytest.fixture
def client(db_session):
    def _override():
        yield db_session
    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# patch TestClient zeby logowac requesty
_orig_get = TestClient.get
_orig_post = TestClient.post
_orig_put = TestClient.put
_orig_delete = TestClient.delete

def _get(self, url, **kw):
    r = _orig_get(self, url, **kw); log_req("GET", url, r); return r
def _post(self, url, **kw):
    r = _orig_post(self, url, **kw); log_req("POST", url, r); return r
def _put(self, url, **kw):
    r = _orig_put(self, url, **kw); log_req("PUT", url, r); return r
def _delete(self, url, **kw):
    r = _orig_delete(self, url, **kw); log_req("DELETE", url, r); return r

TestClient.get = _get
TestClient.post = _post
TestClient.put = _put
TestClient.delete = _delete


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "API działa"


@pytest.mark.parametrize("method,url,body", [
    ("get",    "/pracownicy",       None),
    ("get",    "/pracownik/1",      None),
    ("post",   "/add_pracownik",    {"imie": "X", "nazwisko": "Y", "stanowisko": "Z"}),
    ("put",    "/edit_pracownik/1", {"imie": "X", "nazwisko": "Y", "stanowisko": "Z"}),
    ("delete", "/del_pracownik/1",  None),
    ("get",    "/statusy",          None),
    ("get",    "/dostawy",          None),
    ("get",    "/zamowienia",       None),
    ("get",    "/klienci",          None),
    ("get",    "/produkty",         None),
    ("get",    "/magazyny",         None),
    ("get",    "/adresy",           None),
])
def test_unauthorized(client, method, url, body):
    fn = getattr(client, method)
    r = fn(url, json=body) if body else fn(url)
    assert r.status_code == 401


class TestPracownicy:
    def test_get_all(self, client):
        r = client.get("/pracownicy", headers=H)
        assert r.status_code == 200
        assert type(r.json()) == list

    def test_create(self, client):
        r = client.post("/add_pracownik", headers=H,
                        json={"imie": "Jan", "nazwisko": "Kowalski", "stanowisko": "Dev"})
        assert r.status_code == 201
        assert r.json()["imie"] == "Jan"

    def test_get_by_id(self, client, db_session):
        p = tables.Pracownik(imie="Anna", nazwisko="Nowak", stanowisko="PM")
        db_session.add(p)
        db_session.flush()
        r = client.get(f"/pracownik/{p.id_pracownika}", headers=H)
        assert r.status_code == 200
        assert r.json()["imie"] == "Anna"

    def test_get_not_found(self, client):
        assert client.get("/pracownik/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        p = tables.Pracownik(imie="Piotr", nazwisko="Wisniewski", stanowisko="QA")
        db_session.add(p)
        db_session.flush()
        r = client.put(f"/edit_pracownik/{p.id_pracownika}", headers=H,
                       json={"imie": "Pawel", "nazwisko": "Wisniewski", "stanowisko": "Senior QA"})
        assert r.status_code == 200
        assert r.json()["imie"] == "Pawel"

    def test_update_not_found(self, client):
        r = client.put("/edit_pracownik/99999", headers=H,
                       json={"imie": "X", "nazwisko": "Y", "stanowisko": "Z"})
        assert r.status_code == 404

    def test_delete(self, client, db_session):
        p = tables.Pracownik(imie="Ewa", nazwisko="Zielinska", stanowisko="Tester")
        db_session.add(p)
        db_session.flush()
        assert client.delete(f"/del_pracownik/{p.id_pracownika}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/del_pracownik/99999", headers=H).status_code == 404


class TestStatusy:
    def test_get_all(self, client):
        r = client.get("/statusy", headers=H)
        assert r.status_code == 200

    def test_create(self, client):
        r = client.post("/add_status", headers=H, json={"nazwa": "Nowy"})
        assert r.status_code == 201
        assert r.json()["nazwa"] == "Nowy"

    def test_get_by_id(self, client, db_session):
        s = tables.Status(nazwa="W trakcie")
        db_session.add(s)
        db_session.flush()
        assert client.get(f"/status/{s.id_statusu}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/status/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        s = tables.Status(nazwa="stary status")
        db_session.add(s)
        db_session.flush()
        r = client.put(f"/edit_status/{s.id_statusu}", headers=H, json={"nazwa": "nowy status"})
        assert r.status_code == 200
        assert r.json()["nazwa"] == "nowy status"

    def test_update_not_found(self, client):
        assert client.put("/edit_status/99999", headers=H, json={"nazwa": "X"}).status_code == 404

    def test_delete(self, client, db_session):
        s = tables.Status(nazwa="do usuniecia")
        db_session.add(s)
        db_session.flush()
        assert client.delete(f"/del_status/{s.id_statusu}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/del_status/99999", headers=H).status_code == 404


class TestFirmyDostawcze:
    def test_get_all(self, client):
        assert client.get("/firmyDostawczee", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/add_firmaDostawcza", headers=H, json={"nazwa": "InPost"})
        assert r.status_code == 201
        assert r.json()["nazwa"] == "InPost"

    def test_get_by_id(self, client, db_session):
        f = tables.FirmaDostawcza(nazwa="DHL")
        db_session.add(f)
        db_session.flush()
        assert client.get(f"/firmaDostawcza/{f.id_firmy}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/firmaDostawcza/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        f = tables.FirmaDostawcza(nazwa="stara nazwa")
        db_session.add(f)
        db_session.flush()
        assert client.put(f"/edit_firmaDostawcza/{f.id_firmy}", headers=H, json={"nazwa": "nowa nazwa"}).status_code == 200

    def test_delete(self, client, db_session):
        f = tables.FirmaDostawcza(nazwa="do usuniecia")
        db_session.add(f)
        db_session.flush()
        assert client.delete(f"/del_firmaDostawcza/{f.id_firmy}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/del_firmaDostawcza/99999", headers=H).status_code == 404


class TestFormyDostawy:
    def test_get_all(self, client):
        assert client.get("/formyDostawy", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/add_formaDostawy", headers=H, json={"nazwa": "Kurier"})
        assert r.status_code == 201

    def test_get_by_id(self, client, db_session):
        f = tables.FormaDostawy(nazwa="Paczkomat")
        db_session.add(f)
        db_session.flush()
        assert client.get(f"/formaDostawy/{f.id_formy_dostawy}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/formaDostawy/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        f = tables.FormaDostawy(nazwa="stara")
        db_session.add(f)
        db_session.flush()
        assert client.put(f"/edit_formaDostawy/{f.id_formy_dostawy}", headers=H, json={"nazwa": "nowa"}).status_code == 200

    def test_delete(self, client, db_session):
        f = tables.FormaDostawy(nazwa="usun mnie")
        db_session.add(f)
        db_session.flush()
        assert client.delete(f"/del_formaDostawy/{f.id_formy_dostawy}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/del_formaDostawy/99999", headers=H).status_code == 404


class TestDostawy:
    def test_get_all(self, client):
        assert client.get("/dostawy", headers=H).status_code == 200

    def test_create(self, client, db_session):
        fd = tables.FormaDostawy(nazwa="Kurier")
        fc = tables.FirmaDostawcza(nazwa="DHL")
        db_session.add_all([fd, fc])
        db_session.flush()
        r = client.post("/add_dostawa", headers=H,
                        json={"id_formy_dostawy": fd.id_formy_dostawy, "id_firmy": fc.id_firmy})
        assert r.status_code == 201

    def test_get_by_id(self, client, db_session):
        d = tables.Dostawa(id_formy_dostawy=1, id_firmy=1)
        db_session.add(d)
        db_session.flush()
        assert client.get(f"/dostawa/{d.id_dostawy}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/dostawa/99999", headers=H).status_code == 404

    def test_delete(self, client, db_session):
        d = tables.Dostawa(id_formy_dostawy=1, id_firmy=1)
        db_session.add(d)
        db_session.flush()
        assert client.delete(f"/del_dostawa/{d.id_dostawy}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/del_dostawa/99999", headers=H).status_code == 404


class TestFormyPlatnosci:
    def test_get_all(self, client):
        assert client.get("/formy_platnosci", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/formy_platnosci", headers=H, json={"nazwa": "Przelew"})
        assert r.status_code == 201
        assert r.json()["nazwa"] == "Przelew"

    def test_get_by_id(self, client, db_session):
        f = tables.FormaPlatnosci(nazwa="Gotowka")
        db_session.add(f)
        db_session.flush()
        assert client.get(f"/formy_platnosci/{f.id_formy_platnosci}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/formy_platnosci/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        f = tables.FormaPlatnosci(nazwa="stara")
        db_session.add(f)
        db_session.flush()
        assert client.put(f"/formy_platnosci/{f.id_formy_platnosci}", headers=H, json={"nazwa": "Karta"}).status_code == 200

    def test_delete(self, client, db_session):
        f = tables.FormaPlatnosci(nazwa="usun")
        db_session.add(f)
        db_session.flush()
        assert client.delete(f"/formy_platnosci/{f.id_formy_platnosci}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/formy_platnosci/99999", headers=H).status_code == 404


class TestMagazyny:
    def test_get_all(self, client):
        assert client.get("/magazyny", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/magazyny", headers=H, json={"nazwa": "Warszawa"})
        assert r.status_code == 201

    def test_get_by_id(self, client, db_session):
        m = tables.Magazyn(nazwa="Krakow")
        db_session.add(m)
        db_session.flush()
        assert client.get(f"/magazyny/{m.id_magazynu}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/magazyny/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        m = tables.Magazyn(nazwa="stary")
        db_session.add(m)
        db_session.flush()
        assert client.put(f"/magazyny/{m.id_magazynu}", headers=H, json={"nazwa": "nowy"}).status_code == 200

    def test_delete(self, client, db_session):
        m = tables.Magazyn(nazwa="usun")
        db_session.add(m)
        db_session.flush()
        assert client.delete(f"/magazyny/{m.id_magazynu}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/magazyny/99999", headers=H).status_code == 404


class TestKlienci:
    def test_get_all(self, client):
        assert client.get("/klienci", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/klienci", headers=H,
                        json={"imie": "Marek", "nazwisko": "Lewandowski",
                              "telefon": "500100200", "email": "marek@test.pl"})
        assert r.status_code == 201
        assert r.json()["imie"] == "Marek"

    def test_get_by_id(self, client, db_session):
        k = tables.Klient(imie="Zofia", nazwisko="Wojcik", telefon=None, email=None)
        db_session.add(k)
        db_session.flush()
        assert client.get(f"/klienci/{k.id_klienta}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/klienci/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        k = tables.Klient(imie="stare", nazwisko="imie", telefon=None, email=None)
        db_session.add(k)
        db_session.flush()
        r = client.put(f"/klienci/{k.id_klienta}", headers=H,
                       json={"imie": "nowe", "nazwisko": "imie", "telefon": None, "email": None})
        assert r.status_code == 200

    def test_delete(self, client, db_session):
        k = tables.Klient(imie="do", nazwisko="usuniecia", telefon=None, email=None)
        db_session.add(k)
        db_session.flush()
        assert client.delete(f"/klienci/{k.id_klienta}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/klienci/99999", headers=H).status_code == 404


class TestAdresy:
    def _make_klient(self, session):
        k = tables.Klient(imie="Test", nazwisko="Klient", telefon=None, email=None)
        session.add(k)
        session.flush()
        return k

    def test_get_all(self, client):
        assert client.get("/adresy", headers=H).status_code == 200

    def test_create(self, client, db_session):
        k = self._make_klient(db_session)
        r = client.post("/adresy", headers=H,
                        json={"id_klienta": k.id_klienta, "miasto": "Gdansk",
                              "ulica": "Dluga 1", "kod_pocztowy": "80-001"})
        assert r.status_code == 201
        assert r.json()["miasto"] == "Gdansk"

    def test_get_by_id(self, client, db_session):
        k = self._make_klient(db_session)
        a = tables.Adres(id_klienta=k.id_klienta, miasto="Lodz", ulica="Piotrkowska 1", kod_pocztowy="90-001")
        db_session.add(a)
        db_session.flush()
        assert client.get(f"/adresy/{a.id_adresu}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/adresy/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        k = self._make_klient(db_session)
        a = tables.Adres(id_klienta=k.id_klienta, miasto="stare", ulica="ulica 1", kod_pocztowy="00-001")
        db_session.add(a)
        db_session.flush()
        r = client.put(f"/adresy/{a.id_adresu}", headers=H,
                       json={"id_klienta": k.id_klienta, "miasto": "nowe", "ulica": "ulica 2", "kod_pocztowy": "11-111"})
        assert r.status_code == 200

    def test_delete(self, client, db_session):
        k = self._make_klient(db_session)
        a = tables.Adres(id_klienta=k.id_klienta, miasto="tmp", ulica="tmp 1", kod_pocztowy="00-000")
        db_session.add(a)
        db_session.flush()
        assert client.delete(f"/adresy/{a.id_adresu}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/adresy/99999", headers=H).status_code == 404


class TestProdukty:
    def test_get_all(self, client):
        assert client.get("/produkty", headers=H).status_code == 200

    def test_create(self, client):
        r = client.post("/produkty", headers=H, json={"nazwa": "Laptop", "cena": 3999.99})
        assert r.status_code == 201
        assert r.json()["nazwa"] == "Laptop"

    def test_get_by_id(self, client, db_session):
        p = tables.Produkt(nazwa="Monitor", cena=1200)
        db_session.add(p)
        db_session.flush()
        assert client.get(f"/produkty/{p.id_produktu}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/produkty/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        p = tables.Produkt(nazwa="stary", cena=100)
        db_session.add(p)
        db_session.flush()
        assert client.put(f"/produkty/{p.id_produktu}", headers=H, json={"nazwa": "nowy", "cena": 200}).status_code == 200

    def test_delete(self, client, db_session):
        p = tables.Produkt(nazwa="usun", cena=50)
        db_session.add(p)
        db_session.flush()
        assert client.delete(f"/produkty/{p.id_produktu}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/produkty/99999", headers=H).status_code == 404


class TestProduktMagazyn:
    def _setup(self, db_session):
        p = tables.Produkt(nazwa="Towar", cena=10)
        m = tables.Magazyn(nazwa="Mag1")
        db_session.add_all([p, m])
        db_session.flush()
        return p, m

    def test_get_all(self, client):
        assert client.get("/produktMagazyn", headers=H).status_code == 200

    def test_create(self, client, db_session):
        p, m = self._setup(db_session)
        r = client.post("/produktMagazyn", headers=H,
                        json={"id_produktu": p.id_produktu, "id_magazynu": m.id_magazynu, "ilosc": 50})
        assert r.status_code == 201

    def test_get_by_id(self, client, db_session):
        p, m = self._setup(db_session)
        pm = tables.ProduktMagazyn(id_produktu=p.id_produktu, id_magazynu=m.id_magazynu, ilosc=10)
        db_session.add(pm)
        db_session.flush()
        assert client.get(f"/produktMagazyn/{pm.id_produktMagazyn}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/produktMagazyn/99999", headers=H).status_code == 404

    def test_update(self, client, db_session):
        p, m = self._setup(db_session)
        pm = tables.ProduktMagazyn(id_produktu=p.id_produktu, id_magazynu=m.id_magazynu, ilosc=5)
        db_session.add(pm)
        db_session.flush()
        r = client.put(f"/produktMagazyn/{pm.id_produktMagazyn}", headers=H,
                       json={"id_produktu": p.id_produktu, "id_magazynu": m.id_magazynu, "ilosc": 99})
        assert r.status_code == 200

    def test_delete(self, client, db_session):
        p, m = self._setup(db_session)
        pm = tables.ProduktMagazyn(id_produktu=p.id_produktu, id_magazynu=m.id_magazynu, ilosc=1)
        db_session.add(pm)
        db_session.flush()
        assert client.delete(f"/produktMagazyn/{pm.id_produktMagazyn}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/produktMagazyn/99999", headers=H).status_code == 404


class TestZamowienia:
    def _setup(self, db_session):
        prac = tables.Pracownik(imie="A", nazwisko="B", stanowisko="C")
        stat = tables.Status(nazwa="Nowe")
        fp = tables.FormaPlatnosci(nazwa="Przelew")
        fd = tables.FormaDostawy(nazwa="Kurier")
        firma = tables.FirmaDostawcza(nazwa="DHL")
        db_session.add_all([prac, stat, fp, fd, firma])
        db_session.flush()

        klient = tables.Klient(imie="X", nazwisko="Y", telefon=None, email=None)
        db_session.add(klient)
        db_session.flush()

        dostawa = tables.Dostawa(id_formy_dostawy=fd.id_formy_dostawy, id_firmy=firma.id_firmy)
        db_session.add(dostawa)
        db_session.flush()

        return {
            "id_statusu": stat.id_statusu,
            "id_pracownika": prac.id_pracownika,
            "id_klienta": klient.id_klienta,
            "id_formy_platnosci": fp.id_formy_platnosci,
            "id_dostawy": dostawa.id_dostawy,
        }

    def test_get_all(self, client):
        assert client.get("/zamowienia", headers=H).status_code == 200

    def test_create(self, client, db_session):
        data = self._setup(db_session)
        assert client.post("/zamowienie", headers=H, json=data).status_code == 201

    def test_get_by_id(self, client, db_session):
        data = self._setup(db_session)
        z = tables.Zamowienia(**data)
        db_session.add(z)
        db_session.flush()
        assert client.get(f"/zamowienie/{z.id_zamowienia}", headers=H).status_code == 200

    def test_get_not_found(self, client):
        assert client.get("/zamowienie/99999", headers=H).status_code == 404

    def test_delete(self, client, db_session):
        data = self._setup(db_session)
        z = tables.Zamowienia(**data)
        db_session.add(z)
        db_session.flush()
        assert client.delete(f"/zamowienie/{z.id_zamowienia}", headers=H).status_code == 200

    def test_delete_not_found(self, client):
        assert client.delete("/zamowienie/99999", headers=H).status_code == 404
