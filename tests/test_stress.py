import time
import statistics
import pytest
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = "http://localhost:8001"
H = {"x-api-key": "tajny-klucz-123"}
PRACOWNIK = {"imie": "Stress", "nazwisko": "Test", "stanowisko": "LoadTest"}


def _server_running():
    try:
        return requests.get(f"{BASE}/", timeout=1).status_code == 200
    except Exception:
        return False


skip_if_down = pytest.mark.skipif(
    not _server_running(),
    reason="serwer nie dziala na localhost:8001"
)


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    try:
        pracownicy = requests.get(f"{BASE}/pracownicy", headers=H).json()
        for p in pracownicy:
            if p.get("imie") == "Stress":
                requests.delete(f"{BASE}/del_pracownik/{p['id_pracownika']}", headers=H)
    except Exception:
        pass


def stats(times, label):
    s = sorted(times)
    n = len(s)
    print(f"\n{label}")
    print(f"  n={n} avg={statistics.mean(s):.1f}ms p50={s[n//2]:.1f}ms p95={s[int(n*.95)]:.1f}ms p99={s[int(n*.99)]:.1f}ms max={s[-1]:.1f}ms")


@skip_if_down
def test_burst_1000_get():
    times, errors = [], 0
    for _ in range(1000):
        t = time.perf_counter()
        r = requests.get(f"{BASE}/pracownicy", headers=H)
        times.append((time.perf_counter() - t) * 1000)
        if r.status_code != 200:
            errors += 1

    stats(times, "1000x GET /pracownicy sequential")
    assert errors == 0
    assert sorted(times)[949] < 500


@skip_if_down
def test_concurrent_500_get():
    def req(_):
        t = time.perf_counter()
        r = requests.get(f"{BASE}/pracownicy", headers=H)
        return r.status_code, (time.perf_counter() - t) * 1000

    with ThreadPoolExecutor(max_workers=50) as pool:
        res = list(pool.map(req, range(500)))

    errors = sum(1 for s, _ in res if s != 200)
    stats([t for _, t in res], "500x GET concurrent (50 workers)")
    assert errors == 0


@skip_if_down
def test_burst_500_post():
    times, errors = [], 0
    for _ in range(500):
        t = time.perf_counter()
        r = requests.post(f"{BASE}/add_pracownik", headers=H, json=PRACOWNIK)
        times.append((time.perf_counter() - t) * 1000)
        if r.status_code != 201:
            errors += 1

    stats(times, "500x POST /add_pracownik sequential")
    assert errors == 0
    assert sorted(times)[474] < 1000


@skip_if_down
def test_concurrent_200_post():
    def req(_):
        t = time.perf_counter()
        r = requests.post(f"{BASE}/add_pracownik", headers=H, json=PRACOWNIK)
        return r.status_code, (time.perf_counter() - t) * 1000

    with ThreadPoolExecutor(max_workers=50) as pool:
        res = list(pool.map(req, range(200)))

    errors = sum(1 for s, _ in res if s != 201)
    stats([t for _, t in res], "200x POST concurrent (50 workers)")
    assert errors == 0


@skip_if_down
def test_mixed_crud_load():
    import random
    random.seed(42)
    ops = ["get"] * 250 + ["post"] * 150 + ["get_one"] * 60 + ["status"] * 40
    random.shuffle(ops)

    def req(op):
        t = time.perf_counter()
        if op == "get":
            r = requests.get(f"{BASE}/pracownicy", headers=H)
            ok = r.status_code == 200
        elif op == "post":
            r = requests.post(f"{BASE}/add_pracownik", headers=H, json=PRACOWNIK)
            ok = r.status_code == 201
        elif op == "get_one":
            r = requests.get(f"{BASE}/pracownik/1", headers=H)
            ok = r.status_code in (200, 404)
        else:
            r = requests.get(f"{BASE}/statusy", headers=H)
            ok = r.status_code == 200
        return ok, (time.perf_counter() - t) * 1000

    with ThreadPoolExecutor(max_workers=50) as pool:
        res = list(pool.map(req, ops))

    errors = sum(1 for ok, _ in res if not ok)
    stats([t for _, t in res], "500x mixed CRUD (50 workers)")
    assert errors == 0


@skip_if_down
def test_concurrent_auth_rejection():
    def req(_):
        return requests.get(f"{BASE}/pracownicy", headers={"x-api-key": "zly-klucz"}).status_code

    with ThreadPoolExecutor(max_workers=50) as pool:
        res = list(pool.map(req, range(500)))

    wrong = [s for s in res if s != 401]
    print(f"\n500x auth rejection — ok: {res.count(401)}, wrong: {len(wrong)}")
    assert not wrong


@skip_if_down
def test_spike_100_workers():
    def req(_):
        t = time.perf_counter()
        r = requests.get(f"{BASE}/pracownicy", headers=H)
        return r.status_code, (time.perf_counter() - t) * 1000

    with ThreadPoolExecutor(max_workers=100) as pool:
        res = list(pool.map(req, range(300)))

    errors = sum(1 for s, _ in res if s != 200)
    stats([t for _, t in res], "300x spike GET (100 workers)")
    assert errors == 0


@skip_if_down
def test_sla():
    times = []
    for _ in range(500):
        t = time.perf_counter()
        requests.get(f"{BASE}/", headers=H)
        times.append((time.perf_counter() - t) * 1000)

    s = sorted(times)
    p95, p99 = s[474], s[494]
    print(f"\nSLA — p95={p95:.1f}ms p99={p99:.1f}ms")
    assert p95 < 200
    assert p99 < 500
