"""
DAG de démonstration basique
Module 2 - Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import random
import time

# Configuration par défaut du DAG
default_args = {
    'owner': 'formation',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['admin@formation.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'tags': ['demo', 'basic'],
}

# Définition du DAG
dag = DAG(
    '01_demo_basic_dag',
    default_args=default_args,
    description='DAG de démonstration des concepts de base',
    schedule_interval='0 */2 * * *',  # Toutes les 2 heures
    catchup=False,
    max_active_runs=1,
    doc_md="""
    ## DAG de Démonstration Basique
    
    Ce DAG illustre les concepts fondamentaux d'Airflow:
    - Tasks et dépendances
    - Opérateurs Python et Bash
    - Gestion des erreurs et retries
    - Passage de données entre tasks (XCom)
    
    ### Architecture
    ```
    start → extract_data → transform_data → validate → [load_to_db, send_notification] → end
    ```
    """
)

# ============================================================================
# FONCTIONS PYTHON POUR LES TASKS
# ============================================================================

def extract_data_func(**context):
    """Simule l'extraction de données depuis une source"""
    print("📊 Extraction des données en cours...")
    
    # Simulation d'extraction
    time.sleep(2)
    
    # Générer des données aléatoires
    data = {
        'timestamp': datetime.now().isoformat(),
        'records_count': random.randint(1000, 5000),
        'source': 'API_DEMO',
        'status': 'SUCCESS'
    }
    
    print(f"✅ Extraction terminée: {data['records_count']} enregistrements")
    
    # Pousser les données vers XCom pour la tâche suivante
    context['task_instance'].xcom_push(key='raw_data', value=data)
    
    return data

def transform_data_func(**context):
    """Transforme les données extraites"""
    print("🔄 Transformation des données...")
    
    # Récupérer les données de la tâche précédente
    ti = context['task_instance']
    raw_data = ti.xcom_pull(task_ids='extract_data', key='raw_data')
    
    if not raw_data:
        raise ValueError("Aucune donnée reçue de l'extraction!")
    
    # Simulation de transformation
    transformed_data = {
        **raw_data,
        'transformed_at': datetime.now().isoformat(),
        'records_processed': raw_data['records_count'] * 0.95,  # 95% de données valides
        'quality_score': random.uniform(0.85, 0.99)
    }
    
    print(f"✅ Transformation terminée: {transformed_data['records_processed']:.0f} enregistrements traités")
    
    # Pousser les données transformées
    ti.xcom_push(key='transformed_data', value=transformed_data)
    
    return transformed_data

def validate_data_func(**context):
    """Valide la qualité des données"""
    print("✔️ Validation des données...")
    
    ti = context['task_instance']
    data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    
    # Critères de validation
    validations = {
        'record_count_check': data['records_processed'] > 0,
        'quality_check': data['quality_score'] > 0.8,
        'timestamp_check': 'timestamp' in data
    }
    
    # Vérifier toutes les validations
    all_valid = all(validations.values())
    
    if not all_valid:
        failed_checks = [k for k, v in validations.items() if not v]
        raise ValueError(f"Validation échouée: {failed_checks}")
    
    print(f"✅ Toutes les validations passées: {validations}")
    
    return {'validation_status': 'PASSED', 'checks': validations}

def load_to_database_func(**context):
    """Simule le chargement dans une base de données"""
    print("💾 Chargement dans la base de données...")
    
    ti = context['task_instance']
    data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    
    # Simulation de chargement (avec possibilité d'échec aléatoire pour démonstration)
    if random.random() < 0.1:  # 10% de chance d'échec
        raise Exception("Erreur de connexion à la base de données (simulation)")
    
    time.sleep(3)  # Simulation du temps de chargement
    
    result = {
        'loaded_records': data['records_processed'],
        'load_time': datetime.now().isoformat(),
        'target_table': 'demo_table',
        'status': 'SUCCESS'
    }
    
    print(f"✅ Chargement terminé: {result['loaded_records']:.0f} enregistrements dans {result['target_table']}")
    
    return result

def send_notification_func(**context):
    """Envoie une notification de fin de traitement"""
    print("📧 Envoi de notification...")
    
    ti = context['task_instance']
    
    # Récupérer toutes les métriques
    extract_data = ti.xcom_pull(task_ids='extract_data', key='raw_data')
    transform_data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    load_result = ti.xcom_pull(task_ids='load_to_database')
    
    # Créer le message
    message = f"""
    🎉 Pipeline ETL Terminé avec Succès!
    
    📊 Métriques:
    - Records extraits: {extract_data['records_count']}
    - Records traités: {transform_data['records_processed']:.0f}
    - Quality Score: {transform_data['quality_score']:.2%}
    - Records chargés: {load_result['loaded_records']:.0f}
    
    ⏰ Timestamps:
    - Début: {extract_data['timestamp']}
    - Fin: {load_result['load_time']}
    
    📍 Destination: {load_result['target_table']}
    """
    
    print(message)
    
    # Ici on pourrait envoyer un vrai email ou notification Slack
    return {'notification_sent': True, 'message': message}

# ============================================================================
# DÉFINITION DES TASKS
# ============================================================================

# Task de démarrage
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# Task d'extraction
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_func,
    provide_context=True,
    dag=dag,
)

# Task de transformation
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data_func,
    provide_context=True,
    dag=dag,
)

# Task de validation
validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data_func,
    provide_context=True,
    dag=dag,
)

# Task de chargement
load_task = PythonOperator(
    task_id='load_to_database',
    python_callable=load_to_database_func,
    provide_context=True,
    dag=dag,
    retries=3,  # Plus de retries pour cette tâche critique
)

# Task de notification
notify_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification_func,
    provide_context=True,
    dag=dag,
    trigger_rule='none_failed',  # S'exécute même si certaines tâches sont skipped
)

# Task de nettoyage (Bash)
cleanup_task = BashOperator(
    task_id='cleanup_temp_files',
    bash_command="""
        echo "🧹 Nettoyage des fichiers temporaires..."
        # Simulation de nettoyage
        echo "Fichiers temporaires: $(ls /tmp/*.tmp 2>/dev/null | wc -l)"
        echo "✅ Nettoyage terminé"
    """,
    dag=dag,
)

# Task de fin
end_task = DummyOperator(
    task_id='end',
    dag=dag,
    trigger_rule='none_failed_or_skipped',
)

# ============================================================================
# DÉFINITION DES DÉPENDANCES
# ============================================================================

# Chaîne linéaire principale
start_task >> extract_task >> transform_task >> validate_task

# Parallélisation après validation
validate_task >> [load_task, notify_task]

# Convergence vers le nettoyage
[load_task, notify_task] >> cleanup_task >> end_task

# ============================================================================
# DOCUMENTATION SUPPLÉMENTAIRE
# ============================================================================

# Documentation des tasks individuelles
extract_task.doc_md = """
### Task: Extract Data
Extrait les données depuis la source (API simulée).
Génère entre 1000 et 5000 enregistrements aléatoires.
"""

transform_task.doc_md = """
### Task: Transform Data
Applique des transformations sur les données:
- Filtre les données invalides (95% de taux de validité)
- Calcule un score de qualité
"""

validate_task.doc_md = """
### Task: Validate Data
Vérifie la qualité des données:
- Nombre d'enregistrements > 0
- Score de qualité > 0.8
- Présence des champs obligatoires
"""

load_task.doc_md = """
### Task: Load to Database
Charge les données dans la base cible.
Possibilité d'échec simulé (10%) pour démontrer les retries.
"""