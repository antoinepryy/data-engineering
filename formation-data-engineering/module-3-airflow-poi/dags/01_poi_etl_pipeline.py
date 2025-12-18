"""
DAG ETL Pipeline pour les POI (Points Of Interest)
Module 3 - Formation Data Engineering

Ce DAG implémente le pipeline ETL complet:
1. EXTRACT: Génération/Récupération des données depuis plusieurs sources (via Providers)
2. TRANSFORM: Normalisation et validation des données
3. LOAD: Chargement dans la base de données

Architecture:
    [Setup] → [Extract Sources via Providers] → [Normalize] → [Validate] → [Load to DB] → [Notify]

Le système de Providers permet de switcher entre:
- Fake data (défaut) pour le développement et les tests
- Vraies APIs (Datatourisme, Apidae, TripAdvisor, Tourinsoft) en production
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
import json
import os
import sys
from typing import List, Dict, Any

# Ajouter le chemin des scripts
sys.path.insert(0, '/opt/airflow/scripts')

# Configuration par défaut
default_args = {
    'owner': 'formation',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['admin@formation.com'],
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'tags': ['poi', 'etl', 'module3'],
}

# Définition du DAG
dag = DAG(
    '01_poi_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL complet pour les Points Of Interest',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    doc_md="""
    ## Pipeline ETL POI

    Ce DAG traite les données des Points Of Interest depuis plusieurs sources:
    - **Datatourisme**: Données touristiques françaises
    - **Apidae**: Base de données tourisme régional
    - **TripAdvisor**: Avis et notes utilisateurs
    - **Tourinsoft**: Données offices de tourisme

    ### Architecture des Providers

    Le pipeline utilise un système de **Providers** qui permet de:
    - Utiliser des **données fake** pour le développement (défaut)
    - Basculer vers les **vraies APIs** en production
    - Configurer chaque source indépendamment

    Configuration via variables d'environnement:
    - `POI_USE_REAL_APIS`: "true" pour activer les vraies APIs
    - `POI_PROVIDER_CONFIG`: Chemin vers le fichier de configuration

    ### Processus
    1. **Extraction**: Via le système de Providers (fake ou réel)
    2. **Transformation**: Normalisation au format unifié
    3. **Validation**: Contrôle qualité des données
    4. **Chargement**: Stockage dans la base de données

    ### Métriques suivies
    - Nombre de POI par source
    - Taux de données valides
    - Doublons détectés
    """
)


# ============================================================================
# CONSTANTES
# ============================================================================

DATA_DIR = '/opt/airflow/data'
RAW_DIR = f'{DATA_DIR}/raw'
PROCESSED_DIR = f'{DATA_DIR}/processed'
OUTPUT_DIR = f'{DATA_DIR}/output'
CONFIG_DIR = '/opt/airflow/config'

# Sources supportées (correspondent aux ProviderType)
SOURCES = ['datatourisme', 'apidae', 'tripadvisor', 'tourinsoft']


# ============================================================================
# FONCTIONS ETL
# ============================================================================

def setup_directories(**context):
    """Crée les répertoires nécessaires"""
    print("📁 Configuration des répertoires...")

    for directory in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR]:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")

    return {'status': 'OK', 'directories_created': [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR]}


def get_provider_factory():
    """
    Récupère la factory de providers configurée.
    Utilise la configuration par défaut ou les variables d'environnement.
    """
    try:
        from providers import ProviderFactory

        # Essayer d'abord avec le fichier de config
        config_path = os.environ.get('POI_PROVIDER_CONFIG', f'{CONFIG_DIR}/providers.json')
        if os.path.exists(config_path):
            print(f"  📋 Chargement de la configuration depuis {config_path}")
            return ProviderFactory.from_config_file(config_path)
        else:
            print("  📋 Utilisation de la configuration par variables d'environnement")
            return ProviderFactory.from_env()
    except ImportError:
        print("  ⚠️ Module providers non disponible")
        return None


def extract_with_provider(source: str, num_pois: int = 50, **context):
    """
    Extrait les données via le système de Providers.

    Le provider utilisé (fake ou réel) dépend de la configuration.
    Si le module providers n'est pas disponible, utilise un fallback simplifié.

    Args:
        source: Nom de la source (datatourisme, apidae, etc.)
        num_pois: Nombre de POI à extraire (pour fake data)
        **context: Contexte Airflow

    Returns:
        Résultat de l'extraction avec métadonnées
    """
    print(f"📥 Extraction des données depuis {source.upper()}...")

    ti = context['task_instance']

    # Tenter d'utiliser le système de Providers
    try:
        from providers import ProviderFactory, ProviderType

        factory = get_provider_factory()
        if factory:
            # Afficher le statut des providers
            status = factory.get_provider_status()
            source_status = status.get(source, {})
            mode = source_status.get('mode', 'fake')
            print(f"  📋 Mode: {mode.upper()}")

            # Obtenir le provider approprié
            provider_type = ProviderType(source)
            provider = factory.get_provider(provider_type)

            # Extraire les données
            extraction = provider.extract(num_pois=num_pois)

            if extraction.success:
                pois = extraction.data

                # Normaliser via le provider
                normalized_pois = provider.normalize(pois)

                # Sauvegarder
                output_file = f"{RAW_DIR}/pois_{source}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized_pois, f, ensure_ascii=False, indent=2)

                result = {
                    'source': source,
                    'provider_mode': mode,
                    'count': len(normalized_pois),
                    'file': output_file,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': extraction.metadata
                }

                print(f"  ✓ {len(normalized_pois)} POI extraits depuis {source} (mode {mode})")
                ti.xcom_push(key=f'extract_{source}', value=result)
                return result
            else:
                print(f"  ❌ Erreur d'extraction: {extraction.errors}")
                raise Exception(f"Extraction failed: {extraction.errors}")

    except ImportError as e:
        print(f"  ⚠️ Module providers non disponible ({e}), utilisation du fallback")
    except Exception as e:
        print(f"  ⚠️ Erreur avec le provider ({e}), utilisation du fallback")

    # Fallback: génération simplifiée sans le module providers
    return _extract_fallback(source, num_pois, **context)


def _extract_fallback(source: str, num_pois: int, **context):
    """
    Fallback pour l'extraction si le module providers n'est pas disponible.
    Génère des données fake simplifiées.
    """
    import random

    print(f"  🔄 Fallback: génération simplifiée pour {source}")

    ti = context['task_instance']
    pois = []

    poi_types = ['sites', 'activities', 'restaurants', 'accommodations', 'events']
    regions = ['Ile-de-France', 'Provence-Alpes-Côte d\'Azur', 'Auvergne-Rhône-Alpes']

    for i in range(num_pois):
        poi = {
            'id': None,
            'source': source,
            'reference': f"{source[:2].upper()}{random.randint(10000, 99999)}",
            'poi_name': {'fr': f"POI Test {i+1} - {source}"},
            'types': [random.choice(poi_types)],
            'tags': [f"tag_{random.randint(1, 10)}"],
            'addresses': [{
                'city': f"Ville_{random.randint(1, 100)}",
                'zip_code': str(random.randint(10000, 99999)),
                'region': random.choice(regions),
                'country': 'France'
            }],
            'geopoints': [{
                'latitude': 48.8 + random.uniform(-0.5, 0.5),
                'longitude': 2.3 + random.uniform(-0.5, 0.5)
            }],
            'closed': random.random() < 0.05,
            'display': random.random() > 0.02,
            'sources': [{
                'source': source,
                'reference': f"{source[:2].upper()}{random.randint(10000, 99999)}",
                'last_update': datetime.now().isoformat()
            }]
        }
        pois.append(poi)

    # Sauvegarder
    output_file = f"{RAW_DIR}/pois_{source}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    result = {
        'source': source,
        'provider_mode': 'fallback',
        'count': len(pois),
        'file': output_file,
        'timestamp': datetime.now().isoformat()
    }

    print(f"  ✓ {len(pois)} POI générés en mode fallback")
    ti.xcom_push(key=f'extract_{source}', value=result)

    return result


def normalize_poi_data(source: str, **context):
    """
    Normalise les données d'une source au format unifié.
    Applique les règles de transformation spécifiques à chaque source.
    """
    print(f"🔄 Normalisation des données {source.upper()}...")

    ti = context['task_instance']
    extract_result = ti.xcom_pull(key=f'extract_{source}')

    if not extract_result:
        raise ValueError(f"Aucune donnée extraite pour {source}")

    # Charger les données
    with open(extract_result['file'], 'r', encoding='utf-8') as f:
        pois = json.load(f)

    normalized_pois = []
    errors = []

    for idx, poi in enumerate(pois):
        try:
            # Normalisation du POI
            normalized = {
                'id': None,
                'closed': poi.get('closed', False),
                'display': poi.get('display', True),
                'tags': poi.get('tags', []),
                'types': poi.get('types', []),

                # Normaliser le nom (s'assurer qu'il existe)
                'poi_name': poi.get('poi_name', {}),

                # Normaliser les adresses
                'addresses': [],
                'geopoints': [],
                'contacts': poi.get('contacts', []),
                'descriptions': poi.get('descriptions', []),
                'pictures': poi.get('pictures', []),
                'products': poi.get('products', []),
                'schedules': poi.get('schedules', []),
                'ratings': poi.get('ratings'),
                'age_limit': poi.get('age_limit'),
                'duration': poi.get('duration'),
                'group_size_limit': poi.get('group_size_limit'),
                'sources': poi.get('sources', [])
            }

            # Normaliser les adresses
            for addr in poi.get('addresses', []):
                normalized_addr = {
                    'insee_code': addr.get('insee_code'),
                    'city': addr.get('city', '').strip() if addr.get('city') else None,
                    'zip_code': str(addr.get('zip_code', '')).strip() if addr.get('zip_code') else None,
                    'department': addr.get('department'),
                    'region': addr.get('region'),
                    'country': addr.get('country', 'France'),
                    'address_complement': addr.get('address_complement'),
                    'street_addresses': addr.get('street_addresses', [])
                }
                normalized['addresses'].append(normalized_addr)

            # Normaliser les geopoints
            for geo in poi.get('geopoints', []):
                if geo.get('latitude') and geo.get('longitude'):
                    normalized_geo = {
                        'latitude': float(geo['latitude']),
                        'longitude': float(geo['longitude']),
                        'altitude': geo.get('altitude')
                    }
                    normalized['geopoints'].append(normalized_geo)

            normalized_pois.append(normalized)

        except Exception as e:
            errors.append({
                'index': idx,
                'error': str(e),
                'poi_id': poi.get('sources', [{}])[0].get('reference', 'unknown')
            })

    # Sauvegarder les données normalisées
    output_file = f"{PROCESSED_DIR}/pois_{source}_normalized_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_pois, f, ensure_ascii=False, indent=2)

    result = {
        'source': source,
        'input_count': len(pois),
        'output_count': len(normalized_pois),
        'error_count': len(errors),
        'errors': errors[:10],  # Limiter les erreurs stockées
        'file': output_file,
        'timestamp': datetime.now().isoformat()
    }

    print(f"  ✓ {len(normalized_pois)}/{len(pois)} POI normalisés ({len(errors)} erreurs)")
    ti.xcom_push(key=f'normalize_{source}', value=result)

    return result


def validate_poi_data(**context):
    """
    Valide les données normalisées de toutes les sources.
    Effectue des contrôles de qualité.

    Peut utiliser la validation du provider si disponible.
    """
    print("✔️ Validation des données...")

    ti = context['task_instance']

    # Tenter d'utiliser la validation des providers
    validator = None
    try:
        from providers import FakeDataProvider, ProviderConfig
        config = ProviderConfig(name="validator", source_type="fake")
        validator = FakeDataProvider(config)
        print("  📋 Utilisation de la validation des providers")
    except (ImportError, Exception) as e:
        print(f"  📋 Utilisation de la validation standard ({e})")

    all_pois = []
    validation_results = {
        'sources': {},
        'total_input': 0,
        'total_valid': 0,
        'total_invalid': 0,
        'validation_rules': {}
    }

    # Charger et valider chaque source
    for source in SOURCES:
        normalize_result = ti.xcom_pull(key=f'normalize_{source}')

        if not normalize_result:
            print(f"  ⚠️ Pas de données pour {source}")
            continue

        with open(normalize_result['file'], 'r', encoding='utf-8') as f:
            pois = json.load(f)

        valid_pois = []
        invalid_pois = []

        for poi in pois:
            is_valid = True
            validation_errors = []

            # Utiliser le validateur du provider si disponible
            if validator:
                is_valid, validation_errors = validator.validate(poi)
            else:
                # Validation standard
                # Règle 1: Le POI doit avoir un nom
                if not poi.get('poi_name') or not poi['poi_name'].get('fr'):
                    is_valid = False
                    validation_errors.append('missing_name')

                # Règle 2: Le POI doit avoir au moins une adresse ou un geopoint
                if not poi.get('addresses') and not poi.get('geopoints'):
                    is_valid = False
                    validation_errors.append('missing_location')

                # Règle 3: Le POI doit avoir au moins un type
                if not poi.get('types'):
                    is_valid = False
                    validation_errors.append('missing_type')

                # Règle 4: Les coordonnées doivent être valides (si présentes)
                for geo in poi.get('geopoints', []):
                    lat = geo.get('latitude', 0)
                    lon = geo.get('longitude', 0)
                    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                        is_valid = False
                        validation_errors.append('invalid_coordinates')
                        break

                # Règle 5: Le code postal doit être valide (si présent)
                for addr in poi.get('addresses', []):
                    zip_code = addr.get('zip_code', '')
                    if zip_code and (not zip_code.isdigit() or len(zip_code) != 5):
                        is_valid = False
                        validation_errors.append('invalid_zip_code')
                        break

            if is_valid:
                valid_pois.append(poi)
            else:
                poi['_validation_errors'] = validation_errors
                invalid_pois.append(poi)

        validation_results['sources'][source] = {
            'total': len(pois),
            'valid': len(valid_pois),
            'invalid': len(invalid_pois),
            'validation_rate': len(valid_pois) / len(pois) if pois else 0
        }

        all_pois.extend(valid_pois)
        validation_results['total_input'] += len(pois)
        validation_results['total_valid'] += len(valid_pois)
        validation_results['total_invalid'] += len(invalid_pois)

    # Sauvegarder les POI valides
    output_file = f"{PROCESSED_DIR}/pois_validated_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_pois, f, ensure_ascii=False, indent=2)

    validation_results['file'] = output_file
    validation_results['timestamp'] = datetime.now().isoformat()
    validation_results['overall_validation_rate'] = (
        validation_results['total_valid'] / validation_results['total_input']
        if validation_results['total_input'] > 0 else 0
    )

    print(f"\n📊 Résumé de la validation:")
    print(f"  - Total POI: {validation_results['total_input']}")
    print(f"  - POI valides: {validation_results['total_valid']}")
    print(f"  - POI invalides: {validation_results['total_invalid']}")
    print(f"  - Taux de validation: {validation_results['overall_validation_rate']:.2%}")

    for source, stats in validation_results['sources'].items():
        print(f"\n  {source.upper()}:")
        print(f"    - {stats['valid']}/{stats['total']} valides ({stats['validation_rate']:.2%})")

    ti.xcom_push(key='validation_results', value=validation_results)

    return validation_results


def check_quality_threshold(**context):
    """
    Vérifie si le taux de validation atteint le seuil minimum.
    Décide si on continue vers le chargement ou si on alerte.
    """
    ti = context['task_instance']
    validation_results = ti.xcom_pull(key='validation_results')

    QUALITY_THRESHOLD = 0.8  # 80% minimum

    if validation_results['overall_validation_rate'] >= QUALITY_THRESHOLD:
        print(f"✅ Qualité OK: {validation_results['overall_validation_rate']:.2%} >= {QUALITY_THRESHOLD:.2%}")
        return 'load_to_database'
    else:
        print(f"❌ Qualité insuffisante: {validation_results['overall_validation_rate']:.2%} < {QUALITY_THRESHOLD:.2%}")
        return 'quality_alert'


def load_to_database(**context):
    """
    Charge les données validées dans la base de données.
    Simule l'insertion dans PostgreSQL.
    """
    print("💾 Chargement dans la base de données...")

    ti = context['task_instance']
    validation_results = ti.xcom_pull(key='validation_results')

    # Charger les POI validés
    with open(validation_results['file'], 'r', encoding='utf-8') as f:
        pois = json.load(f)

    # Simulation du chargement en base
    # En production, utiliser SQLAlchemy ou psycopg2

    loaded_count = 0
    errors = []

    for idx, poi in enumerate(pois):
        try:
            # Simuler l'insertion
            # INSERT INTO pois (data) VALUES (poi)
            poi['id'] = idx + 1  # Assigner un ID
            loaded_count += 1

        except Exception as e:
            errors.append({
                'index': idx,
                'error': str(e)
            })

    # Sauvegarder le résultat final
    output_file = f"{OUTPUT_DIR}/pois_loaded_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    result = {
        'loaded_count': loaded_count,
        'error_count': len(errors),
        'file': output_file,
        'timestamp': datetime.now().isoformat(),
        'database': 'poi_database',
        'table': 'pois'
    }

    print(f"  ✓ {loaded_count} POI chargés dans la base de données")
    if errors:
        print(f"  ⚠️ {len(errors)} erreurs de chargement")

    ti.xcom_push(key='load_results', value=result)

    return result


def quality_alert(**context):
    """
    Envoie une alerte en cas de problème de qualité.
    """
    print("🚨 ALERTE QUALITÉ!")

    ti = context['task_instance']
    validation_results = ti.xcom_pull(key='validation_results')

    alert = {
        'severity': 'HIGH',
        'type': 'QUALITY_THRESHOLD_NOT_MET',
        'validation_rate': validation_results['overall_validation_rate'],
        'threshold': 0.8,
        'timestamp': datetime.now().isoformat(),
        'action_required': 'Vérifier les données sources et les règles de validation',
        'details': validation_results['sources']
    }

    print(f"\n📧 Notification envoyée:")
    print(f"  - Taux de validation: {alert['validation_rate']:.2%}")
    print(f"  - Seuil requis: {alert['threshold']:.2%}")
    print(f"  - Action requise: {alert['action_required']}")

    # En production: envoyer email, Slack, etc.

    return alert


def send_success_notification(**context):
    """
    Envoie une notification de succès avec les métriques.
    """
    print("📧 Envoi de la notification de succès...")

    ti = context['task_instance']

    # Récupérer les métriques
    validation_results = ti.xcom_pull(key='validation_results')
    load_results = ti.xcom_pull(key='load_results')

    # Récupérer le mode des providers
    provider_modes = {}
    for source in SOURCES:
        extract_result = ti.xcom_pull(key=f'extract_{source}')
        if extract_result:
            provider_modes[source] = extract_result.get('provider_mode', 'unknown')

    message = f"""
    ✅ Pipeline ETL POI terminé avec succès!

    📋 Configuration Providers:
    """

    for source, mode in provider_modes.items():
        message += f"\n    - {source}: {mode.upper()}"

    message += f"""

    📊 Métriques:
    - POI traités: {validation_results['total_input']}
    - POI valides: {validation_results['total_valid']}
    - POI chargés: {load_results['loaded_count']}
    - Taux de validation: {validation_results['overall_validation_rate']:.2%}

    📁 Fichiers générés:
    - {load_results['file']}

    ⏰ Timestamp: {datetime.now().isoformat()}

    📈 Par source:
    """

    for source, stats in validation_results['sources'].items():
        message += f"\n    - {source}: {stats['valid']}/{stats['total']} ({stats['validation_rate']:.2%})"

    print(message)

    return {'notification_sent': True, 'message': message}


# ============================================================================
# DÉFINITION DES TASKS
# ============================================================================

# Task de démarrage
start = DummyOperator(
    task_id='start',
    dag=dag
)

# Setup des répertoires
setup = PythonOperator(
    task_id='setup_directories',
    python_callable=setup_directories,
    dag=dag
)

# ============================================================================
# TASK GROUP: Extraction par source (via Providers)
# ============================================================================

with TaskGroup('extract_sources', dag=dag) as extract_group:

    extract_tasks = []
    for source in SOURCES:
        task = PythonOperator(
            task_id=f'extract_{source}',
            python_callable=extract_with_provider,  # Utilise le système de providers
            op_kwargs={'source': source, 'num_pois': 30},
            provide_context=True,
            dag=dag
        )
        extract_tasks.append(task)

# ============================================================================
# TASK GROUP: Normalisation par source
# ============================================================================

with TaskGroup('normalize_sources', dag=dag) as normalize_group:

    normalize_tasks = []
    for source in SOURCES:
        task = PythonOperator(
            task_id=f'normalize_{source}',
            python_callable=normalize_poi_data,
            op_kwargs={'source': source},
            provide_context=True,
            dag=dag
        )
        normalize_tasks.append(task)

# Validation
validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_poi_data,
    provide_context=True,
    dag=dag
)

# Branching sur la qualité
quality_check = BranchPythonOperator(
    task_id='check_quality',
    python_callable=check_quality_threshold,
    provide_context=True,
    dag=dag
)

# Chargement en base
load = PythonOperator(
    task_id='load_to_database',
    python_callable=load_to_database,
    provide_context=True,
    dag=dag
)

# Alerte qualité
alert = PythonOperator(
    task_id='quality_alert',
    python_callable=quality_alert,
    provide_context=True,
    dag=dag
)

# Point de convergence
join = DummyOperator(
    task_id='join',
    trigger_rule='none_failed_or_skipped',
    dag=dag
)

# Notification de succès
notify = PythonOperator(
    task_id='send_notification',
    python_callable=send_success_notification,
    provide_context=True,
    trigger_rule='none_failed',
    dag=dag
)

# Fin
end = DummyOperator(
    task_id='end',
    trigger_rule='none_failed_or_skipped',
    dag=dag
)


# ============================================================================
# DÉFINITION DES DÉPENDANCES
# ============================================================================

# Flow principal
start >> setup >> extract_group >> normalize_group >> validate >> quality_check

# Branches qualité
quality_check >> [load, alert]

# Convergence
[load, alert] >> join >> notify >> end


# ============================================================================
# DOCUMENTATION
# ============================================================================

setup.doc_md = """
### Setup Directories
Crée les répertoires nécessaires pour le pipeline:
- `/data/raw`: Données brutes extraites
- `/data/processed`: Données normalisées et validées
- `/data/output`: Données finales chargées
"""

validate.doc_md = """
### Validate Data
Applique les règles de validation:
1. Le POI doit avoir un nom (FR)
2. Le POI doit avoir une localisation
3. Le POI doit avoir un type
4. Les coordonnées doivent être valides
5. Le code postal doit être valide

Utilise le validateur du Provider si disponible.
"""

load.doc_md = """
### Load to Database
Charge les données validées dans PostgreSQL.
En production, utilise SQLAlchemy pour l'insertion.
"""
