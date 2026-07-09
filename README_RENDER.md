# Deploy su Render

Questa guida ti permette di pubblicare l'app su Render e ottenere un link pubblico da usare anche da mobile.

## Prerequisiti
- Repository su GitHub (o GitLab/Bitbucket) con questi file: `requirements.txt`, `wsgi.py`, `render.yaml`.
- Un account gratuito su https://render.com

## Passi
1. Fai push del codice su GitHub.
2. Vai su Render -> New + -> Blueprint -> collega il repository.
3. Render leggerà `render.yaml` e creerà:
   - un servizio web chiamato `pescheria`;
   - un database Postgres gratuito `pescheria-db`.
4. Al primo deploy, Render installerà i pacchetti e avvierà `gunicorn` con `wsgi:app`.
5. Dopo il primo avvio, esegui la migrazione e il seed (opzionale) dal terminale del servizio:

   - Apri il servizio web su Render -> Shell
   - Crea le tabelle (se non usi Flask-Migrate):
