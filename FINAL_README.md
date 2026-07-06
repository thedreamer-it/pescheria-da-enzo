# Pescheria da Enzo - v2 pratica

Include:
- dashboard migliorata
- lista ordini cliccabile e dettaglio ordine
- clienti con via, città, CAP
- prodotti con foto, costo, prezzo pubblico, disponibilità
- listino prezzi
- ordini con righe persistenti

## Avvio rapido

```bash
cd ~/Desktop/Progetto/pescheria_da_enzo_v2
source .venv/bin/activate
pip install -r requirements.txt
export DB_ENGINE=postgres
export PG_USER=samuelepellizzieri
export PG_PASSWORD=
export PG_HOST=localhost
export PG_PORT=5432
export PG_DATABASE=pescheria_da_enzo
python init_db.py
python app.py
```

## Nota sulle immagini
Le immagini iniziali usano URL pubblici di esempio e possono essere sostituite in seguito con foto del vostro catalogo.
