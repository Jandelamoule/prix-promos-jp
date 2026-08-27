#!/usr/bin/env python3
"""Relève quotidiennement les cotations Cardmarket (EUR) des cartes promo japonaises.

Source : les fichiers publics que Cardmarket met à disposition en libre accès depuis sa page
« Price Guides » — pas de compte, pas de clé d'API, mise à jour quotidienne.

  price_guide_6.json      cotations du jour, tous produits Pokémon
  products_singles_6.json catalogue des cartes (nom, extension), pour retrouver les promos

Sortie : prices.json  ->  { "<idProduct>": {"low":5.99,"tr":38.56,"a7":32.92,"a30":31.86} }
         products.json -> { "<idProduct>": {"n":"Pikachu (SV-P 001)","e":<idExpansion>} }

Exécuté par .github/workflows/prices.yml.
"""
import json, sys, gzip, io, pathlib
from urllib.request import urlopen, Request

BASE = "https://downloads.s3.cardmarket.com/productCatalog"
PRICE_URL = f"{BASE}/priceGuide/price_guide_6.json"      # 6 = Pokémon
CATALOG_URL = f"{BASE}/productList/products_singles_6.json"
TIMEOUT = 180

# Extensions Cardmarket retenues : les douze séries promo JAPONAISES, listées explicitement.
# Ne PAS filtrer sur le mot « Promos » dans le nom : l'extension 2107, nommée simplement
# « Promos », est le fourre-tout international (Staff Version, codes Worlds, promos portugaises,
# jumbos hors format) et n'a rien de japonais.
EXPANSIONS = {
    4159: "XY-P",    3324: "SM-P",   3214: "S-P",     5212: "SV-P",
    6230: "M-P",     4218: "BW-P",   4322: "DP-P",    4298: "DPt-P",
    4350: "ADV-P",   4341: "PCG-P",  4274: "L-P",     4170: "NN",
}


def charge(url):
    req = Request(url, headers={"User-Agent": "promo-jp-price-bot/2.0",
                                "Accept-Encoding": "gzip"})
    with urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def liste(doc, *cles):
    """Le fichier est soit une liste, soit un objet enveloppant la liste."""
    if isinstance(doc, list):
        return doc
    for c in cles:
        if isinstance(doc.get(c), list):
            return doc[c]
    for v in doc.values():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return v
    raise SystemExit(f"structure inattendue : {list(doc)[:8]}")


def main():
    here = pathlib.Path(__file__).parent

    cat = liste(charge(CATALOG_URL), "products", "productList")
    print(f"catalogue : {len(cat)} produits")

    # Un produit = une carte. On garde son nom et son extension pour le rapprochement.
    produits = {}
    for p in cat:
        pid = p.get("idProduct") or p.get("id")
        exp = p.get("idExpansion")
        if pid is None or exp not in EXPANSIONS:
            continue
        produits[str(pid)] = {"n": p.get("name") or "", "e": exp, "s": EXPANSIONS[exp]}
    print(f"{len(produits)} produits retenus sur les {len(EXPANSIONS)} séries promo japonaises")

    doc_prix = charge(PRICE_URL)
    pgd_date = doc_prix.get("createdAt") if isinstance(doc_prix, dict) else None
    pg = liste(doc_prix, "priceGuides", "price_guides")
    print(f"guide de prix : {len(pg)} cotations")

    prix = {}
    for e in pg:
        pid = e.get("idProduct") or e.get("id")
        if pid is None or str(pid) not in produits:
            continue
        low, trend = e.get("low"), e.get("trend")
        if low is None and trend is None:
            continue
        prix[str(pid)] = {"low": low, "tr": trend,
                          "a7": e.get("avg7"), "a30": e.get("avg30")}

    if len(prix) < 2000:
        sys.exit(f"ERREUR : seulement {len(prix)} cotations retenues, relevé abandonné")

    json.dump(prix, open(here / "prices.json", "w"), ensure_ascii=False, indent=0, sort_keys=True)
    json.dump(produits, open(here / "products.json", "w"), ensure_ascii=False, indent=0, sort_keys=True)
    # date du relevé, telle que Cardmarket la publie — build.py l'affiche en pied de page
    json.dump({"date": (pgd_date or "")[:10]}, open(here / "releve.json", "w"))
    print(f"prices.json : {len(prix)} cotations · products.json : {len(produits)} produits"
          f" · relevé du {(pgd_date or '?')[:10]}")


if __name__ == "__main__":
    main()
