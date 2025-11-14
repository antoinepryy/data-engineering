# 🚀 Formation Data Engineering - Code et Démonstrations

Ce dépôt contient tout le code nécessaire pour suivre la formation Data Engineering complète.

## 📁 Structure du Projet

```
formation-data-engineering/
├── module-1-vocal/      # Traitement vocal (TTS, STT, Speech-to-Speech)
├── module-2-airflow/    # Apache Airflow orchestration
├── module-3-dbt/        # Data Build Tool
├── module-4-spark/      # Apache Spark
├── projet-final/        # Projet d'intégration
├── data/               # Datasets partagés
├── notebooks/          # Jupyter notebooks
└── utils/              # Scripts utilitaires
```

## 🐳 Prérequis

- Docker Desktop (4GB RAM minimum alloué)
- Docker Compose v2+
- 20GB d'espace disque disponible
- Ports disponibles: 3000, 3001, 5000, 5432, 5433, 6379, 7077, 8080, 8501, 8888, 8889, 9000, 9090

## 🚀 Démarrage Rapide

### 1. Cloner le repository
```bash
git clone [URL_DU_REPO]
cd formation-data-engineering
```

### 2. Démarrer l'environnement complet
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tous les services sont lancés
docker-compose ps
```

### 3. Accès aux interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin / admin |
| **Spark UI** | http://localhost:9090 | - |
| **Jupyter** | http://localhost:8889 | Token: formation2024 |
| **Streamlit (Vocal)** | http://localhost:8501 | - |
| **Express (Vocal)** | http://localhost:3000 | - |
| **Portainer** | http://localhost:9000 | - |
| **PostgreSQL (Airflow)** | localhost:5432 | airflow / airflow |
| **PostgreSQL (DBT)** | localhost:5433 | dbt_user / dbt_pass |

## 📚 Modules de Formation

### Module 1: Traitement Vocal
```bash
# Accéder au container Python
docker exec -it vocal-python bash

# Lancer les démos
cd /app
python demos/01_text_to_speech.py
python demos/02_speech_to_text.py
python demos/03_translation.py

# Interface Streamlit
streamlit run app.py
```

### Module 2: Apache Airflow
```bash
# Vérifier les DAGs
docker exec -it airflow-scheduler airflow dags list

# Déclencher un DAG
docker exec -it airflow-scheduler airflow dags trigger example_etl

# Voir les logs
docker logs airflow-scheduler
```

### Module 3: DBT
```bash
# Accéder au container DBT
docker exec -it dbt bash

# Initialiser le projet
dbt init my_project

# Lancer les modèles
dbt run

# Générer la documentation
dbt docs generate
dbt docs serve --port 8082
```

### Module 4: Apache Spark
```bash
# Accéder au container Spark
docker exec -it spark-master bash

# Soumettre un job Spark
spark-submit /opt/spark-apps/demos/wordcount.py

# Lancer PySpark interactif
pyspark --master spark://spark-master:7077
```

## 🛠️ Commands Utiles

### Gestion des containers
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Voir les logs d'un service
docker-compose logs -f [service-name]

# Redémarrer un service
docker-compose restart [service-name]

# Nettoyer les ressources Docker
docker system prune -a --volumes
```

### Monitoring
```bash
# Voir l'utilisation des ressources
docker stats

# Vérifier la santé des services
docker-compose ps

# Accéder à un container
docker exec -it [container-name] bash
```

## 📝 Exercices

Les exercices sont organisés par module :

1. **Module 1** : `/module-1-vocal/exercices/`
2. **Module 2** : `/module-2-airflow/exercices/`
3. **Module 3** : `/module-3-dbt/exercices/`
4. **Module 4** : `/module-4-spark/exercices/`

Chaque exercice contient :
- `README.md` : Instructions détaillées
- `solution/` : Solution complète
- `tests/` : Tests unitaires

## 🔧 Troubleshooting

### Problème : "Port already in use"
```bash
# Identifier le processus utilisant le port
lsof -i :PORT_NUMBER
# Ou sur Windows
netstat -ano | findstr :PORT_NUMBER

# Tuer le processus
kill -9 PID
```

### Problème : "Container keeps restarting"
```bash
# Vérifier les logs
docker-compose logs [service-name]

# Augmenter les ressources Docker
# Docker Desktop > Preferences > Resources
```

### Problème : "Permission denied"
```bash
# Linux/Mac
sudo chown -R $USER:$USER ./

# Windows (PowerShell as Admin)
icacls .\ /grant Everyone:F /T
```

## 📚 Documentation

- [Documentation complète](./docs/)
- [Slides de présentation](./slides/)
- [Ressources supplémentaires](./resources/)

## 🤝 Support

- Slack : #formation-data-engineering
- Email : support@formation.com
- Issues : GitHub Issues

## 📄 License

MIT License - Voir [LICENSE](./LICENSE)

---

**Note** : Assurez-vous d'avoir au moins 8GB de RAM disponible pour faire tourner l'ensemble des services simultanément. Pour des machines avec moins de ressources, lancez les modules individuellement.