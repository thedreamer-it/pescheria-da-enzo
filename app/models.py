from datetime import datetime, date
from . import db

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30))
    via = db.Column(db.String(160))
    citta = db.Column(db.String(80))
    cap = db.Column(db.String(20))
    note = db.Column(db.Text)

class Prodotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.Text)
    costo = db.Column(db.Float, default=0.0)
    prezzo_pubblico = db.Column(db.Float, default=0.0)
    giacenza = db.Column(db.Float, default=0.0)
    disponibile = db.Column(db.Boolean, default=True)
    unita_misura = db.Column(db.String(20), default="pz")
    descrizione = db.Column(db.Text)

class Confezione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prodotto_id = db.Column(db.Integer, db.ForeignKey("prodotto.id"), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    moltiplicatore = db.Column(db.Float, default=1.0)
    prezzo_extra = db.Column(db.Float, default=0.0)

    prodotto = db.relationship("Prodotto", backref="confezioni")

class Ordine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=True)
    data_ordine = db.Column(db.DateTime, default=datetime.utcnow)
    data_consegna = db.Column(db.Date, default=date.today, nullable=False)
    stato = db.Column(db.String(30), default="nuovo")
    consegnato = db.Column(db.Boolean, default=False, nullable=False)
    totale = db.Column(db.Float, default=0.0)
    note = db.Column(db.Text)

    cliente = db.relationship("Cliente", backref="ordini")
    righe = db.relationship("RigaOrdine", backref="ordine", cascade="all, delete-orphan")

class RigaOrdine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordine_id = db.Column(db.Integer, db.ForeignKey("ordine.id"), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey("prodotto.id"), nullable=False)
    confezione_id = db.Column(db.Integer, db.ForeignKey("confezione.id"), nullable=True)
    quantita = db.Column(db.Float, default=0.0)
    prezzo_unitario = db.Column(db.Float, default=0.0)
    quantita_magazzino = db.Column(db.Float, default=0.0)
    evaso = db.Column(db.Boolean, default=False, nullable=False)
    modificato = db.Column(db.Boolean, default=False, nullable=False)

    prodotto = db.relationship("Prodotto")
    confezione = db.relationship("Confezione")
