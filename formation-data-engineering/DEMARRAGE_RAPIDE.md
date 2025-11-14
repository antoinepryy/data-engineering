# 🎉 Formation Data Engineering - Prête à l'Emploi !

## ✅ Services Actuellement Actifs

| Service | URL | Status | Description |
|---------|-----|--------|-------------|
| **Module Vocal** | http://localhost:8501 | ✅ Actif | Interface Streamlit pour TTS/STT |
| **Jupyter Lab** | http://localhost:8889 | ✅ Actif | Notebooks Python (token: `formation2024`) |
| **PostgreSQL** | localhost:5432 | ✅ Actif | Base pour Airflow |

---

## 🚀 Accès Immédiat aux Modules

### 1️⃣ **Module Vocal (DISPONIBLE MAINTENANT)**
```bash
# Ouvrir dans le navigateur
open http://localhost:8501

# OU directement
# Chrome: http://localhost:8501
# Firefox: http://localhost:8501
```

**Fonctionnalités disponibles :**
- 🔊 Text-to-Speech (3 moteurs)
- 🎙️ Speech-to-Text (Whisper)
- 🔄 Speech-to-Speech Translation
- 📊 Analyse Audio
- 💻 Exercices interactifs

### 2️⃣ **Jupyter Notebooks (DISPONIBLE MAINTENANT)**
```bash
# Ouvrir dans le navigateur
open http://localhost:8889

# Token d'accès: formation2024
```

**Contenu disponible :**
- Notebooks d'exemples
- Exercices PySpark
- Analyses de données

---

## 📚 Démarrer les Autres Modules

### Module 2: Apache Airflow
```bash
# Depuis le dossier formation-data-engineering
./start.sh
# Choisir option 4

# OU manuellement
docker-compose up -d airflow-init
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker

# Accès: http://localhost:8080 (admin/admin)
```

### Module 3: DBT
```bash
# Démarrer PostgreSQL et DBT
docker-compose up -d postgres-dbt dbt

# Accéder au container
docker exec -it dbt bash
cd /usr/app/formation_analytics

# Lancer les transformations
dbt run
dbt test
```

### Module 4: Apache Spark
```bash
# Démarrer le cluster
docker-compose up -d spark-master spark-worker-1 spark-worker-2

# Accès UI: http://localhost:9090

# Lancer PySpark
docker exec -it spark-master pyspark
```

---

## 🧪 Tester le Module Vocal

### Test Rapide TTS
1. Ouvrir http://localhost:8501
2. Aller dans l'onglet "Text-to-Speech"
3. Entrer du texte
4. Cliquer "Générer Audio"

### Test Rapide STT
1. Aller dans l'onglet "Speech-to-Text"
2. Uploader un fichier audio
3. Cliquer "Transcrire"

### Exercices Guidés
1. Aller dans l'onglet "Exercices"
2. Choisir un exercice
3. Suivre les instructions

---

## 🔧 Commandes Utiles

### Monitoring
```bash
# Voir les logs du module vocal
docker logs -f vocal-python

# Vérifier l'état des services
docker ps

# Ressources utilisées
docker stats
```

### Redémarrage si nécessaire
```bash
# Redémarrer Streamlit
docker exec vocal-python pkill streamlit
docker exec -d vocal-python streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0

# Redémarrer tous les services
docker-compose restart
```

### Accès aux containers
```bash
# Module Vocal
docker exec -it vocal-python bash

# Jupyter
docker exec -it jupyter bash

# PostgreSQL
docker exec -it postgres-airflow psql -U airflow
```

---

## 📊 Architecture Déployée

```
┌─────────────────────────────────────────┐
│     Votre Machine (localhost)           │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Module Vocal │  │   Jupyter    │   │
│  │   Port 8501  │  │  Port 8889   │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  PostgreSQL  │  │   (Airflow)  │   │
│  │   Port 5432  │  │  Port 8080   │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  Docker Network: formation-network      │
└─────────────────────────────────────────┘
```

---

## 🎓 Parcours d'Apprentissage Recommandé

### Semaine 1: Fondamentaux
- ✅ **Jour 1-2**: Module Vocal (TTS, STT)
- **Jour 3-4**: Airflow basics
- **Jour 5**: Projet intégration

### Semaine 2: Avancé
- **Jour 1-2**: DBT transformations
- **Jour 3-4**: Spark DataFrames
- **Jour 5**: Spark Streaming

### Semaine 3: Projet Final
- Intégration complète des 4 modules
- Pipeline end-to-end
- Optimisation et production

---

## ❓ Troubleshooting

### Streamlit ne répond pas
```bash
# Vérifier les logs
docker logs vocal-python

# Redémarrer
docker restart vocal-python

# Relancer Streamlit
docker exec -d vocal-python streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0
```

### Jupyter demande un token
- Token: `formation2024`
- Ou récupérer le token:
```bash
docker exec jupyter jupyter notebook list
```

### Port déjà utilisé
```bash
# Mac/Linux
lsof -i :8501
kill -9 [PID]

# Windows
netstat -ano | findstr :8501
taskkill /PID [PID] /F
```

---

## 🌟 Prochaines Étapes

1. **Explorer le Module Vocal** (disponible maintenant)
   - Tester toutes les démos
   - Faire les exercices

2. **Utiliser Jupyter** pour expérimenter
   - Créer vos propres notebooks
   - Tester les exemples de code

3. **Progresser vers les autres modules**
   - Airflow pour l'orchestration
   - DBT pour les transformations
   - Spark pour le Big Data

---

## 📞 Support

- **Documentation complète**: `/Programme_Formation_Data_Engineering.md`
- **Guide technique**: `/README.md`
- **Exercices**: Dans chaque module `/exercices/`

---

**🎉 Félicitations! Votre environnement de formation est prêt!**

Commencez par ouvrir http://localhost:8501 pour explorer le module de traitement vocal.