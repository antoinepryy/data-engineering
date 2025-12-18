"""
DAG de Détection des Doublons et Agrégation des POI
Module 3 - Formation Data Engineering

Ce DAG implémente le processus de détection des redondances:
1. Comparaison avec la base de données existante
2. Détection par références communes
3. Détection par mesures de similarité (nom, coordonnées, adresse)
4. Agrégation des données redondantes

Architecture:
    [Load Data] → [Check DB] → [Find Common Refs] → [Similarity Matching] → [Aggregate] → [Store Results]
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
import math
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

# Configuration par défaut
default_args = {
    'owner': 'formation',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['admin@formation.com'],
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'tags': ['poi', 'deduplication', 'aggregation', 'module3'],
}

# Définition du DAG
dag = DAG(
    '02_poi_deduplication',
    default_args=default_args,
    description='Détection des doublons et agrégation des POI',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    doc_md="""
    ## Détection des Doublons POI
    
    Ce DAG détecte les POI redondants entre différentes sources et les agrège.
    
    ### Méthodes de détection
    1. **Base de données**: Comparaison avec les POI existants
    2. **Références communes**: POI partageant une référence source
    3. **Similarité**: Comparaison nom + coordonnées + adresse
    
    ### Règles d'agrégation
    - Niveau de sourcing: POI validé par responsable > modifié par externe > automatique
    - Attributs simples: Max/Min/Union selon le type
    - Attributs complexes: Première valeur non nulle ou union
    
    ### Seuils de détection
    - Similarité nom: > 85%
    - Distance géographique: < 200m (validation directe) ou < 1km (avec adresse)
    - Similarité adresse: > 80%
    """
)


# ============================================================================
# CONSTANTES
# ============================================================================

DATA_DIR = '/opt/airflow/data'
PROCESSED_DIR = f'{DATA_DIR}/processed'
OUTPUT_DIR = f'{DATA_DIR}/output'
DEDUP_DIR = f'{DATA_DIR}/deduplication'

# Seuils de détection
NAME_SIMILARITY_THRESHOLD = 0.85
DIRECT_DISTANCE_THRESHOLD = 200  # mètres
EXTENDED_DISTANCE_THRESHOLD = 1000  # mètres
ADDRESS_SIMILARITY_THRESHOLD = 0.80


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance à vol d'oiseau entre deux points (formule Haversine).
    Retourne la distance en mètres.
    """
    R = 6371000  # Rayon de la Terre en mètres
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calcule la similarité entre deux chaînes de caractères.
    Retourne un score entre 0 et 1.
    """
    if not str1 or not str2:
        return 0.0
    
    # Normalisation
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    
    return SequenceMatcher(None, s1, s2).ratio()


def get_poi_name(poi: Dict) -> Optional[str]:
    """Extrait le nom français du POI."""
    if poi.get('poi_name'):
        return poi['poi_name'].get('fr', '')
    return None


def get_poi_coordinates(poi: Dict) -> Optional[Tuple[float, float]]:
    """Extrait les coordonnées du POI."""
    if poi.get('geopoints') and len(poi['geopoints']) > 0:
        geo = poi['geopoints'][0]
        if geo.get('latitude') and geo.get('longitude'):
            return (geo['latitude'], geo['longitude'])
    return None


def get_poi_department(poi: Dict) -> Optional[str]:
    """Extrait le département du POI (depuis le code postal)."""
    if poi.get('addresses') and len(poi['addresses']) > 0:
        zip_code = poi['addresses'][0].get('zip_code', '')
        if zip_code and len(zip_code) >= 2:
            return zip_code[:2]
    return None


def get_poi_address(poi: Dict) -> Optional[str]:
    """Extrait l'adresse complète du POI."""
    if poi.get('addresses') and len(poi['addresses']) > 0:
        addr = poi['addresses'][0]
        parts = []
        if addr.get('street_addresses'):
            parts.extend(addr['street_addresses'])
        if addr.get('city'):
            parts.append(addr['city'])
        if addr.get('zip_code'):
            parts.append(addr['zip_code'])
        return ' '.join(parts)
    return None


def get_source_reference(poi: Dict) -> Optional[Tuple[str, str]]:
    """Extrait la source et référence du POI."""
    if poi.get('sources') and len(poi['sources']) > 0:
        src = poi['sources'][0]
        return (src.get('source', ''), src.get('reference', ''))
    return None


# ============================================================================
# FONCTIONS D'AGRÉGATION
# ============================================================================

def aggregate_simple_attributes(pois: List[Dict]) -> Dict:
    """
    Agrège les attributs simples des POI redondants.
    """
    result = {
        'closed': max(poi.get('closed', False) for poi in pois),  # Si un dit fermé, c'est fermé
        'display': min(poi.get('display', True) for poi in pois),  # Si un dit non affichable, pas affichable
        'tags': list(set(tag for poi in pois for tag in poi.get('tags', []))),
        'types': list(set(t for poi in pois for t in poi.get('types', [])))
    }
    return result


def aggregate_complex_attributes(pois: List[Dict]) -> Dict:
    """
    Agrège les attributs complexes des POI redondants.
    """
    result = {}
    
    # Age limit: min/max
    age_limits = [poi.get('age_limit') for poi in pois if poi.get('age_limit')]
    if age_limits:
        result['age_limit'] = {
            'min_age': min(al.get('min_age', 0) for al in age_limits if al.get('min_age') is not None),
            'max_age': max(al.get('max_age', 99) for al in age_limits if al.get('max_age') is not None)
        }
    
    # Duration: moyenne
    durations = [poi.get('duration') for poi in pois if poi.get('duration')]
    if durations:
        result['duration'] = {
            'average_duration': int(sum(d.get('average_duration', 0) for d in durations) / len(durations)),
            'min_duration': int(sum(d.get('min_duration', 0) for d in durations) / len(durations)),
            'max_duration': int(sum(d.get('max_duration', 0) for d in durations) / len(durations))
        }
    
    # Group size limit: min/max
    group_limits = [poi.get('group_size_limit') for poi in pois if poi.get('group_size_limit')]
    if group_limits:
        result['group_size_limit'] = {
            'min_group_size': min(gl.get('min_group_size', 1) for gl in group_limits),
            'max_group_size': max(gl.get('max_group_size', 100) for gl in group_limits),
            'max_wheelchairs': max(gl.get('max_wheelchairs', 0) for gl in group_limits)
        }
    
    # POI name: première valeur non nulle par langue
    names = {}
    for poi in pois:
        if poi.get('poi_name'):
            for lang, name in poi['poi_name'].items():
                if lang not in names and name:
                    names[lang] = name
    result['poi_name'] = names
    
    return result


def aggregate_list_attributes(pois: List[Dict]) -> Dict:
    """
    Agrège les listes d'objets complexes des POI redondants.
    """
    result = {}
    
    # Addresses: fusionner par ville
    addresses_by_city = {}
    for poi in pois:
        for addr in poi.get('addresses', []):
            city = addr.get('city', 'unknown')
            if city not in addresses_by_city:
                addresses_by_city[city] = addr.copy()
            else:
                # Compléter les champs manquants
                existing = addresses_by_city[city]
                for key, value in addr.items():
                    if value and not existing.get(key):
                        existing[key] = value
                    elif key == 'street_addresses' and value:
                        existing_streets = set(existing.get('street_addresses', []))
                        existing_streets.update(value)
                        existing['street_addresses'] = list(existing_streets)
    result['addresses'] = list(addresses_by_city.values())
    
    # Contacts: fusionner par nom complet
    contacts_by_name = {}
    for poi in pois:
        for contact in poi.get('contacts', []):
            full_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            if full_name and full_name not in contacts_by_name:
                contacts_by_name[full_name] = contact.copy()
            elif full_name:
                existing = contacts_by_name[full_name]
                # Union des listes
                for key in ['roles', 'phones', 'emails', 'websites']:
                    if contact.get(key):
                        existing_list = set(existing.get(key, []))
                        existing_list.update(contact[key])
                        existing[key] = list(existing_list)
    result['contacts'] = list(contacts_by_name.values())
    
    # Descriptions: fusionner par type
    descriptions_by_type = {}
    for poi in pois:
        for desc in poi.get('descriptions', []):
            desc_type = desc.get('type', 'general')
            if desc_type not in descriptions_by_type:
                descriptions_by_type[desc_type] = desc.copy()
            else:
                # Première valeur non nulle par langue
                existing = descriptions_by_type[desc_type]
                for lang, text in desc.items():
                    if lang != 'type' and text and not existing.get(lang):
                        existing[lang] = text
    result['descriptions'] = list(descriptions_by_type.values())
    
    # Geopoints: union
    all_geopoints = []
    seen_coords = set()
    for poi in pois:
        for geo in poi.get('geopoints', []):
            coord_key = (round(geo.get('latitude', 0), 5), round(geo.get('longitude', 0), 5))
            if coord_key not in seen_coords:
                seen_coords.add(coord_key)
                all_geopoints.append(geo)
    result['geopoints'] = all_geopoints
    
    # Pictures: union par URL
    pictures_by_url = {}
    for poi in pois:
        for pic in poi.get('pictures', []):
            url = pic.get('url', '')
            if url and url not in pictures_by_url:
                pictures_by_url[url] = pic.copy()
            elif url:
                # Compléter les champs manquants
                existing = pictures_by_url[url]
                for key, value in pic.items():
                    if value and not existing.get(key):
                        existing[key] = value
    result['pictures'] = list(pictures_by_url.values())
    
    # Products: fusionner par nom + currency
    products_by_key = {}
    for poi in pois:
        for product in poi.get('products', []):
            key = f"{product.get('name', '')}_{product.get('currency', 'euro')}"
            if key not in products_by_key:
                products_by_key[key] = product.copy()
            else:
                existing = products_by_key[key]
                # Min/Max prix
                if product.get('min_price') is not None:
                    existing['min_price'] = min(existing.get('min_price', float('inf')), product['min_price'])
                if product.get('max_price') is not None:
                    existing['max_price'] = max(existing.get('max_price', 0), product['max_price'])
    result['products'] = list(products_by_key.values())
    
    # Schedules: garder tous
    all_schedules = []
    for poi in pois:
        all_schedules.extend(poi.get('schedules', []))
    result['schedules'] = all_schedules
    
    # Sources: union
    all_sources = []
    seen_refs = set()
    for poi in pois:
        for src in poi.get('sources', []):
            ref_key = (src.get('source', ''), src.get('reference', ''))
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                all_sources.append(src)
    result['sources'] = all_sources
    
    # Ratings: fusionner
    # Simplification: prendre les ratings du premier POI qui en a
    for poi in pois:
        if poi.get('ratings'):
            result['ratings'] = poi['ratings']
            break
    
    return result


def aggregate_pois(pois: List[Dict]) -> Dict:
    """
    Agrège une liste de POI redondants en un seul POI.
    """
    if not pois:
        return {}
    
    if len(pois) == 1:
        return pois[0].copy()
    
    # Agrégation par catégorie d'attributs
    result = {
        'id': None,
        **aggregate_simple_attributes(pois),
        **aggregate_complex_attributes(pois),
        **aggregate_list_attributes(pois),
        '_aggregation_info': {
            'source_count': len(pois),
            'sources': [get_source_reference(poi) for poi in pois],
            'aggregation_date': datetime.now().isoformat()
        }
    }
    
    return result


# ============================================================================
# FONCTIONS DE DÉTECTION
# ============================================================================

def load_poi_data(**context):
    """
    Charge les données POI validées.
    """
    print("📂 Chargement des données POI...")
    
    os.makedirs(DEDUP_DIR, exist_ok=True)
    
    # Chercher le fichier le plus récent
    files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith('pois_validated_')]
    
    if not files:
        # Créer des données de test si aucun fichier n'existe
        print("  ⚠️ Aucun fichier trouvé, génération de données de test...")
        
        from scripts.fake_data_generator import generate_poi_dataset, save_dataset
        pois = generate_poi_dataset(num_pois=100, duplicate_rate=0.20)
        
        # Sauvegarder directement dans processed
        output_file = f"{PROCESSED_DIR}/pois_validated_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pois, f, ensure_ascii=False, indent=2)
        
        latest_file = output_file
    else:
        latest_file = f"{PROCESSED_DIR}/{sorted(files)[-1]}"
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    print(f"  ✓ {len(pois)} POI chargés depuis {latest_file}")
    
    # Sauvegarder les infos
    result = {
        'file': latest_file,
        'count': len(pois),
        'timestamp': datetime.now().isoformat()
    }
    
    context['task_instance'].xcom_push(key='loaded_data', value=result)
    
    return result


def detect_by_common_references(**context):
    """
    Détecte les POI partageant des références communes entre sources.
    Ex: Datatourisme et Tourinsoft peuvent partager la même référence.
    """
    print("🔗 Détection par références communes...")
    
    ti = context['task_instance']
    loaded_data = ti.xcom_pull(key='loaded_data')
    
    with open(loaded_data['file'], 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    # Grouper par référence
    by_reference = defaultdict(list)
    
    for idx, poi in enumerate(pois):
        ref = get_source_reference(poi)
        if ref:
            # Utiliser uniquement la partie référence (sans la source)
            by_reference[ref[1]].append(idx)
    
    # Trouver les groupes avec plusieurs POI
    duplicate_groups = []
    matched_indices = set()
    
    for ref, indices in by_reference.items():
        if len(indices) > 1:
            # Vérifier que les sources sont différentes
            sources = set()
            for idx in indices:
                src_ref = get_source_reference(pois[idx])
                if src_ref:
                    sources.add(src_ref[0])
            
            if len(sources) > 1:  # Au moins 2 sources différentes
                duplicate_groups.append({
                    'method': 'common_reference',
                    'reference': ref,
                    'indices': indices,
                    'sources': list(sources)
                })
                matched_indices.update(indices)
    
    result = {
        'duplicate_groups': duplicate_groups,
        'matched_count': len(matched_indices),
        'group_count': len(duplicate_groups),
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"  ✓ {len(duplicate_groups)} groupes trouvés ({len(matched_indices)} POI)")
    
    ti.xcom_push(key='common_ref_results', value=result)
    
    return result


def detect_by_similarity(**context):
    """
    Détecte les POI similaires par comparaison nom + coordonnées + adresse.
    """
    print("🔍 Détection par mesures de similarité...")
    
    ti = context['task_instance']
    loaded_data = ti.xcom_pull(key='loaded_data')
    common_ref_results = ti.xcom_pull(key='common_ref_results') or {}

    with open(loaded_data['file'], 'r', encoding='utf-8') as f:
        pois = json.load(f)

    # Exclure les POI déjà matchés
    already_matched = set()
    for group in common_ref_results.get('duplicate_groups', []):
        already_matched.update(group['indices'])
    
    # Grouper par département pour réduire les comparaisons
    by_department = defaultdict(list)
    for idx, poi in enumerate(pois):
        if idx not in already_matched:
            dept = get_poi_department(poi)
            if dept:
                by_department[dept].append(idx)
    
    duplicate_groups = []
    matched_indices = set()
    comparisons_made = 0
    
    for dept, indices in by_department.items():
        print(f"  Traitement département {dept}: {len(indices)} POI...")
        
        # Produit cartésien au sein du département
        for i, idx1 in enumerate(indices):
            if idx1 in matched_indices:
                continue
            
            poi1 = pois[idx1]
            name1 = get_poi_name(poi1)
            coords1 = get_poi_coordinates(poi1)
            addr1 = get_poi_address(poi1)
            
            if not name1:
                continue
            
            group_indices = [idx1]
            
            for idx2 in indices[i+1:]:
                if idx2 in matched_indices:
                    continue
                
                poi2 = pois[idx2]
                name2 = get_poi_name(poi2)
                coords2 = get_poi_coordinates(poi2)
                addr2 = get_poi_address(poi2)
                
                if not name2:
                    continue
                
                comparisons_made += 1
                
                # Étape 1: Similarité des noms
                name_similarity = calculate_similarity(name1, name2)
                
                if name_similarity < NAME_SIMILARITY_THRESHOLD:
                    continue
                
                # Étape 2: Vérification des coordonnées
                is_duplicate = False
                
                if coords1 and coords2:
                    distance = calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
                    
                    if distance <= DIRECT_DISTANCE_THRESHOLD:
                        # Distance < 200m: validation directe
                        is_duplicate = True
                    elif distance <= EXTENDED_DISTANCE_THRESHOLD:
                        # Distance < 1km: vérifier l'adresse
                        if addr1 and addr2:
                            addr_similarity = calculate_similarity(addr1, addr2)
                            if addr_similarity >= ADDRESS_SIMILARITY_THRESHOLD:
                                is_duplicate = True
                else:
                    # Pas de coordonnées: vérifier l'adresse
                    if addr1 and addr2:
                        addr_similarity = calculate_similarity(addr1, addr2)
                        if addr_similarity >= ADDRESS_SIMILARITY_THRESHOLD:
                            is_duplicate = True
                
                if is_duplicate:
                    group_indices.append(idx2)
                    matched_indices.add(idx2)
            
            if len(group_indices) > 1:
                duplicate_groups.append({
                    'method': 'similarity',
                    'indices': group_indices,
                    'name_reference': name1,
                    'department': dept
                })
                matched_indices.update(group_indices)
    
    result = {
        'duplicate_groups': duplicate_groups,
        'matched_count': len(matched_indices),
        'group_count': len(duplicate_groups),
        'comparisons_made': comparisons_made,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n  ✓ {len(duplicate_groups)} groupes trouvés ({len(matched_indices)} POI)")
    print(f"  ✓ {comparisons_made} comparaisons effectuées")
    
    ti.xcom_push(key='similarity_results', value=result)
    
    return result


def aggregate_duplicates(**context):
    """
    Agrège tous les groupes de doublons détectés.
    """
    print("🔄 Agrégation des doublons...")
    
    ti = context['task_instance']
    loaded_data = ti.xcom_pull(key='loaded_data')
    common_ref_results = ti.xcom_pull(key='common_ref_results')
    similarity_results = ti.xcom_pull(key='similarity_results')
    
    with open(loaded_data['file'], 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    # Combiner tous les groupes de doublons
    all_groups = (
        common_ref_results.get('duplicate_groups', []) +
        similarity_results.get('duplicate_groups', [])
    )
    
    # Indices de tous les POI impliqués dans un groupe
    grouped_indices = set()
    for group in all_groups:
        grouped_indices.update(group['indices'])
    
    # Agrégation
    aggregated_pois = []
    aggregation_stats = {
        'total_groups': len(all_groups),
        'pois_aggregated': 0,
        'unique_pois_kept': 0,
        'by_method': {
            'common_reference': 0,
            'similarity': 0
        }
    }
    
    # Traiter les groupes de doublons
    for group in all_groups:
        group_pois = [pois[idx] for idx in group['indices']]
        aggregated = aggregate_pois(group_pois)
        aggregated_pois.append(aggregated)
        
        aggregation_stats['pois_aggregated'] += len(group['indices'])
        aggregation_stats['by_method'][group['method']] += 1
    
    # Ajouter les POI uniques (non impliqués dans un groupe)
    for idx, poi in enumerate(pois):
        if idx not in grouped_indices:
            aggregated_pois.append(poi)
            aggregation_stats['unique_pois_kept'] += 1
    
    # Assigner des IDs
    for idx, poi in enumerate(aggregated_pois):
        poi['id'] = idx + 1
    
    # Sauvegarder
    output_file = f"{DEDUP_DIR}/pois_deduplicated_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_pois, f, ensure_ascii=False, indent=2)
    
    # Sauvegarder les stats
    stats_file = f"{DEDUP_DIR}/dedup_stats_{datetime.now().strftime('%Y%m%d')}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            'input_count': len(pois),
            'output_count': len(aggregated_pois),
            'reduction_rate': 1 - (len(aggregated_pois) / len(pois)) if pois else 0,
            'aggregation_stats': aggregation_stats,
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    result = {
        'input_count': len(pois),
        'output_count': len(aggregated_pois),
        'reduction_rate': 1 - (len(aggregated_pois) / len(pois)) if pois else 0,
        'aggregation_stats': aggregation_stats,
        'output_file': output_file,
        'stats_file': stats_file,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n📊 Résultats de l'agrégation:")
    print(f"  - POI en entrée: {result['input_count']}")
    print(f"  - POI en sortie: {result['output_count']}")
    print(f"  - Taux de réduction: {result['reduction_rate']:.2%}")
    print(f"  - Groupes traités: {aggregation_stats['total_groups']}")
    print(f"    - Par référence commune: {aggregation_stats['by_method']['common_reference']}")
    print(f"    - Par similarité: {aggregation_stats['by_method']['similarity']}")
    
    ti.xcom_push(key='aggregation_results', value=result)
    
    return result


def generate_dedup_report(**context):
    """
    Génère un rapport de déduplication.
    """
    print("📄 Génération du rapport de déduplication...")
    
    ti = context['task_instance']
    aggregation_results = ti.xcom_pull(key='aggregation_results')
    common_ref_results = ti.xcom_pull(key='common_ref_results')
    similarity_results = ti.xcom_pull(key='similarity_results')
    
    report = f"""
# Rapport de Déduplication POI

## Résumé

- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **POI en entrée**: {aggregation_results['input_count']}
- **POI en sortie**: {aggregation_results['output_count']}
- **Taux de réduction**: {aggregation_results['reduction_rate']:.2%}

## Détection par références communes

- **Groupes détectés**: {common_ref_results['group_count']}
- **POI concernés**: {common_ref_results['matched_count']}

## Détection par similarité

- **Groupes détectés**: {similarity_results['group_count']}
- **POI concernés**: {similarity_results['matched_count']}
- **Comparaisons effectuées**: {similarity_results['comparisons_made']}

## Seuils utilisés

| Critère | Seuil |
|---------|-------|
| Similarité nom | {NAME_SIMILARITY_THRESHOLD:.0%} |
| Distance directe | {DIRECT_DISTANCE_THRESHOLD}m |
| Distance étendue | {EXTENDED_DISTANCE_THRESHOLD}m |
| Similarité adresse | {ADDRESS_SIMILARITY_THRESHOLD:.0%} |

## Fichiers générés

- Données dédupliquées: `{aggregation_results['output_file']}`
- Statistiques: `{aggregation_results['stats_file']}`

---
*Rapport généré automatiquement par le pipeline de déduplication POI*
    """
    
    # Sauvegarder le rapport
    report_file = f"{DEDUP_DIR}/dedup_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"  ✓ Rapport sauvegardé: {report_file}")
    print(report)
    
    return {'report_file': report_file, 'report': report}


# ============================================================================
# DÉFINITION DES TASKS
# ============================================================================

# Start
start = DummyOperator(task_id='start', dag=dag)

# Chargement des données
load_data = PythonOperator(
    task_id='load_data',
    python_callable=load_poi_data,
    provide_context=True,
    dag=dag
)

# TaskGroup: Détection des doublons
with TaskGroup('detection', dag=dag) as detection_group:
    
    detect_common_refs = PythonOperator(
        task_id='by_common_references',
        python_callable=detect_by_common_references,
        provide_context=True,
        dag=dag
    )
    
    detect_similarity = PythonOperator(
        task_id='by_similarity',
        python_callable=detect_by_similarity,
        provide_context=True,
        dag=dag
    )
    
    # Exécuter en parallèle puis synchroniser
    detect_common_refs
    detect_similarity

# Agrégation
aggregate = PythonOperator(
    task_id='aggregate_duplicates',
    python_callable=aggregate_duplicates,
    provide_context=True,
    dag=dag
)

# Rapport
report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_dedup_report,
    provide_context=True,
    dag=dag
)

# End
end = DummyOperator(task_id='end', dag=dag)


# ============================================================================
# DÉPENDANCES
# ============================================================================

start >> load_data >> detection_group >> aggregate >> report >> end


# ============================================================================
# DOCUMENTATION
# ============================================================================

load_data.doc_md = """
### Load Data
Charge les données POI validées depuis le pipeline ETL précédent.
"""

detect_common_refs.doc_md = """
### Detection by Common References
Détecte les POI partageant la même référence entre différentes sources.
Exemple: Un POI peut avoir la même référence dans Datatourisme et Tourinsoft.
"""

detect_similarity.doc_md = """
### Detection by Similarity
Détecte les POI similaires en utilisant:
1. Comparaison des noms (seuil: 85%)
2. Distance géographique (<200m ou <1km avec adresse)
3. Similarité des adresses (seuil: 80%)
"""

aggregate.doc_md = """
### Aggregate Duplicates
Agrège les POI redondants selon les règles:
- **closed**: Valeur maximale
- **display**: Valeur minimale
- **tags/types**: Union
- **addresses**: Fusion par ville
- **contacts**: Fusion par nom
- **pictures**: Union par URL
"""
