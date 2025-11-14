FROM bitnami/spark:3.5.0

USER root

# Install Python and additional dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    vim \
    curl \
    wget \
    postgresql-client \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for Spark
RUN pip3 install --no-cache-dir \
    pyspark==3.5.0 \
    pandas==2.0.3 \
    numpy==1.24.3 \
    matplotlib==3.7.1 \
    seaborn==0.12.2 \
    scikit-learn==1.3.0 \
    pyarrow==12.0.1 \
    jupyter==1.0.0 \
    notebook==6.5.4 \
    jupyterlab==4.0.3 \
    findspark==2.0.1 \
    delta-spark==2.4.0 \
    great-expectations==0.17.12 \
    streamlit==1.28.0 \
    kafka-python==2.0.2 \
    redis==4.6.0 \
    psycopg2-binary==2.9.6 \
    sqlalchemy==2.0.19 \
    plotly==5.15.0 \
    boto3==1.28.17

# Create necessary directories
RUN mkdir -p /opt/spark-apps /opt/spark-data /opt/notebooks /opt/spark-events

# Set permissions
RUN chmod -R 777 /opt/spark-apps /opt/spark-data /opt/notebooks /opt/spark-events

# Copy application files
COPY --chown=1001:1001 . /opt/spark-apps/

# Set Spark configurations
ENV SPARK_MODE=master
ENV SPARK_MASTER_URL=spark://spark-master:7077
ENV PYSPARK_PYTHON=python3
ENV PYTHONPATH=/opt/spark-apps:$PYTHONPATH

# Expose ports
EXPOSE 4040 6066 7077 8080 8888

WORKDIR /opt/spark-apps

USER 1001

CMD ["bash"]