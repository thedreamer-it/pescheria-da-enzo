from app import create_app, db
from app.models import Cliente, Prodotto, Ordine, RigaOrdine

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    c1 = Cliente(nome="Mario Rossi", telefono="3331234567", via="Via del Porto 12", citta="Ancona", cap="60121", note="Consegna pomeriggio")
    c2 = Cliente(nome="Anna Bianchi", telefono="3207654321", via="Via Mare 8", citta="Pesaro", cap="61121", note="Ordina spesso il venerdì")

    p1 = Prodotto(nome="Orata", image_url="https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=900&q=80", costo=12.00, prezzo_pubblico=18.50, giacenza=12, disponibile=True, unita_misura="kg")
    p2 = Prodotto(nome="Gamberi Rossi", image_url="https://images.unsplash.com/photo-1604908813191-26f8d4d5f7b1?auto=format&fit=crop&w=900&q=80", costo=21.00, prezzo_pubblico=32.00, giacenza=6, disponibile=True, unita_misura="kg")
    p3 = Prodotto(nome="Calamari", image_url="https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?auto=format&fit=crop&w=900&q=80", costo=14.50, prezzo_pubblico=22.00, giacenza=9, disponibile=False, unita_misura="kg")

    db.session.add_all([c1, c2, p1, p2, p3])
    db.session.commit()

    o1 = Ordine(cliente_id=c1.id, stato="nuovo", totale=37.0, note="2 kg orata")
    o2 = Ordine(cliente_id=c2.id, stato="in_preparazione", totale=22.0, note="1 kg calamari")
    db.session.add_all([o1, o2])
    db.session.commit()

    r1 = RigaOrdine(ordine_id=o1.id, prodotto_id=p1.id, quantita=2.0, prezzo_unitario=18.50)
    r2 = RigaOrdine(ordine_id=o2.id, prodotto_id=p3.id, quantita=1.0, prezzo_unitario=22.00)
    db.session.add_all([r1, r2])
    db.session.commit()

    print("Database inizializzato con dati demo v2.")
