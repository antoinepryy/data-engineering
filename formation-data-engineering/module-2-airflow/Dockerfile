FROM apache/airflow:2.8.0-python3.10

USER root

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages compatible with Airflow 2.8.0
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    psycopg2-binary \
    apache-airflow-providers-postgres \
    apache-airflow-providers-http

# Copy DAGs and plugins
COPY --chown=airflow:airflow dags /opt/airflow/dags
COPY --chown=airflow:airflow plugins /opt/airflow/plugins
COPY --chown=airflow:airflow config/airflow.cfg /opt/airflow/airflow.cfg

WORKDIR /opt/airflow