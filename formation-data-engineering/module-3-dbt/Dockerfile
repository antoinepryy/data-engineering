FROM python:3.10-slim

WORKDIR /usr/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install DBT and dependencies
RUN pip install --no-cache-dir \
    dbt-core==1.7.0 \
    dbt-postgres==1.7.0 \
    dbt-redshift==1.7.0 \
    dbt-snowflake==1.7.0 \
    dbt-bigquery==1.7.0 \
    sqlfluff==2.3.5 \
    sqlfluff-templater-dbt==2.3.5 \
    pandas==2.0.3 \
    jupyter==1.0.0 \
    streamlit==1.28.0

# Create DBT directories
RUN mkdir -p /usr/app/formation_analytics /usr/app/logs

# Copy DBT project files
COPY . /usr/app/

# Set environment variables
ENV DBT_PROFILES_DIR=/usr/app
ENV PYTHONPATH=/usr/app

WORKDIR /usr/app/formation_analytics

# Expose ports for documentation and Streamlit
EXPOSE 8080 8501

CMD ["bash"]