from fastapi import FastAPI, Header, HTTPException, Depends

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