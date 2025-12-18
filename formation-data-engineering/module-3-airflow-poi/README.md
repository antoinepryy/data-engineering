# Module 3 - Pipeline ETL POI avec Apache Airflow

## Introduction

Ce module présente un pipeline ETL complet pour la gestion des **Points Of Interest (POI)** utilisant Apache Airflow. Il simule un cas réel d'intégration de données touristiques provenant de plusieurs sources.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODULE 3 - POI ETL PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │ Datatourisme │    │    Apidae    │    │  TripAdvisor │                   │
│  │    (API)     │    │    (API)     │    │    (API)     │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                           │
│         └───────────────────┼───────────────────┘                           │
│                             │                                               │
│                             ▼                                               │
│                    ┌────────────────┐                                       │
│                    │   EXTRACTION   │  DAG 1: poi_etl_pipeline              │
│                    │  (Fake Data)   │                                       │
│                    └────────┬───────┘                                       │
│                             │                                               │
│                             ▼                                               │
│                    ┌────────────────┐                                       │
│                    │ NORMALISATION  │  Uniformisation du format             │
│                    │   & VALIDATION │  Contrôle qualité                     │
│                    └────────┬───────┘                                       │
│                             │                                               │
│                             ▼                                               │
│                    ┌────────────────┐                                       │
│                    │  DÉDUPLICATION │  DAG 2: poi_deduplication             │
│                    │  & AGRÉGATION  │  Détection des doublons               │
│                    └────────┬───────┘                                       │
│                             │                                               │
│                             ▼                                               │
│                    ┌────────────────┐                                       │
│                    │   CHARGEMENT   │  PostgreSQL                           │
│                    │   (Database)   │                                       │
│                    └────────┬───────┘                                       │
│                             │                                               │
│                             ▼                                               │
│                    ┌────────────────┐                                       │
│                    │   DASHBOARD    │  Streamlit                            │
│                    │ (Visualisation)│                                       │
│                    └────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Structure du Module

```
module-3-airflow-poi/
├── dags/
│   ├── 01_poi_etl_pipeline.py      # DAG principal ETL
│   └── 02_poi_deduplication_dag.py # DAG de déduplication
├── scripts/
│   ├── fake_data_generator.py      # Générateur de données fictives
│   └── init_db.sql                 # Script d'initialisation DB
├── app/
│   └── streamlit_app.py            # Dashboard de visualisation
├── data/                           # Données (générées automatiquement)
│   ├── raw/                        # Données brutes
│   ├── processed/                  # Données traitées
│   ├── output/                     # Données finales
│   └── deduplication/              # Résultats déduplication
├── plugins/                        # Plugins Airflow personnalisés
├── docker-compose.yml              # Configuration Docker
├── Dockerfile                      # Image Airflow
├── Dockerfile.streamlit            # Image Dashboard
├── requirements.txt                # Dépendances Python
└── README.md                       # Ce fichier
```

## Démarrage Rapide

### Prérequis

- Docker Desktop (avec au moins 4GB RAM alloués)
- Docker Compose v2+
- Ports disponibles: 8080, 8501, 5433, 5434

### Lancer le projet

```bash
# Se placer dans le répertoire du module
cd formation-data-engineering/module-3-airflow-poi

# Créer les répertoires et lancer les services
mkdir -p data/{raw,processed,output,deduplication}
echo "AIRFLOW_UID=$(id -u)" > .env
docker-compose up -d --build

# Vérifier que tout est démarré (attendre ~1-2 min pour healthy)
docker-compose ps
```

### Arrêter le projet

```bash
# Arrêter les services (conserve les données)
docker-compose down

# Arrêter et supprimer toutes les données
docker-compose down -v
```

### Relancer le projet

```bash
# Relancer sans rebuild
docker-compose up -d

# Relancer avec rebuild (si modification du code)
docker-compose up -d --build
```

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler
docker-compose logs -f poi-dashboard
```

### Accès aux Services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Airflow** | http://localhost:8080 | admin / admin |
| **Dashboard POI** | http://localhost:8501 | - |
| **PostgreSQL Airflow** | localhost:5433 | airflow / airflow |
| **PostgreSQL POI** | localhost:5434 | poi / poi |

## DAGs Disponibles

### DAG 1: `01_poi_etl_pipeline`

Pipeline ETL principal qui:
1. **Extrait** les données de 4 sources (Datatourisme, Apidae, TripAdvisor, Tourinsoft)
2. **Normalise** les données au format unifié
3. **Valide** la qualité des données
4. **Charge** dans la base de données

```
start → setup → [extract_sources] → [normalize_sources] → validate → quality_check
                                                                          │
                                                          ┌───────────────┴───────────────┐
                                                          ▼                               ▼
                                                   load_to_database               quality_alert
                                                          │                               │
                                                          └───────────────┬───────────────┘
                                                                          ▼
                                                                   send_notification → end
```

### DAG 2: `02_poi_deduplication`

Pipeline de déduplication qui:
1. **Charge** les données validées
2. **Détecte** les doublons par:
   - Références communes entre sources
   - Mesures de similarité (nom, coordonnées, adresse)
3. **Agrège** les POI redondants
4. **Génère** un rapport de déduplication

```
start → load_data → [detection] → aggregate_duplicates → generate_report → end
                         │
                         ├── by_common_references
                         └── by_similarity
```

## Structure des Données POI

Les POI suivent le format documenté dans `processus_etl.md`:

```json
{
  "id": 1,
  "closed": false,
  "display": true,
  "tags": ["sites_monument_castle"],
  "types": ["sites"],
  "poi_name": {
    "fr": "Château de Versailles",
    "en": "Palace of Versailles"
  },
  "addresses": [{
    "city": "Versailles",
    "zip_code": "78000",
    "region": "Ile-de-France",
    "country": "France"
  }],
  "geopoints": [{
    "latitude": 48.8049,
    "longitude": 2.1204
  }],
  "sources": [{
    "source": "Datatourisme",
    "reference": "DT12345",
    "last_update": "2024-01-15"
  }]
}
```

## Règles de Déduplication

### Détection des Doublons

| Méthode | Critères |
|---------|----------|
| **Références communes** | Même référence dans différentes sources |
| **Similarité nom** | Score > 85% (SequenceMatcher) |
| **Distance géo** | < 200m (direct) ou < 1km (avec adresse) |
| **Similarité adresse** | Score > 80% |

### Règles d'Agrégation

| Attribut | Règle |
|----------|-------|
| `closed` | Valeur maximale (si un dit fermé → fermé) |
| `display` | Valeur minimale (si un dit masqué → masqué) |
| `tags`, `types` | Union des valeurs |
| `addresses` | Fusion par ville |
| `contacts` | Fusion par nom complet |
| `pictures` | Union par URL |
| `products` | Fusion par nom+devise, min/max prix |

## Dashboard Streamlit

Le dashboard offre:

- **Carte interactive** des POI avec filtres
- **Graphiques** de distribution par source/type/région
- **Tableau** de données avec recherche et export
- **Analyse** des résultats de déduplication

## Exercices Pratiques

### Exercice 1: Modifier le seuil de qualité

Dans `01_poi_etl_pipeline.py`, modifier le seuil de validation:

```python
# Ligne ~280
QUALITY_THRESHOLD = 0.9  # Passer de 0.8 à 0.9
```

### Exercice 2: Ajouter une nouvelle source

1. Modifier `SOURCES` dans le DAG
2. Créer la fonction d'extraction spécifique
3. Adapter la normalisation si nécessaire

### Exercice 3: Créer une alerte Slack

Remplacer `send_success_notification` par une vraie notification Slack:

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

notify_slack = SlackWebhookOperator(
    task_id='notify_slack',
    slack_webhook_conn_id='slack_webhook',
    message="Pipeline POI terminé: {{ ti.xcom_pull(key='load_results')['loaded_count'] }} POI chargés",
    dag=dag
)
```

### Exercice 4: Améliorer la détection de similarité

Implémenter une détection basée sur:
- Numéro de téléphone
- Email de contact
- Site web

## Tester les DAGs

### Via l'interface Web (recommandé)

1. Ouvrir http://localhost:8080 (admin/admin)
2. Activer le DAG `01_poi_etl_pipeline` (toggle ON)
3. Cliquer sur le bouton "Play" → "Trigger DAG"
4. Suivre l'exécution dans l'onglet "Graph"
5. Une fois terminé, faire de même avec `02_poi_deduplication`

### Via la ligne de commande

```bash
# Lancer le pipeline ETL
docker exec airflow-scheduler-poi airflow dags trigger 01_poi_etl_pipeline

# Attendre la fin puis lancer la déduplication
docker exec airflow-scheduler-poi airflow dags trigger 02_poi_deduplication

# Voir l'état d'un DAG
docker exec airflow-scheduler-poi airflow dags state 01_poi_etl_pipeline $(date +%Y-%m-%d)

# Voir les dernières exécutions
docker exec airflow-scheduler-poi airflow dags list-runs -d 01_poi_etl_pipeline
```

### Vérifier les résultats

```bash
# Voir les fichiers générés
ls -la data/output/
ls -la data/deduplication/

# Voir le rapport de déduplication
cat data/deduplication/dedup_report_*.md
```

## Commandes Utiles

```bash
# Logs d'un service
docker-compose logs -f airflow-scheduler

# Entrer dans un container
docker exec -it airflow-webserver-poi bash

# Lister les DAGs
docker exec airflow-scheduler-poi airflow dags list

# Voir les erreurs d'import des DAGs
docker exec airflow-scheduler-poi airflow dags list-import-errors

# Reset complet (supprime toutes les données)
docker-compose down -v && docker-compose up -d --build
```

## Troubleshooting

### Airflow ne démarre pas

```bash
# Vérifier les logs
docker-compose logs airflow-init

# Réinitialiser la DB
docker-compose down -v
docker-compose up -d
```

### DAG non visible

```bash
# Vérifier les erreurs de syntaxe
docker exec airflow-webserver-poi airflow dags list-import-errors
```

### Problèmes de permissions

```bash
# Linux: définir l'UID
echo "AIRFLOW_UID=$(id -u)" > .env
docker-compose down && docker-compose up -d
```

## Ressources

- [Documentation Apache Airflow](https://airflow.apache.org/docs/)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [Processus ETL POI](../docs/processus_etl.md)

## Auteurs

Formation Data Engineering - Module 3

---

**Note**: Ce module utilise des données fictives générées automatiquement. En production, les données proviendraient des vraies APIs des sources touristiques.
