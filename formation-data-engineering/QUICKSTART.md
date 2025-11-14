# 🚀 Guide de Démarrage Rapide

## Installation en 5 minutes

### 1️⃣ Prérequis
- Docker Desktop installé et lancé
- 8GB RAM minimum disponible
- Ports libres: 3000, 5432, 8080, 8888, 9090

### 2️⃣ Lancement rapide
```bash
# Clone du projet (si pas déjà fait)
cd formation-data-engineering

# Création du réseau Docker
docker network create formation-network 2>/dev/null || true

# Lancement des services essentiels seulement
docker-compose up -d vocal-python jupyter postgres-airflow

# Vérification
docker-compose ps
```

### 3️⃣ Accès aux services

| Module | Service | URL | Identifiants |
|--------|---------|-----|--------------|
| **Vocal** | Streamlit | http://localhost:8501 | - |
| **Jupyter** | Notebooks | http://localhost:8889 | Token: formation2024 |
| **Airflow** | Web UI | http://localhost:8080 | admin / admin |

## 📚 Modules par ordre de difficulté

### Débutant: Module 1 - Traitement Vocal
```bash
# Démarrer uniquement le module vocal
docker-compose up -d vocal-python

# Accéder à l'application
open http://localhost:8501

# Tester les démos
# 1. Text-to-Speech
# 2. Speech-to-Text  
# 3. Analyse Audio
```

### Intermédiaire: Module 2 - Airflow
```bash
# Démarrer Airflow (prend 2-3 minutes)
docker-compose up -d postgres-airflow redis airflow-init
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker

# Accéder à Airflow
open http://localhost:8080

# Login: admin / admin
# Activer le DAG: 01_demo_basic_dag
```

### Avancé: Module 3 & 4 - DBT + Spark
```bash
# DBT
docker-compose up -d postgres-dbt dbt

# Spark
docker-compose up -d spark-master spark-worker-1

# Accès Spark UI
open http://localhost:9090
```

## 🎯 Exercices Pratiques Guidés

### Exercice 1: Créer un lecteur de news (30 min)
1. Ouvrir Jupyter: http://localhost:8889
2. Créer un nouveau notebook Python
3. Copier le code starter:

```python
# Installer les dépendances
!pip install feedparser gtts pydub

# Importer les librairies
import feedparser
from gtts import gTTS
from IPython.display import Audio

# Récupérer les news
feed = feedparser.parse("https://news.ycombinator.com/rss")
articles = feed.entries[:3]

# Créer le script
script = "Voici les dernières actualités tech. "
for i, article in enumerate(articles, 1):
    script += f"Article {i}. {article.title}. "

# Générer l'audio
tts = gTTS(script, lang='en')
tts.save("news.mp3")

# Écouter
Audio("news.mp3")
```

### Exercice 2: Pipeline ETL avec Airflow (45 min)
1. Créer un nouveau DAG dans `/module-2-airflow/dags/`
2. Template de base:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    # Votre code ici
    return {"data": [1,2,3]}

def transform(**context):
    data = context['ti'].xcom_pull(task_ids='extract')
    # Transformation
    return {"transformed": data}

def load(**context):
    data = context['ti'].xcom_pull(task_ids='transform')
    print(f"Loading: {data}")

with DAG('mon_premier_dag', 
         start_date=datetime(2024, 1, 1),
         schedule_interval='@daily') as dag:
    
    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)
    
    t1 >> t2 >> t3
```

## 🔧 Commandes Utiles

### Monitoring
```bash
# Voir les logs d'un service
docker-compose logs -f vocal-python

# Statistiques ressources
docker stats

# Entrer dans un container
docker exec -it vocal-python bash
```

### Reset / Nettoyage
```bash
# Arrêter tous les services
docker-compose down

# Reset complet (supprime les données)
docker-compose down -v

# Libérer de l'espace
docker system prune -a
```

## ❓ Troubleshooting

### Problème: "Port already in use"
```bash
# Mac/Linux
lsof -i :8080  # Identifier le processus
kill -9 [PID]  # Tuer le processus

# Windows
netstat -ano | findstr :8080
taskkill /PID [PID] /F
```

### Problème: "Container keeps restarting"
```bash
# Vérifier les logs
docker-compose logs [service-name]

# Augmenter la mémoire Docker
# Docker Desktop → Preferences → Resources → Memory: 8GB
```

### Problème: Airflow ne démarre pas
```bash
# Réinitialiser Airflow
docker-compose down
docker volume rm formation-data-engineering_postgres-airflow-data
docker-compose up -d
```

## 📖 Documentation Complète

- [Module 1 - Traitement Vocal](./module-1-vocal/README.md)
- [Module 2 - Apache Airflow](./module-2-airflow/README.md)
- [Module 3 - DBT](./module-3-dbt/README.md)
- [Module 4 - Apache Spark](./module-4-spark/README.md)

## 💬 Support

- **Slack**: #formation-data-engineering
- **Email**: support@formation.com
- **Forum**: https://forum.formation.com

---

✨ **Tip**: Commencez par le Module 1 (Vocal) qui fonctionne immédiatement sans configuration!