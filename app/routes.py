from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from . import db
from .models import Cliente, Prodotto, Confezione, Ordine, RigaOrdine

main = Blueprint("main", __name__)


def seed_demo_data():
    """Inserisce alcuni prodotti demo solo se non esistono già."""
    demo = [
        {
            "nome": "Orata",
            "image_url": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?auto=format&fit=crop&w=900&q=80",
            "costo": 8.50,
            "prezzo_pubblico": 14.90,
            "giacenza": 48,
            "unita_misura": "pz",
            "descrizione": "Orata fresca da banco",
        },
        {
            "nome": "Spigola",
            "image_url": "https://images.unsplash.com/photo-1579631542720-3a87824fff86?auto=format&fit=crop&w=900&q=80",
            "costo": 9.20,
            "prezzo_pubblico": 16.50,
            "giacenza": 36,
            "unita_misura": "pz",
            "descrizione": "Spigola fresca ideale al forno",
        },
        {
            "nome": "Gamberi Rossi",
            "image_url": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=900&q=80",
            "costo": 18.00,
            "prezzo_pubblico": 28.00,
            "giacenza": 20,
            "unita_misura": "kg",
            "descrizione": "Gamberi rossi selezionati",
        },
        {
            "nome": "Calamari",
            "image_url": "https://images.unsplash.com/photo-1603048719539-9ecb6fdfaf20?auto=format&fit=crop&w=900&q=80",
            "costo": 10.50,
            "prezzo_pubblico": 18.50,
            "giacenza": 15,
            "unita_misura": "kg",
            "descrizione": "Calamari freschi",
        },
        {
            "nome": "Salmone",
            "image_url": "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?auto=format&fit=crop&w=900&q=80",
            "costo": 13.00,
            "prezzo_pubblico": 22.00,
            "giacenza": 24,
            "unita_misura": "tranci",
            "descrizione": "Tranci di salmone",
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

        confezioni_esistenti = {
            c.nome for c in Confezione.query.filter_by(prodotto_id=prodotto.id).all()
        }

        for nome_conf, moltiplicatore in [
            ("Base", 1),
            ("Confezione x2", 2),
            ("Confezione x5", 5),
        ]:
            if nome_conf not in confezioni_esistenti:
                db.session.add(
                    Confezione(
                        prodotto_id=prodotto.id,
                        nome=nome_conf,
                        moltiplicatore=moltiplicatore,
                        prezzo_extra=0,
                    )
                )

    db.session.commit()


def ricalcola_totale_ordine(ordine):
    """Ricalcola totale, quantità magazzino e stato consegna dell'ordine."""
    totale = 0.0

    for riga in ordine.righe:
        moltiplicatore = riga.confezione.moltiplicatore if riga.confezione else 1
        riga.quantita_magazzino = riga.quantita * moltiplicatore
        totale += riga.quantita * riga.prezzo_unitario

    ordine.totale = totale
    ordine.consegnato = all(r.evaso for r in ordine.righe) if ordine.righe else False

    if ordine.consegnato and ordine.righe:
        ordine.stato = "evaso"
    elif ordine.righe and ordine.stato == "evaso":
        ordine.stato = "in_preparazione"


@main.route("/")
def dashboard():
    seed_demo_data()
    clienti = Cliente.query.count()
    prodotti = Prodotto.query.count()
    ordini = Ordine.query.count()
    da_preparare = Ordine.query.filter(Ordine.stato != "evaso").count()
    recenti = Ordine.query.order_by(Ordine.data_ordine.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        clienti=clienti,
        prodotti=prodotti,
        ordini=ordini,
        da_preparare=da_preparare,
        recenti=recenti,
    )


@main.route("/nuovo-ordine")
def nuovo_ordine():
    seed_demo_data()
    prodotti = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    clienti = Cliente.query.order_by(Cliente.nome.asc()).all()
    return render_template("nuovo_ordine.html", prodotti=prodotti, clienti=clienti)


@main.route("/ordini")
def ordini():
    lista = Ordine.query.order_by(Ordine.data_ordine.desc()).all()
    return render_template("ordini.html", ordini=lista)


@main.route("/ordini/<int:ordine_id>", methods=["GET", "POST"])
def ordine_dettaglio(ordine_id):
    ordine = Ordine.query.get_or_404(ordine_id)

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "stato":
            nuovo_stato = request.form.get("stato", ordine.stato)
            ordine.stato = nuovo_stato
            ordine.consegnato = nuovo_stato == "evaso"

            if ordine.consegnato:
                for riga in ordine.righe:
                    riga.evaso = True

            ricalcola_totale_ordine(ordine)
            db.session.commit()
            flash("Stato ordine aggiornato.", "success")
            return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

        if action == "riga":
            riga_id = request.form.get("riga_id", type=int)
            riga = RigaOrdine.query.filter_by(id=riga_id, ordine_id=ordine.id).first_or_404()

            quantita = float(request.form.get("quantita") or 0)
            if quantita < 0:
                flash("La quantità non può essere negativa.", "warning")
                return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

            riga.quantita = quantita
            riga.evaso = request.form.get("evaso") == "1"
            riga.modificato = True

            ricalcola_totale_ordine(ordine)
            db.session.commit()
            flash("Riga ordine aggiornata.", "success")
            return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

        if action == "add_riga":
            prodotto_id = request.form.get("prodotto_id", type=int)
            confezione_id = request.form.get("confezione_id", type=int)
            quantita = float(request.form.get("quantita") or 0)

            if not prodotto_id or quantita <= 0:
                flash("Seleziona un prodotto e inserisci una quantità valida.", "warning")
                return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

            prodotto = Prodotto.query.get_or_404(prodotto_id)
            confezione = None

            if confezione_id:
                confezione = Confezione.query.filter_by(
                    id=confezione_id,
                    prodotto_id=prodotto.id,
                ).first()

            moltiplicatore = confezione.moltiplicatore if confezione else 1
            prezzo = (prodotto.prezzo_pubblico or 0) + (
                (confezione.prezzo_extra or 0) if confezione else 0
            )

            riga_esistente = RigaOrdine.query.filter_by(
                ordine_id=ordine.id,
                prodotto_id=prodotto.id,
                confezione_id=confezione.id if confezione else None,
            ).first()

            if riga_esistente:
                riga_esistente.quantita += quantita
                riga_esistente.prezzo_unitario = prezzo
                riga_esistente.modificato = True
            else:
                db.session.add(
                    RigaOrdine(
                        ordine_id=ordine.id,
                        prodotto_id=prodotto.id,
                        confezione_id=confezione.id if confezione else None,
                        quantita=quantita,
                        prezzo_unitario=prezzo,
                        quantita_magazzino=quantita * moltiplicatore,
                        evaso=False,
                        modificato=True,
                    )
                )
                db.session.flush()

            ricalcola_totale_ordine(ordine)
            db.session.commit()
            flash("Prodotto aggiunto all'ordine.", "success")
            return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

        if action == "delete_riga":
            riga_id = request.form.get("riga_id", type=int)
            riga = RigaOrdine.query.filter_by(id=riga_id, ordine_id=ordine.id).first_or_404()

            db.session.delete(riga)
            db.session.flush()

            ricalcola_totale_ordine(ordine)
            db.session.commit()
            flash("Riga eliminata dall'ordine.", "success")
            return redirect(url_for("main.ordine_dettaglio", ordine_id=ordine.id))

    prodotti = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("ordine_dettaglio.html", ordine=ordine, prodotti=prodotti)


@main.route("/prodotti", methods=["GET", "POST"])
def prodotti():
    seed_demo_data()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()

        if nome:
            giacenza = float(request.form.get("giacenza") or 0)

            prodotto = Prodotto(
                nome=nome,
                image_url=request.form.get("image_url", "").strip() or None,
                costo=float(request.form.get("costo") or 0),
                prezzo_pubblico=float(request.form.get("prezzo_pubblico") or 0),
                giacenza=giacenza,
                disponibile=giacenza > 0,
                unita_misura=request.form.get("unita_misura", "pz").strip() or "pz",
                descrizione=request.form.get("descrizione", "").strip() or None,
            )
            db.session.add(prodotto)
            db.session.commit()
            flash("Prodotto aggiunto correttamente.", "success")
        else:
            flash("Inserisci il nome del prodotto.", "warning")

        return redirect(url_for("main.prodotti"))

    prodotti_lista = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("prodotti.html", prodotti=prodotti_lista)


@main.route("/prodotti/<int:prodotto_id>/modifica", methods=["GET", "POST"])
def modifica_prodotto(prodotto_id):
    prodotto = Prodotto.query.get_or_404(prodotto_id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if nome:
            prodotto.nome = nome

        prodotto.image_url = request.form.get("image_url", "").strip() or None
        prodotto.costo = float(request.form.get("costo") or 0)
        prodotto.prezzo_pubblico = float(request.form.get("prezzo_pubblico") or 0)
        prodotto.giacenza = float(request.form.get("giacenza") or 0)
        prodotto.unita_misura = request.form.get("unita_misura", "pz").strip() or "pz"
        prodotto.descrizione = request.form.get("descrizione", "").strip() or None
        prodotto.disponibile = request.form.get("disponibile") == "1"

        db.session.commit()
        flash("Prodotto aggiornato correttamente.", "success")
        return redirect(url_for("main.prodotti"))

    return render_template("modifica_prodotto.html", prodotto=prodotto)


@main.route("/clienti", methods=["GET", "POST"])
def clienti():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()

        if nome:
            cliente = Cliente(
                nome=nome,
                telefono=request.form.get("telefono", "").strip() or None,
                via=request.form.get("via", "").strip() or None,
                citta=request.form.get("citta", "").strip() or None,
                cap=request.form.get("cap", "").strip() or None,
                note=request.form.get("note", "").strip() or None,
            )
            db.session.add(cliente)
            db.session.commit()
            flash("Cliente aggiunto correttamente.", "success")
        else:
            flash("Inserisci il nome del cliente.", "warning")

        return redirect(url_for("main.clienti"))

    lista = Cliente.query.order_by(Cliente.nome.asc()).all()
    return render_template("clienti.html", clienti=lista)


@main.route("/listino")
def listino():
    prodotti_lista = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("listino.html", prodotti=prodotti_lista)


@main.route("/api/ordina", methods=["POST"])
def api_ordina():
    data = request.get_json(force=True)
    cliente_id = data.get("cliente_id")
    articoli = data.get("articoli", [])
    note = data.get("note", "")

    if not articoli:
        return jsonify({"ok": False, "error": "Carrello vuoto"}), 400

    ordine = Ordine(
        cliente_id=cliente_id or None,
        stato="nuovo",
        consegnato=False,
        totale=0.0,
        note=note,
    )
    db.session.add(ordine)
    db.session.flush()

    totale = 0.0

    for it in articoli:
        prodotto = Prodotto.query.get(int(it["prodotto_id"]))
        if not prodotto:
            continue

        confezione = None
        confezione_id = it.get("confezione_id")
        if confezione_id:
            confezione = Confezione.query.get(int(confezione_id))

        qty = float(it.get("qty", 0))
        if qty <= 0:
            continue

        moltiplicatore = confezione.moltiplicatore if confezione else 1
        qty_magazzino = qty * moltiplicatore
        prezzo = float(it.get("prezzo_unit", prodotto.prezzo_pubblico if prodotto else 0))

        totale += qty * prezzo

        db.session.add(
            RigaOrdine(
                ordine_id=ordine.id,
                prodotto_id=prodotto.id,
                confezione_id=confezione.id if confezione else None,
                quantita=qty,
                prezzo_unitario=prezzo,
                quantita_magazzino=qty_magazzino,
                evaso=False,
                modificato=False,
            )
        )

        prodotto.giacenza = max(0, (prodotto.giacenza or 0) - qty_magazzino)
        prodotto.disponibile = prodotto.giacenza > 0

    ordine.totale = totale
    db.session.commit()

    return jsonify({"ok": True, "ordine_id": ordine.id})
