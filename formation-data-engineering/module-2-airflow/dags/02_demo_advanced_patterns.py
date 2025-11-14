"""
DAG de démonstration des patterns avancés
Module 2 - Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowSkipException
import pandas as pd
import random
import json

# Configuration du DAG
default_args = {
    'owner': 'formation',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'sla': timedelta(hours=2),  # Service Level Agreement
    'tags': ['demo', 'advanced', 'patterns'],
}

dag = DAG(
    '02_demo_advanced_patterns',
    default_args=default_args,
    description='Patterns avancés: Branching, TaskGroups, Dynamic Tasks',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    doc_md="""
    ## DAG de Patterns Avancés
    
    Ce DAG démontre:
    1. **Branching** : Logique conditionnelle
    2. **TaskGroups** : Organisation des tâches
    3. **Dynamic Tasks** : Génération dynamique
    4. **Sensors** : Attente de conditions
    5. **Variables** : Configuration dynamique
    6. **Cross-DAG Dependencies** : Trigger d'autres DAGs
    """
)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def check_data_quality(**context):
    """Vérifie la qualité des données et décide de la branche à suivre"""
    print("🔍 Vérification de la qualité des données...")
    
    # Simulation d'un score de qualité
    quality_score = random.uniform(0.6, 1.0)
    
    print(f"📊 Score de qualité: {quality_score:.2%}")
    
    # Décision basée sur le score
    if quality_score >= 0.9:
        print("✅ Excellente qualité → Processing normal")
        return 'high_quality_processing'
    elif quality_score >= 0.7:
        print("⚠️ Qualité moyenne → Processing avec nettoyage")
        return 'medium_quality_processing'
    else:
        print("❌ Qualité faible → Alertes et reprocessing")
        return 'low_quality_alert'

def process_high_quality(**context):
    """Traitement pour données de haute qualité"""
    print("🚀 Traitement rapide des données de haute qualité")
    
    data = {
        'processing_type': 'HIGH_QUALITY',
        'optimization': 'FULL',
        'estimated_time': '5 minutes',
        'records': random.randint(10000, 20000)
    }
    
    context['task_instance'].xcom_push(key='processing_result', value=data)
    return data

def process_medium_quality(**context):
    """Traitement pour données de qualité moyenne avec nettoyage"""
    print("🧹 Nettoyage et traitement des données")
    
    # Simulation de nettoyage
    steps = [
        "Suppression des doublons",
        "Correction des valeurs manquantes",
        "Normalisation des formats",
        "Validation des contraintes"
    ]
    
    results = []
    for step in steps:
        print(f"  → {step}")
        results.append({
            'step': step,
            'records_affected': random.randint(100, 1000),
            'status': 'COMPLETED'
        })
    
    data = {
        'processing_type': 'MEDIUM_QUALITY',
        'cleaning_steps': results,
        'estimated_time': '15 minutes',
        'records': random.randint(8000, 15000)
    }
    
    context['task_instance'].xcom_push(key='processing_result', value=data)
    return data

def alert_low_quality(**context):
    """Alerte pour données de faible qualité"""
    print("🚨 ALERTE: Données de faible qualité détectées!")
    
    alert = {
        'severity': 'HIGH',
        'timestamp': datetime.now().isoformat(),
        'action_required': 'Manual review',
        'notification_sent_to': ['admin@formation.com', 'quality@formation.com']
    }
    
    print(f"📧 Notifications envoyées à: {alert['notification_sent_to']}")
    
    # Ici on pourrait déclencher un vrai système d'alertes
    context['task_instance'].xcom_push(key='alert_details', value=alert)
    
    # On pourrait lever une exception pour arrêter le pipeline
    # raise AirflowSkipException("Pipeline arrêté pour revue manuelle")
    
    return alert

def generate_dynamic_tasks_config(**context):
    """Génère la configuration pour les tâches dynamiques"""
    print("⚙️ Génération de la configuration des tâches dynamiques...")
    
    # Simulation: nombre de sources à traiter
    num_sources = random.randint(3, 7)
    
    sources = []
    for i in range(num_sources):
        sources.append({
            'id': f'source_{i+1}',
            'type': random.choice(['API', 'DATABASE', 'FILE', 'STREAM']),
            'priority': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'estimated_records': random.randint(1000, 10000)
        })
    
    print(f"📋 {len(sources)} sources à traiter")
    
    return sources

def process_source(source_id, source_type, **context):
    """Traite une source de données spécifique"""
    print(f"📥 Traitement de {source_id} (Type: {source_type})")
    
    # Simulation du traitement
    result = {
        'source_id': source_id,
        'type': source_type,
        'records_processed': random.randint(500, 5000),
        'processing_time': random.uniform(1, 10),
        'status': 'SUCCESS'
    }
    
    print(f"✅ {source_id} traité: {result['records_processed']} enregistrements")
    
    return result

def aggregate_results(**context):
    """Agrège les résultats de tous les traitements"""
    print("📊 Agrégation des résultats...")
    
    ti = context['task_instance']
    
    # Récupérer les résultats de toutes les tâches dynamiques
    task_ids = context['dag_run'].get_task_instances()
    
    total_records = 0
    total_time = 0
    processed_sources = []
    
    for task in task_ids:
        if 'process_source_' in task.task_id:
            result = ti.xcom_pull(task_ids=task.task_id)
            if result:
                total_records += result.get('records_processed', 0)
                total_time += result.get('processing_time', 0)
                processed_sources.append(result.get('source_id', 'unknown'))
    
    summary = {
        'total_records': total_records,
        'total_processing_time': round(total_time, 2),
        'sources_processed': len(processed_sources),
        'average_records_per_source': total_records // max(len(processed_sources), 1),
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"""
    📈 Résumé du traitement:
    - Sources traitées: {summary['sources_processed']}
    - Total enregistrements: {summary['total_records']:,}
    - Temps total: {summary['total_processing_time']:.2f} secondes
    - Moyenne par source: {summary['average_records_per_source']:,} enregistrements
    """)
    
    return summary

def trigger_downstream_dag(**context):
    """Décide si déclencher un DAG en aval"""
    ti = context['task_instance']
    
    # Récupérer les métriques d'agrégation
    summary = ti.xcom_pull(task_ids='reporting.aggregate_results')
    
    if summary and summary.get('total_records', 0) > 10000:
        print("🚀 Déclenchement du DAG de reporting avancé")
        return 'trigger_reporting_dag'
    else:
        print("⏭️ Pas assez de données, skip du reporting avancé")
        return 'skip_reporting'

# ============================================================================
# DÉFINITION DES TASKS
# ============================================================================

# Task de démarrage
start = DummyOperator(task_id='start', dag=dag)

# Sensor pour attendre un fichier (simulation)
wait_for_data = DummyOperator(
    task_id='wait_for_data',
    dag=dag,
    doc_md="""
    ### FileSensor (simulé)
    En production, utiliserait FileSensor pour attendre un fichier:
    ```python
    FileSensor(
        task_id='wait_for_data',
        filepath='/data/input/daily_data.csv',
        poke_interval=30,
        timeout=600
    )
    ```
    """
)

# Branching basé sur la qualité des données
quality_check = BranchPythonOperator(
    task_id='check_quality',
    python_callable=check_data_quality,
    provide_context=True,
    dag=dag
)

# Branches pour différentes qualités
high_quality = PythonOperator(
    task_id='high_quality_processing',
    python_callable=process_high_quality,
    provide_context=True,
    dag=dag
)

medium_quality = PythonOperator(
    task_id='medium_quality_processing',
    python_callable=process_medium_quality,
    provide_context=True,
    dag=dag
)

low_quality = PythonOperator(
    task_id='low_quality_alert',
    python_callable=alert_low_quality,
    provide_context=True,
    dag=dag
)

# Point de convergence après branching
join_branches = DummyOperator(
    task_id='join_branches',
    trigger_rule='none_failed_or_skipped',
    dag=dag
)

# ============================================================================
# TASK GROUP: Processing Pipeline
# ============================================================================

with TaskGroup('processing_pipeline', dag=dag) as processing_group:
    
    # Génération de la configuration
    generate_config = PythonOperator(
        task_id='generate_config',
        python_callable=generate_dynamic_tasks_config,
        dag=dag
    )
    
    # Tâches dynamiques (simulation avec tâches statiques)
    # En production, on utiliserait expand() ou des tâches générées dynamiquement
    dynamic_tasks = []
    for i in range(5):  # Simulation de 5 sources
        task = PythonOperator(
            task_id=f'process_source_{i+1}',
            python_callable=process_source,
            op_kwargs={
                'source_id': f'source_{i+1}',
                'source_type': ['API', 'DATABASE', 'FILE'][i % 3]
            },
            provide_context=True,
            dag=dag
        )
        dynamic_tasks.append(task)
    
    # Synchronisation des tâches dynamiques
    sync_point = DummyOperator(
        task_id='sync_dynamic_tasks',
        trigger_rule='none_failed',
        dag=dag
    )
    
    # Chaînage dans le groupe
    generate_config >> dynamic_tasks >> sync_point

# ============================================================================
# TASK GROUP: Reporting
# ============================================================================

with TaskGroup('reporting', dag=dag) as reporting_group:
    
    # Agrégation des résultats
    aggregate = PythonOperator(
        task_id='aggregate_results',
        python_callable=aggregate_results,
        provide_context=True,
        dag=dag
    )
    
    # Génération de rapports
    generate_report = BashOperator(
        task_id='generate_report',
        bash_command="""
            echo "📄 Génération du rapport..."
            echo "Format: PDF, Excel, JSON"
            echo "Destination: /data/reports/daily_report_{{ ds }}.pdf"
            echo "✅ Rapport généré avec succès"
        """,
        dag=dag
    )
    
    # Envoi du rapport
    send_report = DummyOperator(
        task_id='send_report',
        dag=dag,
        doc_md="Envoi du rapport par email aux stakeholders"
    )
    
    # Chaînage dans le groupe
    aggregate >> generate_report >> send_report

# ============================================================================
# Décision finale: Trigger ou Skip
# ============================================================================

decide_trigger = BranchPythonOperator(
    task_id='decide_downstream_trigger',
    python_callable=trigger_downstream_dag,
    provide_context=True,
    dag=dag
)

# Trigger conditionnel d'un autre DAG
trigger_reporting = DummyOperator(
    task_id='trigger_reporting_dag',
    dag=dag,
    doc_md="""
    En production, utiliserait TriggerDagRunOperator:
    ```python
    TriggerDagRunOperator(
        task_id='trigger_reporting_dag',
        trigger_dag_id='advanced_reporting_pipeline',
        conf={'source': 'advanced_patterns', 'date': '{{ ds }}'}
    )
    ```
    """
)

skip_reporting = DummyOperator(
    task_id='skip_reporting',
    dag=dag
)

# Task de fin
end = DummyOperator(
    task_id='end',
    trigger_rule='none_failed_or_skipped',
    dag=dag
)

# ============================================================================
# DÉFINITION DES DÉPENDANCES
# ============================================================================

# Flow principal
start >> wait_for_data >> quality_check

# Branches de qualité
quality_check >> [high_quality, medium_quality, low_quality]

# Convergence
[high_quality, medium_quality, low_quality] >> join_branches

# Pipeline de traitement
join_branches >> processing_group >> reporting_group

# Décision finale
reporting_group >> decide_trigger
decide_trigger >> [trigger_reporting, skip_reporting]
[trigger_reporting, skip_reporting] >> end