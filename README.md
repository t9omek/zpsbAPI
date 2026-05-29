# zpsbAPI
Wdrażanie i integracja systemów informatycznych


TB:
Uruchomienie projektu 

Plik: docker-compose.yml

Polecenie: docker-compose up -d

Plik baza.sql powinien zostac dodany do
/docker-entrypoint-initdb.d/



Ręczne wykonanie skryptu SQL


docker exec -i serverAPI_db psql -U postgres -d apiDB < baza.sql




