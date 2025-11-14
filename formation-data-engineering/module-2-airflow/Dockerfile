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

# Install Python packages
RUN pip install --no-cache-dir \
    pandas==2.0.3 \
    numpy==1.24.3 \
    requests==2.31.0 \
    sqlalchemy==2.0.19 \
    psycopg2-binary==2.9.6 \
    boto3==1.28.17 \
    pyspark==3.4.1 \
    dbt-core==1.5.2 \
    dbt-postgres==1.5.2 \
    great-expectations==0.17.12 \
    apache-airflow-providers-postgres==5.5.1 \
    apache-airflow-providers-ssh==3.7.1 \
    apache-airflow-providers-http==4.4.2 \
    apache-airflow-providers-docker==3.7.3 \
    apache-airflow-providers-amazon==8.3.1 \
    apache-airflow-providers-google==10.3.0 \
    apache-airflow-providers-spark==4.1.3 \
    apache-airflow-providers-databricks==4.3.1

# Copy DAGs and plugins
COPY --chown=airflow:airflow dags /opt/airflow/dags
COPY --chown=airflow:airflow plugins /opt/airflow/plugins
COPY --chown=airflow:airflow config/airflow.cfg /opt/airflow/airflow.cfg

WORKDIR /opt/airflow