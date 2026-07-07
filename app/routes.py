from flask import Blueprint, render_template, request, jsonify
from . import db
from .models import Cliente, Prodotto, Confezione, Ordine, RigaOrdine

main = Blueprint("main", __name__)

def seed_demo_data():
    demo = [
        {
            "nome": "Orata",
            "image_url": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?auto=format&fit=crop&w=900&q=80",
            "costo": 8.50,
            "prezzo_pubblico": 14.90,
            "giacenza": 48,
            "unita_misura": "pz",
            "descrizione": "Orata fresca da banco"
        },
        {
            "nome": "Spigola",
            "image_url": "https://images.unsplash.com/photo-1579631542720-3a87824fff86?auto=format&fit=crop&w=900&q=80",
            "costo": 9.20,
            "prezzo_pubblico": 16.50,
            "giacenza": 36,
            "unita_misura": "pz",
            "descrizione": "Spigola fresca ideale al forno"
        },
        {
            "nome": "Gamberi Rossi",
            "image_url": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=900&q=80",
            "costo": 18.00,
            "prezzo_pubblico": 28.00,
            "giacenza": 20,
            "unita_misura": "kg",
            "descrizione": "Gamberi rossi selezionati"
        },
        {
            "nome": "Calamari",
            "image_url": "https://images.unsplash.com/photo-1603048719539-9ecb6fdfaf20?auto=format&fit=crop&w=900&q=80",
            "costo": 10.50,
            "prezzo_pubblico": 18.50,
            "giacenza": 15,
            "unita_misura": "kg",
            "descrizione": "Calamari freschi"
        },
        {
            "nome": "Salmone",
            "image_url": "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?auto=format&fit=crop&w=900&q=80",
            "costo": 13.00,
            "prezzo_pubblico": 22.00,
            "giacenza": 24,
            "unita_misura": "tranci",
            "descrizione": "Tranci di salmone"
        },
    ]

    for item in demo:
        prodotto = Prodotto.query.filter_by(nome=item["nome"]).first()

        if not prodotto:
            prodotto = Prodotto(
                nome=item["nome"],
                image_url=item["image_url"],
                costo=item["costo"],
                prezzo_pubblico=item["prezzo_pubblico"],
                giacenza=item["giacenza"],
                disponibile=item["giacenza"] > 0,
                unita_misura=item["unita_misura"],
                descrizione=item["descrizione"],
            )
            db.session.add(prodotto)
            db.session.flush()

        confezioni_esistenti = {c.nome for c in Confezione.query.filter_by(prodotto_id=prodotto.id).all()}
        for nome_conf, moltiplicatore in [("Base", 1), ("Confezione x2", 2), ("Confezione x5", 5)]:
            if nome_conf not in confezioni_esistenti:
                db.session.add(Confezione(
                    prodotto_id=prodotto.id,
                    nome=nome_conf,
                    moltiplicatore=moltiplicatore,
                    prezzo_extra=0,
                ))

    db.session.commit()

@main.route("/")
def dashboard():
    seed_demo_data()
    clienti = Cliente.query.count()
    prodotti = Prodotto.query.count()
    ordini = Ordine.query.count()
    da_preparare = Ordine.query.filter(Ordine.stato != "evaso").count()
    recenti = Ordine.query.order_by(Ordine.data_ordine.desc()).limit(5).all()
    return render_template("dashboard.html", clienti=clienti, prodotti=prodotti, ordini=ordini, da_preparare=da_preparare, recenti=recenti)

@main.route("/nuovo-ordine")
def nuovo_ordine():
    seed_demo_data()
    prodotti = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    clienti = Cliente.query.order_by(Cliente.nome.asc()).all()
    return render_template("nuovo_ordine.html", prodotti=prodotti, clienti=clienti)

@main.route("/api/ordina", methods=["POST"])
def api_ordina():
    data = request.get_json(force=True)
    cliente_id = data.get("cliente_id")
    articoli = data.get("articoli", [])
    note = data.get("note", "")

    if not articoli:
        return jsonify({"ok": False, "error": "Carrello vuoto"}), 400

    ordine = Ordine(cliente_id=cliente_id or None, stato="nuovo", totale=0.0, note=note)
    db.session.add(ordine)
    db.session.flush()

    totale = 0.0

    for it in articoli:
        p = Prodotto.query.get(int(it["prodotto_id"]))
        if not p:
            continue

        confezione = None
        confezione_id = it.get("confezione_id")
        if confezione_id:
            confezione = Confezione.query.get(int(confezione_id))

        qty = float(it.get("qty", 0))
        moltiplicatore = confezione.moltiplicatore if confezione else 1
        qty_magazzino = qty * moltiplicatore
        prezzo = float(it.get("prezzo_unit", p.prezzo_pubblico if p else 0))
        totale += qty * prezzo

        db.session.add(RigaOrdine(
            ordine_id=ordine.id,
            prodotto_id=p.id,
            confezione_id=confezione.id if confezione else None,
            quantita=qty,
            prezzo_unitario=prezzo,
            quantita_magazzino=qty_magazzino
        ))

        p.giacenza = max(0, (p.giacenza or 0) - qty_magazzino)
        p.disponibile = p.giacenza > 0

    ordine.totale = totale
    db.session.commit()

    return jsonify({"ok": True, "ordine_id": ordine.id})
