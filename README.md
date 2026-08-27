# Radar Promos JP — relevé de prix et reconstruction de la page

Ce dépôt contient tout ce qu'il faut pour que la page
**https://claude.ai/code/artifact/14c745db-0752-46e0-b37b-c73b9e537b6a**
soit reconstruite chaque jour avec des prix frais.

| Fichier | Rôle | Change |
|---|---|---|
| `cards.json` | catalogue complet : 2 638 cartes, vignettes comprises (~14 Mo) | rarement |
| `build.py` | fabrique `radar-promos-jp.html` à partir de `cards.json` + `prices.json` | rarement |
| `fetch_prices.py` | relève les cotations Cardmarket du jour | rarement |
| `prices.json` | les cotations, indexées par `idProduct` Cardmarket | chaque jour |
| `releve.json` | la date du relevé Cardmarket | chaque jour |
| `products.json` | noms et extensions des produits retenus | à chaque nouveauté |

## Mise en route (une seule fois)

1. Créer un dépôt GitHub — **public de préférence**, sinon `raw.githubusercontent.com`
   demandera un jeton et la tâche quotidienne échouera.
2. Y déposer ces fichiers, en plaçant
   `prices-workflow (a placer dans .github-workflows).yml` sous `.github/workflows/prices.yml`.
3. **Settings → Actions → General → Workflow permissions** : cocher *Read and write permissions*.
4. Onglet **Actions** → *Relevé quotidien des prix* → **Run workflow** pour le premier relevé.
5. Donner à Claude l'URL du dépôt : il la note dans la fiche du projet, et la tâche quotidienne
   s'enclenche d'elle-même le lendemain matin.

Ensuite le relevé tourne seul à 04:20 UTC (06:20 heure de Paris en été), et la tâche Claude de
6 h reconstruit puis republie la page.

## Le workflow

`fetch_prices.py` télécharge deux fichiers publics de Cardmarket — le guide de prix et le
catalogue produits — sans compte ni clé d'API, et n'en retient que les **douze extensions promo
japonaises** listées en dur dans le script. Il s'arrête en erreur si moins de 2 000 cotations
sont retenues, plutôt que d'écraser un bon relevé par un mauvais.

`build.py` reconstruit ensuite la page et **refuse d'écrire** si le résultat est dégradé :
moins de 2 500 cartes, moins de 2 000 cotées, moins de 2 400 visuels, ou une page dépassant
15,5 Mo (la limite d'un artifact est de 16 Mo). Le workflow l'exécute aussi, pour qu'un relevé
qui casserait la page soit détecté chez GitHub et non au moment de publier.

`radar-promos-jp.html` n'est volontairement **pas** versionné : 14 Mo par jour feraient enfler
le dépôt inutilement. Il est reconstruit à la demande.

## Format de `prices.json`

```json
{ "462904": { "low": 5.99, "tr": 38.56, "a7": 32.92, "a30": 31.86 } }
```

`low` = offre la plus basse, toutes conditions confondues · `tr` = tendance ·
`a7` / `a30` = moyennes 7 et 30 jours. Cardmarket ne publie pas de prix par état.
