# Amazon Scraper

Outil de collecte de données produit sur plusieurs boutiques Amazon. Le projet combine Selenium et Chrome pour parcourir les résultats, une interface de bureau PyQt6 pour configurer et suivre la collecte, puis SQLite et CSV pour conserver les données.

Auteur : EDERE HERVE REGINA

## Fonctionnalités

- Sélection d’une ou plusieurs catégories de produits.
- Choix parmi dix boutiques Amazon : France, États-Unis, Royaume-Uni, Canada, Allemagne, Espagne, Italie, Japon, Australie et Brésil.
- Limite configurable jusqu’à 50 produits par collecte.
- Suivi de l’avancement et messages d’état dans l’interface.
- Enregistrement des résultats dans SQLite et export CSV.
- Aucune URL de produit n’est sauvegardée.

## Catégories

Téléphones portables, casques Bluetooth, télévisions, GPS, accessoires sans fil, univers Hi-Fi, photo et caméscope.

## Données collectées

Selon les informations affichées sur la page, le scraper peut enregistrer le nom du produit, la catégorie, le prix, la note, le nombre d’avis, la disponibilité et la boutique Amazon concernée.

## Technologies

| Technologie | Utilisation |
| --- | --- |
| Python | Logique de l’application |
| Selenium | Automatisation du navigateur et collecte des résultats |
| Google Chrome | Navigateur piloté par Selenium |
| PyQt6 | Interface graphique |
| SQLite | Stockage local des produits |
| CSV | Export tabulaire, compatible avec Excel |

## Structure

```text
amazon_scraper/
├── app/
│   ├── controllers/
│   ├── models/
│   ├── scraper/
│   └── views/
├── data/
├── exports/
├── tests/
├── .gitignore
├── README.md
├── config.py
├── main.py
└── requirements.txt
```

## Prérequis

- Python 3.10 ou plus récent
- Google Chrome
- Une connexion Internet pour lancer une collecte

Selenium Manager prend en charge la gestion du pilote Chrome au démarrage.

## Installation

Depuis la racine du projet, crée et active un environnement virtuel sous Windows :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Installe les dépendances :

```powershell
python -m pip install -r requirements.txt
```

## Démarrage

Lance l’application avec :

```powershell
python main.py
```

Dans la fenêtre, sélectionne les catégories, la boutique Amazon et le nombre maximal de produits, puis lance la collecte. Chrome est visible pendant l’exécution ; garde la fenêtre ouverte jusqu’à la fin.

## Stockage et exports

| Fichier | Description |
| --- | --- |
| `data/amazon_scraper.sqlite3` | Base SQLite persistante. Les produits sont identifiés par boutique, catégorie et titre ; une nouvelle collecte met à jour les correspondances existantes. |
| `exports/produits.csv` | Export de la collecte, avec des en-têtes français et des colonnes séparées par des points-virgules. |

Les dossiers nécessaires sont créés automatiquement. Aucun rapport HTML n’est généré.

## Configuration

Les paramètres sont regroupés dans `config.py` : boutiques, catégories et requêtes localisées, nombre maximal de produits, visibilité du navigateur et délais d’attente Selenium. Le navigateur est visible par défaut.

## Limites

Le contenu et la structure des pages Amazon peuvent varier selon la boutique ou évoluer dans le temps ; les informations récupérées peuvent donc être incomplètes et les sélecteurs peuvent nécessiter une mise à jour. Amazon peut aussi présenter un CAPTCHA ou limiter l’accès. Le scraper ne contourne pas ces protections.

---

Projet réalisé par EDERE HERVE REGINA
