from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from sqlalchemy import func
from . import db
from .models import Cliente, Prodotto, Ordine, RigaOrdine

main = Blueprint("main", __name__)

def order_total(o):
    return sum((r.quantita or 0) * (r.prezzo_unitario or 0) for r in o.righe)

@main.route("/")
def dashboard():
    clienti = Cliente.query.count()
    prodotti = Prodotto.query.count()
    ordini = Ordine.query.count()
    da_preparare = Ordine.query.filter(Ordine.stato != "evaso").count()
    recenti = Ordine.query.order_by(Ordine.data_ordine.desc()).limit(5).all()
    return render_template("dashboard.html", clienti=clienti, prodotti=prodotti, ordini=ordini, da_preparare=da_preparare, recenti=recenti)

@main.route("/nuovo-ordine")
def nuovo_ordine():
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
        qty = float(it.get("qty", 0))
        prezzo = float(it.get("prezzo_unit", p.prezzo_pubblico if p else 0))
        totale += qty * prezzo
        db.session.add(RigaOrdine(ordine_id=ordine.id, prodotto_id=p.id, quantita=qty, prezzo_unitario=prezzo))
        if p:
            try:
                p.giacenza = max(0, (p.giacenza or 0) - qty)
                p.disponibile = p.giacenza > 0
            except Exception:
                pass

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
    if request.method == "POST":
        db.session.add(Prodotto(
            nome=request.form.get("nome"),
            image_url=request.form.get("image_url"),
            costo=float(request.form.get("costo") or 0),
            prezzo_pubblico=float(request.form.get("prezzo_pubblico") or 0),
            giacenza=float(request.form.get("giacenza") or 0),
            disponibile=bool(request.form.get("disponibile")),
            unita_misura=request.form.get("unita_misura") or "kg",
        ))
        db.session.commit()
        return redirect(url_for("main.prodotti"))
    items = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("prodotti.html", prodotti=items)

@main.route("/listino")
def listino():
    prodotti = Prodotto.query.order_by(Prodotto.nome.asc()).all()
    return render_template("listino.html", prodotti=prodotti)
