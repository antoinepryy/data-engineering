# Dockerfile pour le Module 3 - Pipeline ETL POI avec Airflow
# Formation Data Engineering

FROM apache/airflow:2.7.3-python3.10

USER root

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Installation des dépendances Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copier les scripts et DAGs
COPY --chown=airflow:root dags/ /opt/airflow/dags/
COPY --chown=airflow:root scripts/ /opt/airflow/scripts/
COPY --chown=airflow:root plugins/ /opt/airflow/plugins/

# Créer les répertoires de données
RUN mkdir -p /opt/airflow/data/raw \
    /opt/airflow/data/processed \
    /opt/airflow/data/output \
    /opt/airflow/data/deduplication

# Variables d'environnement
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV PYTHONPATH=/opt/airflow/scripts:$PYTHONPATH

EXPOSE 8080
