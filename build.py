#!/usr/bin/env python3
"""Génère la page 'Radar Promos JP' à partir de cards.json (statique) et prices.json (frais)."""
import json, sys, datetime, html, pathlib

HERE = pathlib.Path(__file__).parent
cards = json.load(open(HERE / "cards.json", encoding="utf-8"))

# prices.json optionnel, produit par la GitHub Action : {idProduct: {low, tr, a7, a30}}
# La clé est l'identifiant produit Cardmarket, pas l'identifiant de carte.
pf = HERE / "prices.json"
if pf.exists():
    fresh = json.load(open(pf, encoding="utf-8"))
    releve = (json.load(open(HERE / "releve.json", encoding="utf-8")).get("date")
              if (HERE / "releve.json").exists() else None)
    maj = 0
    for c in cards:
        p = fresh.get(str(c.get("cmId")))
        if p:
            c["low"], c["trend"] = p.get("low"), p.get("tr")
            c["a7"], c["a30"] = p.get("a7"), p.get("a30")
            if releve:
                c["up"] = releve
            maj += 1
    print(f"{maj} cotations rafraîchies depuis prices.json")

updated = max([c["up"] for c in cards if c.get("up")] or ["?"])
gen = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Sépare vignettes et métadonnées pour que la mise à jour quotidienne ne touche qu'un bloc
meta = [{k: v for k, v in c.items() if k != "thumb"} for c in cards]
thumbs = {c["id"]: c["thumb"] for c in cards if c.get("thumb")}

ORDRE = ["SV-P", "M-P", "S-P", "SM-P", "XY-P", "BW-P", "DPt-P", "DP-P",
         "L-P", "PCG-P", "ADV-P", "NN"]
import collections
_n = collections.Counter(c["set"] for c in cards)
_lab = {c["set"]: c.get("setLabel") or c["set"] for c in cards}
serie_opts = "".join(
    f'<option value="{s}">{s} — {html.escape(_lab.get(s, s))} · {_n[s]}</option>'
    for s in ORDRE if _n.get(s))

page = """<title>Radar Promos JP</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap">
<style>
:root{
  --ground:#F4F2EC; --surface:#FFFFFF; --surface-2:#EDEAE1; --line:#D9D4C7;
  --ink:#17181D; --ink-2:#55545C; --ink-3:#8C8A90;
  --gold:#A9761A; --gold-soft:#F0E0BC;
  --cheap:#1F7A6B; --mid:#8A7A2E; --dear:#A83E38;
  --shadow:0 1px 2px rgba(20,18,10,.06),0 8px 20px rgba(20,18,10,.05);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#111319; --surface:#191C23; --surface-2:#232730; --line:#31353F;
    --ink:#ECEAE3; --ink-2:#A5A3A8; --ink-3:#74737A;
    --gold:#E3AE41; --gold-soft:#3A3018;
    --cheap:#4FC0AB; --mid:#D2BC5E; --dear:#E8756D;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --ground:#111319; --surface:#191C23; --surface-2:#232730; --line:#31353F;
  --ink:#ECEAE3; --ink-2:#A5A3A8; --ink-3:#74737A;
  --gold:#E3AE41; --gold-soft:#3A3018;
  --cheap:#4FC0AB; --mid:#D2BC5E; --dear:#E8756D;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Zen Kaku Gothic New",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1360px;margin:0 auto;padding:28px 20px 72px}
header.top{display:flex;flex-wrap:wrap;align-items:flex-end;gap:20px 28px;margin-bottom:22px}
h1{font-size:26px;font-weight:700;margin:0;letter-spacing:-.01em;text-wrap:balance}
h1 .jp{color:var(--gold);font-weight:500}
.sub{margin:4px 0 0;color:var(--ink-2);font-size:13.5px;max-width:62ch}
.stats{display:flex;gap:22px;margin-left:auto;flex-wrap:wrap}
.stat{min-width:76px}
.stat b{display:block;font-family:"Roboto Mono",ui-monospace,monospace;font-size:20px;font-weight:500;font-variant-numeric:tabular-nums;line-height:1.2}
.stat span{display:block;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-top:2px}

.controls{position:sticky;top:0;z-index:20;background:var(--ground);padding:10px 0 12px;border-bottom:1px solid var(--line);margin-bottom:20px}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.row + .row{margin-top:9px}
input[type=search],select{
  font-family:inherit;font-size:13.5px;color:var(--ink);background:var(--surface);
  border:1px solid var(--line);border-radius:7px;padding:7px 10px;
}
input[type=search]{min-width:230px;flex:0 1 300px}
input[type=search]:focus-visible,select:focus-visible,.chip:focus-visible,button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.chip{
  font:inherit;font-size:12.5px;cursor:pointer;background:var(--surface);color:var(--ink-2);
  border:1px solid var(--line);border-radius:99px;padding:6px 13px;transition:background .12s,color .12s,border-color .12s;
}
.chip:hover{border-color:var(--gold)}
.chip[aria-pressed="true"]{background:var(--gold-soft);border-color:var(--gold);color:var(--ink);font-weight:500}
.grouplabel{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-right:2px}
.count{margin-left:auto;font-size:12.5px;color:var(--ink-2);font-variant-numeric:tabular-nums}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(136px,1fr));gap:12px}
.card{
  background:var(--surface);border:1px solid var(--line);border-radius:11px;overflow:hidden;
  box-shadow:var(--shadow);display:flex;flex-direction:column;text-align:left;
  font:inherit;color:inherit;padding:0;cursor:pointer;transition:transform .13s ease,border-color .13s;
}
.card:hover{transform:translateY(-2px);border-color:var(--gold)}
.thumbbox{position:relative;background:var(--surface-2);aspect-ratio:63/88;display:flex;align-items:center;justify-content:center}
.thumbbox.empty{aspect-ratio:auto;min-height:46px;border-bottom:1px solid var(--line)}
.thumbbox img{width:100%;height:100%;object-fit:cover;display:block}
.noimg{font-size:11.5px;color:var(--ink-3);text-align:center;padding:12px;line-height:1.4}
.tag{
  position:absolute;bottom:6px;right:6px;font-size:9px;letter-spacing:.07em;text-transform:uppercase;
  background:rgba(18,16,10,.78);color:#F2D9A0;padding:2px 6px;border-radius:4px;font-weight:500;
  backdrop-filter:blur(2px);
}
.tag-soon{background:rgba(31,122,107,.9);color:#EAFBF6}
.fav{
  position:absolute;top:5px;left:5px;width:22px;height:22px;line-height:21px;text-align:center;
  border-radius:50%;font-size:13px;cursor:pointer;user-select:none;
  background:rgba(18,16,10,.55);color:rgba(255,255,255,.72);backdrop-filter:blur(2px);
  transition:transform .12s,color .12s,background .12s;
}
.fav:hover{transform:scale(1.12);color:#F2D9A0}
.fav.on{background:var(--gold);color:#1B1508}
.fav:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.chip-fav .st{color:var(--gold)}
.chip-fav em{font-style:normal;font-variant-numeric:tabular-nums;color:var(--ink-3);margin-left:2px}
.chip-fav[aria-pressed="true"] em{color:var(--ink)}
.chip:disabled{opacity:.45;cursor:not-allowed}
.dfav{
  font:inherit;font-size:12.5px;cursor:pointer;border:1px solid var(--line);border-radius:7px;
  padding:6px 11px;background:var(--surface-2);color:var(--ink);
}
.dfav.on{background:var(--gold);border-color:var(--gold);color:#1B1508;font-weight:500}
.meta{padding:8px 9px 10px;display:flex;flex-direction:column;gap:2px;flex:1}
.nm{font-size:12.5px;font-weight:500;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.ja{font-size:11.5px;color:var(--ink-3)}
.ref{font-family:"Roboto Mono",monospace;font-size:10.5px;color:var(--ink-3);letter-spacing:.02em}
.diff{display:flex;align-items:center;gap:6px;margin-top:8px;font-size:10.5px;color:var(--ink-2)}
.diff em{font-style:normal;font-variant-numeric:tabular-nums}
.mtr{display:inline-flex;gap:2px;flex:none}
.mtr i{width:5px;height:11px;border-radius:1px;background:var(--surface-2);border:1px solid var(--line)}
.mtr i.on{border-color:transparent}
.mtr i.on.l1{background:#8E2F2A}.mtr i.on.l2{background:#B8632B}
.mtr i.on.l3{background:#9A8A2E}.mtr i.on.l4{background:#4E8C6A}.mtr i.on.l5{background:#7C8794}
.how{display:flex;align-items:center;gap:5px;margin-top:6px;font-size:11px;font-weight:500;color:var(--ink)}
.k{width:7px;height:7px;border-radius:2px;flex:none;background:var(--ink-3)}
.k-achat{background:#C98A1F}.k-boutique{background:#3F7FBF}.k-tournoi{background:#B05252}
.k-campagne{background:#8A6BC0}.k-produit{background:#2E8B7F}.k-magazine{background:#C06BA0}
.k-collaboration{background:#5FA03C}.k-jeu-vidéo{background:#3C7A8F}.k-concours{background:#9A8A2E}
.src{font-size:11px;color:var(--ink-2);margin-top:2px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;line-height:1.35}
.price{display:flex;align-items:baseline;gap:6px;margin-top:auto;padding-top:6px;font-family:"Roboto Mono",monospace;font-variant-numeric:tabular-nums}
.price b{font-size:15px;font-weight:500;white-space:nowrap}
.price small{font-size:10.5px;color:var(--ink-3);white-space:nowrap}
.b-cheap b{color:var(--cheap)} .b-mid b{color:var(--mid)} .b-dear b{color:var(--dear)}
.b-none b{color:var(--ink-3);font-size:13px}

dialog{
  border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);
  padding:0;max-width:min(620px,92vw);box-shadow:0 24px 60px rgba(0,0,0,.35);
}
dialog::backdrop{background:rgba(10,10,14,.55)}
.dwrap{display:flex;gap:18px;padding:20px}
.dwrap img{width:190px;border-radius:8px;align-self:flex-start;background:var(--surface-2)}
.dinfo{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}
.dinfo h2{margin:0;font-size:20px;font-weight:700}
.dl{display:grid;grid-template-columns:auto 1fr;gap:3px 14px;margin:12px 0 0;font-size:13px}
.dl dt{color:var(--ink-3);font-size:11px;letter-spacing:.06em;text-transform:uppercase;align-self:center}
.dl dd{margin:0;font-family:"Roboto Mono",monospace;font-variant-numeric:tabular-nums}
.dl dd.txt{font-family:inherit;font-size:13px}
.howfull{display:block;margin-top:4px;font-size:12.5px;color:var(--ink-2);line-height:1.45}
.dl dd.est{border-left:2px dashed var(--line);padding-left:9px;margin-left:-2px}
.dl dd.est .mtr{vertical-align:-1px}
.links{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}
.links a{
  font-size:12.5px;text-decoration:none;color:var(--ink);background:var(--surface-2);
  border:1px solid var(--line);border-radius:7px;padding:6px 11px;
}
.links a:hover{border-color:var(--gold);color:var(--gold)}
.close{position:absolute;top:10px;right:12px;background:none;border:0;color:var(--ink-3);font-size:22px;cursor:pointer;line-height:1}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:var(--ink-3);font-size:12px;line-height:1.7}
footer a{color:var(--ink-2)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media (max-width:620px){
  .dwrap{flex-direction:column}.dwrap img{width:150px;align-self:center}
  .stats{margin-left:0}
}
</style>

<div class="wrap">
  <header class="top">
    <div>
      <h1>Radar Promos <span class="jp">プロモ</span></h1>
      <p class="sub">Uniquement des <strong>cartes promo japonaises</strong> — jamais les extensions principales. Prix Cardmarket en euros, triés du moins cher au plus cher&nbsp;: l'offre la plus basse du marché, la tendance en repère.</p>
    </div>
    <div class="stats" id="stats"></div>
  </header>

  <div class="controls">
    <div class="row">
      <input type="search" id="q" placeholder="Rechercher un nom, un illustrateur, un numéro…" aria-label="Rechercher">
      <select id="sort" aria-label="Trier">
        <optgroup label="Prix">
          <option value="low-asc">Prix croissant</option>
          <option value="low-desc">Prix décroissant</option>
          <option value="trend-asc">Tendance croissante</option>
          <option value="trend-desc">Tendance décroissante</option>
          <option value="gap">Meilleure décote (offre vs tendance)</option>
        </optgroup>
        <optgroup label="Ancienneté">
          <option value="date-asc">Des plus anciennes aux plus récentes</option>
          <option value="date-desc">Des plus récentes aux plus anciennes</option>
        </optgroup>
        <optgroup label="Rareté">
          <option value="diff">Diffusion la plus restreinte</option>
        </optgroup>
        <optgroup label="Référence">
          <option value="num">Numéro de carte</option>
        </optgroup>
      </select>
      <select id="kind" aria-label="Filtrer par mode d'obtention">
        <option value="">Toute obtention</option>
        <option value="achat">Cadeau à l'achat en boutique</option>
        <option value="boutique">Événement en boutique</option>
        <option value="tournoi">Tournoi officiel</option>
        <option value="campagne">Campagne promotionnelle</option>
        <option value="produit">Vendue en produit</option>
        <option value="magazine">Magazine</option>
        <option value="collaboration">Collaboration de marque</option>
        <option value="jeu vidéo">Bonus de jeu vidéo</option>
        <option value="concours">Concours</option>
      </select>
      <span class="count" id="count"></span>
    </div>
    <div class="row">
      <span class="grouplabel">Série</span>
      <select id="serie" aria-label="Série"><option value="">Toutes les séries</option>SERIEOPTS</select>
      <span class="grouplabel" style="margin-left:14px">Affiner</span>
      <button class="chip" id="f-fa" aria-pressed="false">Full art</button>
      <button class="chip" id="f-img" aria-pressed="false">Avec illustration</button>
      <button class="chip" id="f-doc" aria-pressed="false">Obtention documentée</button>
      <button class="chip" id="f-priced" aria-pressed="true">Coté seulement</button>
      <button class="chip chip-fav" id="f-star" aria-pressed="false"><span class="st">★</span> Favoris <em id="favn"></em></button>
    </div>
  </div>

  <div class="grid" id="grid"></div>

  <footer>
    <p><strong>Sources.</strong> Prix&nbsp;: fichiers publics de Cardmarket (<em>price guide</em> et catalogue produits, mis à jour quotidiennement, en libre accès), relevé du <span id="upd"></span>. Visuels et fiches&nbsp;: site officiel Pokémon Card Japon. Mode d'obtention et date de publication&nbsp;: Bulbapedia, colonne <em>Promotion</em>, traduite. Page générée le GENDATE.</p>
    <p><strong>Périmètre&nbsp;: douze séries promo, aucune extension principale.</strong> Les séries promo japonaises portent un suffixe <em>-P</em> — DP-P, DPt-P, L-P, BW-P, XY-P, SM-P, S-P, SV-P, M-P, ADV-P, PCG-P — auxquelles s'ajoutent les promos japonaises non numérotées. Une carte listée «&nbsp;Promos Diamant&nbsp;&amp;&nbsp;Perle&nbsp;» vient de la série <em>DP-P</em>, distribuée en dehors des boosters (cartes bonus des snacks Meiji, cartes d'échange, Gym Challenge, McDonald's)&nbsp;; elle n'appartient pas à l'extension Diamant&nbsp;&amp;&nbsp;Perle vendue en boutique. L'extension Cardmarket intitulée simplement «&nbsp;Promos&nbsp;» est <em>exclue</em>&nbsp;: c'est un fourre-tout international — cartes «&nbsp;Staff Version&nbsp;», codes en ligne des Mondiaux, promos portugaises, jumbos hors format.</p>
    <p><strong>Couverture.</strong> <strong>2&nbsp;614 cartes sur 2&nbsp;638 ont leur illustration</strong>, tirée du catalogue Cardmarket. <strong>2&nbsp;031 portent leur numéro de série, 1&nbsp;931 leur mode d'obtention et 1&nbsp;399 une date</strong> — 764 au jour près, 635 à l'année. Les intitulés de carte affichés sont ceux de Cardmarket, donc en anglais&nbsp;: cela ne veut pas dire que la carte l'est.</p>
    <p><strong>Comment le numéro et l'origine ont été rattachés.</strong> Cardmarket ne publie pas le numéro de série&nbsp;; Bulbapedia le publie mais pas l'identifiant Cardmarket. Les deux listes d'une même série sont ordonnées de la même façon, ce qui permet un alignement de séquence n'acceptant une paire que si les deux noms de carte <em>coïncident exactement</em>. Contrôle avant application&nbsp;: l'alignement a été rejoué sur 389 cartes dont le numéro était déjà connu par une autre source — <strong>389 justes, 0 fausse</strong>. Les cartes qu'il n'a pas pu apparier restent sans numéro plutôt que d'être devinées.</p>
    <p><strong>Traduction.</strong> Les intitulés d'obtention des séries anciennes viennent de Bulbapedia en anglais et sont traduits par règles de phrase — le sens reste celui de la source. 98&nbsp;% des intitulés sont entièrement en français&nbsp;; les noms propres (Meiji Chocolate, Battle Road, Trade Please DP) sont conservés tels quels.</p>
    <p><strong>Dates et obtention.</strong> Le descriptif est celui de la source, carte par carte — pas une règle générale appliquée à une famille de cartes. Quand une carte a circulé par plusieurs canaux, ils sont tous listés et la date retenue est celle de la <em>première</em> distribution. Les cartes marquées «&nbsp;à paraître&nbsp;» ont une date de sortie annoncée postérieure à aujourd'hui — leur cote existe déjà en précommande, mais leur visuel n'est pas encore publié.</p>
    <p><strong>Diffusion&nbsp;: une estimation, pas un tirage.</strong> The Pokémon Company n'a jamais publié de chiffre de tirage, pour aucune carte — la fourchette affichée est <em>déduite du canal de distribution documenté</em> et signalée partout par le signe «&nbsp;~&nbsp;» et un trait pointillé. Cinq niveaux, de «&nbsp;quelques dizaines&nbsp;» (lot du vainqueur d'un tournoi national) à «&nbsp;plus d'un million&nbsp;» (bonus d'un jeu à succès). Contrôle de cohérence sur les 1&nbsp;650 cartes classées&nbsp;: le prix médian décroît du niveau&nbsp;1 au niveau&nbsp;5 — 19,49&nbsp;€, 15,99&nbsp;€, 15,79&nbsp;€, 6,20&nbsp;€, 1,50&nbsp;€. L'ordre tient, mais l'écart entre les trois premiers niveaux est faible&nbsp;: sur les séries anciennes, la rareté joue moins que l'âge et la demande. À prendre comme un indice, pas comme une mesure.</p>
    <p><strong>Favoris.</strong> L'étoile en haut à gauche d'une carte la met de côté, et la puce «&nbsp;Favoris&nbsp;» n'affiche plus qu'elles. La liste est enregistrée <em>dans ce navigateur seulement</em>&nbsp;: elle n'est ni transmise, ni partagée avec les personnes à qui vous ouvririez la page, et ne suit pas d'un appareil à l'autre. Elle survit en revanche aux actualisations quotidiennes de la page, parce qu'elle est indexée sur l'identifiant produit Cardmarket, qui ne bouge pas. Un navigateur en navigation privée, ou réglé pour bloquer le stockage des sites, désactive la fonction — la puce apparaît alors grisée.</p>
    <p><strong>Détection «&nbsp;full art&nbsp;».</strong> Les promos japonaises ne portent pas de marque de rareté&nbsp;: le classement full art est <em>déduit automatiquement de l'analyse du visuel</em>, et n'existe donc que pour les cartes qui en ont un. Ce n'est pas une donnée publiée par l'éditeur.</p>
  </footer>
</div>

<dialog id="dlg"><button class="close" id="dclose" aria-label="Fermer">&times;</button><div class="dwrap" id="dbody"></div></dialog>

<script id="cards-meta" type="application/json">METAJSON</script>
<script id="cards-thumbs" type="application/json">THUMBJSON</script>
<script>
(function(){
  const META=JSON.parse(document.getElementById('cards-meta').textContent);
  const TH=JSON.parse(document.getElementById('cards-thumbs').textContent);
  META.forEach(c=>{c.thumb=TH[c.id]||null; if(!c.trend)c.trend=null; if(!c.a7)c.a7=null; if(!c.a30)c.a30=null;});

  const state={fa:false, img:false, doc:false, star:false, serie:'', priced:true, q:'', sort:'low-asc', kind:''};

  // --- Favoris : stockés dans le navigateur du lecteur, jamais transmis ni partagés.
  // Clé = identifiant produit Cardmarket (stable), pas l'identifiant de carte qui peut
  // changer si la carte gagne un numéro de série lors d'une mise à jour.
  const CLE='radar-promos-jp/favoris/v1';
  let dispo=true;
  function lire(){
    try{ return new Set(JSON.parse(localStorage.getItem(CLE)||'[]')); }
    catch(e){ dispo=false; return new Set(); }
  }
  const FAV=lire();
  function ecrire(){
    if(!dispo) return;
    try{ localStorage.setItem(CLE, JSON.stringify([...FAV])); }
    catch(e){ dispo=false; }
  }
  function estFav(c){ return FAV.has(String(c.cmId)); }
  function bascule(c){
    const k=String(c.cmId);
    FAV.has(k) ? FAV.delete(k) : FAV.add(k);
    ecrire(); majFav(); render();
  }
  function majFav(){
    const n=FAV.size;
    document.getElementById('favn').textContent = n ? n : '';
    const b=document.getElementById('f-star');
    b.disabled = !dispo && n===0;
    b.title = dispo ? 'Afficher seulement les cartes mises en favori'
                    : 'Ce navigateur n’autorise pas l’enregistrement local';
  }
  const grid=document.getElementById('grid'), countEl=document.getElementById('count');
  const eur=n=>n==null?'—':n.toFixed(2).replace('.',',')+' €';
  const MOIS=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
  const TODAY=new Date().toISOString().slice(0,10);
  const dshort=c=>c.date?MOIS[+c.date.slice(5,7)-1]+' '+c.date.slice(0,4):(c.annee||'');
  const dlong=c=>c.date?c.date.slice(8,10).replace(/^0/,'')+' '+MOIS[+c.date.slice(5,7)-1]+' '+c.date.slice(0,4)
    :(c.annee?'courant '+c.annee:'date inconnue');
  const future=c=>c.date&&c.date>TODAY;

  function band(c){
    if(c.low==null) return 'b-none';
    if(c.low<1) return 'b-cheap';
    if(c.low<10) return 'b-mid';
    return 'b-dear';
  }
  function visible(){
    let r=META;
    if(state.serie) r=r.filter(c=>c.set===state.serie);
    if(state.fa) r=r.filter(c=>c.fa);
    if(state.img) r=r.filter(c=>c.thumb);
    if(state.doc) r=r.filter(c=>c.src);
    if(state.star) r=r.filter(estFav);
    if(state.priced) r=r.filter(c=>c.low!=null);
    if(state.kind) r=r.filter(c=>c.srcKind===state.kind);
    const q=state.q.trim().toLowerCase();
    if(q) r=r.filter(c=>[c.fr,c.en,c.ja,c.cmName,c.ill,c.id,c.src,String(c.num)].some(v=>v&&String(v).toLowerCase().includes(q)));
    const s=state.sort;
    const key={'low-asc':c=>c.low??1e9,'low-desc':c=>-(c.low??-1),
      'trend-asc':c=>c.trend??1e9,'trend-desc':c=>-(c.trend??-1),
      'gap':c=>(c.low!=null&&c.trend)?c.low/c.trend:1e9,
      'diff':c=>c.diff??9,
      'date-asc':c=>c.date?+c.date.replace(/-/g,''):(c.annee?+c.annee*10000+615:1e9),
      'date-desc':c=>c.date?-c.date.replace(/-/g,''):(c.annee?-(+c.annee*10000+615):1e9),
      'num':c=>c.num}[s];
    r.sort((a,b)=>{const x=key(a),y=key(b);return x===y?a.num-b.num:x-y;});
    return r;
  }
  function render(){
    const rows=visible();
    countEl.textContent=rows.length+' carte'+(rows.length>1?'s':'');
    grid.innerHTML='';
    const frag=document.createDocumentFragment();
    for(const c of rows){
      const el=document.createElement('button');
      el.className='card '+band(c); el.type='button';
      const label=nom(c);
      el.innerHTML=
        '<div class="thumbbox'+(c.thumb?'':' empty')+'">'+(c.thumb
          ? '<img loading="lazy" alt="'+esc(label)+'" src="'+c.thumb+'">'
          : '<div class="noimg">'+(future(c)?'visuel pas encore<br>publié':'visuel<br>non rattaché')+'</div>')
        +(future(c)?'<span class="tag tag-soon">à paraître</span>'
          :(c.fa?'<span class="tag">'+(c.energy?'Énergie':'Full art')+'</span>':''))
        +'<span class="fav'+(estFav(c)?' on':'')+'" role="button" tabindex="0" aria-pressed="'+estFav(c)+'" aria-label="'+(estFav(c)?'Retirer des favoris':'Mettre en favori')+'">★</span>'
        +'</div>'
        +'<div class="meta"><span class="nm">'+esc(label)+'</span>'
        +(c.ja&&(c.fr||c.en)?'<span class="ja">'+esc(c.ja)+'</span>':'')
        +'<span class="ref">'+ref(c)+((c.date||c.annee)?' · '+dshort(c):'')+'</span>'
        +(c.diff?'<span class="diff" title="Ordre de grandeur estimé, pas un tirage officiel">'+meter(c.diff)+'<em>~ '+esc(c.diffLabel)+'</em></span>':'')
        +(c.srcTag?'<span class="how"><i class="k k-'+c.srcKind.replace(/ /g,'-')+'"></i>'+esc(c.srcTag)+'</span>':'')
        +(c.src?'<span class="src">'+esc(c.src)+'</span>':'')
        +'<span class="price"><b>'+eur(c.low)+'</b><small>tend. '+eur(c.trend)+'</small></span></div>';
      el.addEventListener('click',e=>{
        const st=e.target.closest('.fav');
        if(st){ e.preventDefault(); e.stopPropagation(); bascule(c); return; }
        open(c);
      });
      el.addEventListener('keydown',e=>{
        if((e.key===' '||e.key==='Enter') && e.target.closest('.fav')){ e.preventDefault(); bascule(c); }
      });
      frag.appendChild(el);
    }
    grid.appendChild(frag);
    stats(rows);
  }
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}
  function nom(c){return c.fr||c.en||c.ja||(c.cmName||'').replace(/\s*\[.*$/,'')||'—';}
  function ref(c){return c.num?c.set+' '+String(c.num).padStart(3,'0'):c.set+' · réf. Cardmarket';}
  function meter(l){let s='<span class="mtr" aria-hidden="true">';for(let i=1;i<=5;i++)s+='<i'+(i<=l?' class="on l'+l+'"':'')+'></i>';return s+'</span>';}
  function stats(rows){
    const p=rows.map(c=>c.low).filter(v=>v!=null).sort((a,b)=>a-b);
    const med=p.length?p[Math.floor(p.length/2)]:null;
    const under=p.filter(v=>v<2).length;
    document.getElementById('stats').innerHTML=
      st(rows.length,'affichées')+st(p.length?eur(p[0]):'—','moins chère')+st(med!=null?eur(med):'—','médiane')+st(under,'sous 2 €');
  }
  const st=(v,l)=>'<div class="stat"><b>'+v+'</b><span>'+l+'</span></div>';

  const dlg=document.getElementById('dlg'), dbody=document.getElementById('dbody');
  function open(c){
    const label=nom(c);
    const cmq=encodeURIComponent(c.cmName||((c.en||c.ja||'')+' '+c.set));
    const gap=(c.low!=null&&c.trend)?Math.round((1-c.low/c.trend)*100):null;
    dbody.innerHTML=
      (c.thumb?'<img alt="'+esc(label)+'" src="'+c.thumb+'">':'')
      +'<div class="dinfo"><h2>'+esc(label)+'</h2>'
      +(c.ja?'<div class="ja">'+esc(c.ja)+'</div>':'')
      +'<div class="ref">'+ref(c)+' · '+esc(c.setLabel||c.set)+(c.ill?' · ill. '+esc(c.ill):'')+'</div>'
      +(c.cmName&&c.cmName!==label?'<div class="ja">Cardmarket&nbsp;: '+esc(c.cmName)+'</div>':'')
      +'<dl class="dl">'
      +((c.date||c.annee||c.num)?'<dt>Publication</dt><dd class="txt">'+dlong(c)+(future(c)?' — à paraître':'')+'</dd>':'')
      +(c.diff?'<dt>Diffusion</dt><dd class="txt est">'+meter(c.diff)+' <b>~ '+esc(c.diffLabel)+'</b> d’exemplaires'
        +'<span class="howfull">Estimation, pas un tirage officiel — aucun n’est publié. '+esc(c.diffWhy)+'</span></dd>':'')
      +'<dt>Obtention</dt><dd class="txt">'+(c.src
          ? esc(c.src)+(c.srcTag?'<span class="howfull">Catégorie&nbsp;: '+esc(c.srcTag)+'</span>':'')
          : 'non documentée<span class="howfull">Cette carte vient du catalogue Cardmarket ; son numéro, son visuel et son mode d’obtention n’ont pas encore été rattachés.</span>')+'</dd>'
      +'<dt>Offre basse</dt><dd>'+eur(c.low)+'</dd>'
      +'<dt>Tendance</dt><dd>'+eur(c.trend)+(gap!=null&&gap>0?'  ('+gap+' % sous la tendance)':'')+'</dd>'
      +'<dt>Moy. 7 j</dt><dd>'+eur(c.a7)+'</dd>'
      +'<dt>Moy. 30 j</dt><dd>'+eur(c.a30)+'</dd>'
      +'</dl><div class="links">'
      +'<button type="button" class="dfav'+(estFav(c)?' on':'')+'" id="dfav">'+(estFav(c)?'★ En favori':'☆ Mettre en favori')+'</button>'
      +(c.big?'<a href="'+c.big+'" target="_blank" rel="noopener">Visuel haute définition</a>':'')
      +(c.jp?'<a href="https://www.pokemon-card.com/card-search/details.php/card/'+c.jp+'" target="_blank" rel="noopener">Fiche officielle</a>':'')
      +'<a href="https://www.cardmarket.com/fr/Pokemon/Products/Search?searchString='+cmq+'" target="_blank" rel="noopener">Chercher sur Cardmarket</a>'
      +'</div></div>';
    const bf=document.getElementById('dfav');
    if(bf) bf.onclick=()=>{ bascule(c); open(c); };
    dlg.showModal();
  }
  document.getElementById('dclose').addEventListener('click',()=>dlg.close());
  dlg.addEventListener('click',e=>{if(e.target===dlg)dlg.close();});

  for(const [id,key] of [['f-fa','fa'],['f-img','img'],['f-doc','doc'],['f-priced','priced'],['f-star','star']]){
    document.getElementById(id).onclick=function(){
      state[key]=!state[key]; this.setAttribute('aria-pressed',String(state[key])); render();
    };
  }
  document.getElementById('serie').addEventListener('change',e=>{state.serie=e.target.value;render();});
  document.getElementById('kind').addEventListener('change',e=>{state.kind=e.target.value;render();});
  document.getElementById('q').addEventListener('input',e=>{state.q=e.target.value;render();});
  document.getElementById('sort').addEventListener('change',e=>{state.sort=e.target.value;render();});
  document.getElementById('upd').textContent=UPDDATE;
  majFav();
  render();
})();
</script>
"""

page = (page
        .replace("METAJSON", json.dumps(meta, ensure_ascii=False).replace("</", "<\\/"))
        .replace("THUMBJSON", json.dumps(thumbs).replace("</", "<\\/"))
        .replace("SERIEOPTS", serie_opts)
        .replace("GENDATE", gen)
        .replace("UPDDATE", json.dumps(updated[:10] if updated != "?" else "?")))

# --- garde-fous : mieux vaut ne rien produire qu'une page dégradée
cotees = sum(1 for c in cards if c.get("low") is not None)
avec_img = sum(1 for c in cards if c.get("thumb"))
poids = len(page.encode("utf-8")) / 1048576
probleme = []
if len(cards) < 2500:
    probleme.append(f"seulement {len(cards)} cartes")
if cotees < 2000:
    probleme.append(f"seulement {cotees} cartes cotées")
if avec_img < 2400:
    probleme.append(f"seulement {avec_img} visuels")
if poids > 15.5:
    probleme.append(f"page de {poids:.1f} Mo, au-dessus de la limite de 16 Mo")
if probleme:
    sys.exit("ARRÊT — " + " ; ".join(probleme) + ". Rien n'a été écrit, ne pas publier.")

out = HERE / "radar-promos-jp.html"
out.write_text(page, encoding="utf-8")
print(f"écrit {out} — {poids:.2f} Mo · {len(cards)} cartes, {cotees} cotées, {avec_img} avec visuel")
