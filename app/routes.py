from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from . import db
from .models import Cliente, Prodotto, Confezione, Ordine, RigaOrdine

main = Blueprint("main", __name__)

def seed_demo_data():
    if Prodotto.query.count() > 0:
        return

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
        p = Prodotto(
            nome=item["nome"],
            image_url=item["image_url"],
            costo=item["costo"],
            prezzo_pubblico=item["prezzo_pubblico"],
            giacenza=item["giacenza"],
            disponibile=item["giacenza"] > 0,
            unita_misura=item["unita_misura"],
            descrizione=item["descrizione"],
        )
        db.session.add(p)
        db.session.flush()

        db.session.add(Confezione(prodotto_id=p.id, nome="Base", moltiplicatore=1, prezzo_extra=0))
        db.session.add(Confezione(prodotto_id=p.id, nome="Confezione x2", moltiplicatore=2, prezzo_extra=0))
        db.session.add(Confezione(prodotto_id=p.id, nome="Confezione x5", moltiplicatore=5, prezzo_extra=0))

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

@main.route("/ordini")
def ordini():
    items = Ordine.query.order_by(Ordine.data_ordine.desc()).all()
    return render_template("ordini.html", ordini=items)

@main.route("/ordini/<int:order_id>")
def ordine_dettaglio(order_id):
    o = Ordine.query.get_or_404(order_id)
    return render_template("ordine_dettaglio.html", ordine=o)

@main.route("/ordini/<int:order_id>/set/<stato>")
def set_stato(order_id, stato):
    o = Ordine.query.get_or_404(order_id)
    o.stato = stato
    db.session.commit()
    return redirect(url_for("main.ordine_dettaglio", order_id=order_id))

@main.route("/clienti", methods=["GET", "POST"])
def clienti():
    if request.method == "POST":
        db.session.add(Cliente(
            nome=request.form.get("nome"),
            telefono=request.form.get("telefono"),
            via=request.form.get("via"),
            citta=request.form.get("citta"),
            cap=request.form.get("cap"),
            note=request.form.get("note"),
        ))
        db.session.commit()
        return redirect(url_for("main.clienti"))

    items = Cliente.query.order_by(Cliente.nome.asc()).all()
    return render_template("clienti.html", clienti=items)

@main.route("/prodotti", methods=["GET", "POST"])
def prodotti():
    seed_demo_data()

    if request.method == "POST":
        azione = request.form.get("azione")

        if azione == "carico":
            prodotto_id = request.form.get("prodotto_id")
            quantita_carico = float(request.form.get("quantita_carico") or 0)
            prodotto = Prodotto.query.get(int(prodotto_id))
            if prodotto:
                prodotto.giacenza = (prodotto.giacenza or 0) + quantita_carico
                prodotto.disponibile = prodotto.giacenza > 0
                db.session.commit()
            return redirect(url_for("main.prodotti"))

        p = Prodotto(
            nome=request.form.get("nome"),
            image_url=request.form.get("image_url"),
            costo=float(request.form.get("costo") or 0),
            prezzo_pubblico=float(request.form.get("prezzo_pubblico") or 0),
            giacenza=float(request.form.get("giacenza") or 0),
            disponibile=bool(request.form.get("disponibile")),
            unita_misura=request.form.get("unita_misura") or "pz",
            descrizione=request.form.get("descrizione"),
        )
        db.session.add(p)
        db.session.flush()

        db.session.add(Confezione(prodotto_id=p.id, nome="Base", moltiplicatore=1, prezzo_extra=0))

        nome_conf = request.form.getlist("conf_nome[]")
        mult_conf = request.form.getlist("conf_moltiplicatore[]")

        for nome, mol in zip(nome_conf, mult_conf):
            if nome and mol:
                db.session.add(Confezione(
                    prodotto_id=p.id,
                    nome=nome,
                    moltiplicatore=float(mol),
                    prezzo_extra=0
                ))

        db.session.commit()
        return redirect(url_for("main.prodotti"))

    items = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("prodotti.html", prodotti=items)

@main.route("/listino")
def listino():
    prodotti = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("listino.html", prodotti=prodotti)
