"""
Générateur de données fictives pour les POI (Points Of Interest)
Module 3 - Formation Data Engineering

Ce module génère des données réalistes simulant plusieurs sources:
- Datatourisme
- Apidae
- TripAdvisor
- Tourinsoft
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker
import os

# Initialisation de Faker pour plusieurs langues
fake_fr = Faker('fr_FR')
fake_en = Faker('en_US')
fake_es = Faker('es_ES')
fake_de = Faker('de_DE')

# ============================================================================
# CONSTANTES ET CONFIGURATIONS
# ============================================================================

POI_TYPES = ['sites', 'activities', 'accommodations', 'restaurants', 'events']

POI_TAGS = {
    'sites': [
        'sites_monument_castle', 'sites_monument_church', 'sites_monument_museum',
        'sites_nature_park', 'sites_nature_garden', 'sites_nature_lake',
        'sites_historic_ruins', 'sites_historic_battlefield'
    ],
    'activities': [
        'activities_outdoor_hiking', 'activities_outdoor_cycling', 'activities_outdoor_climbing',
        'activities_aquatic_swimming', 'activities_aquatic_kayak', 'activities_aquatic_wellness_spa',
        'activities_sites_recreationpark_amusementpark', 'activities_sites_recreationpark_themepark',
        'activities_cultural_workshop', 'activities_cultural_tour'
    ],
    'accommodations': [
        'accommodations_hotel_luxury', 'accommodations_hotel_budget',
        'accommodations_camping', 'accommodations_guesthouse',
        'accommodations_rental_apartment', 'accommodations_rental_house'
    ],
    'restaurants': [
        'restaurants_gastronomy', 'restaurants_traditional', 'restaurants_fastfood',
        'restaurants_cafe', 'restaurants_bar', 'restaurants_winery'
    ],
    'events': [
        'events_festival_music', 'events_festival_food', 'events_market',
        'events_exhibition', 'events_sport_competition', 'events_cultural'
    ]
}

SOURCES = ['Datatourisme', 'Apidae', 'TripAdvisor', 'Tourinsoft', 'GooglePlaces']

REGIONS_FR = {
    'Ile-de-France': {'departments': ['Paris', 'Seine-et-Marne', 'Yvelines', 'Essonne', 'Hauts-de-Seine'], 'lat_range': (48.5, 49.0), 'lon_range': (1.8, 3.0)},
    'Provence-Alpes-Côte d\'Azur': {'departments': ['Bouches-du-Rhône', 'Var', 'Alpes-Maritimes', 'Vaucluse'], 'lat_range': (43.0, 44.5), 'lon_range': (4.5, 7.5)},
    'Auvergne-Rhône-Alpes': {'departments': ['Rhône', 'Loire', 'Isère', 'Savoie', 'Haute-Savoie'], 'lat_range': (44.5, 46.5), 'lon_range': (3.5, 7.0)},
    'Nouvelle-Aquitaine': {'departments': ['Gironde', 'Dordogne', 'Charente-Maritime', 'Pyrénées-Atlantiques'], 'lat_range': (43.0, 46.5), 'lon_range': (-1.5, 1.5)},
    'Occitanie': {'departments': ['Haute-Garonne', 'Hérault', 'Gard', 'Pyrénées-Orientales'], 'lat_range': (42.5, 44.5), 'lon_range': (0.0, 4.5)},
    'Bretagne': {'departments': ['Finistère', 'Côtes-d\'Armor', 'Morbihan', 'Ille-et-Vilaine'], 'lat_range': (47.5, 48.8), 'lon_range': (-4.8, -1.0)},
    'Centre-Val de Loire': {'departments': ['Loiret', 'Indre-et-Loire', 'Loir-et-Cher', 'Cher'], 'lat_range': (46.5, 48.5), 'lon_range': (0.5, 3.0)},
}

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# ============================================================================
# FONCTIONS DE GÉNÉRATION
# ============================================================================

def generate_multilingual_text(base_text: str, languages: List[str] = None) -> Dict[str, str]:
    """Génère un texte multilingue à partir d'un texte de base"""
    if languages is None:
        languages = ['fr', 'en', 'es', 'de']
    
    translations = {'fr': base_text}
    
    # Simulation de traductions (en production, utiliser une API de traduction)
    prefixes = {
        'en': '[EN] ',
        'es': '[ES] ',
        'de': '[DE] ',
        'it': '[IT] ',
        'nl': '[NL] ',
    }
    
    for lang in languages:
        if lang != 'fr':
            translations[lang] = f"{prefixes.get(lang, '')}{base_text}"
    
    return translations


def generate_address(region: str = None) -> Dict[str, Any]:
    """Génère une adresse réaliste"""
    if region is None:
        region = random.choice(list(REGIONS_FR.keys()))
    
    region_data = REGIONS_FR[region]
    department = random.choice(region_data['departments'])
    
    return {
        'insee_code': random.randint(10000, 99999),
        'city': fake_fr.city(),
        'zip_code': str(random.randint(10000, 99999)),
        'department': department,
        'region': region,
        'country': 'France',
        'address_complement': random.choice(['', 'Bis', 'Ter', 'A', 'B']) if random.random() > 0.7 else None,
        'street_addresses': [fake_fr.street_address()]
    }


def generate_geopoint(region: str = None) -> Dict[str, float]:
    """Génère des coordonnées géographiques réalistes"""
    if region is None:
        region = random.choice(list(REGIONS_FR.keys()))
    
    region_data = REGIONS_FR[region]
    
    return {
        'latitude': round(random.uniform(*region_data['lat_range']), 6),
        'longitude': round(random.uniform(*region_data['lon_range']), 6),
        'altitude': random.randint(0, 2000) if random.random() > 0.5 else None
    }


def generate_contact() -> Dict[str, Any]:
    """Génère un contact fictif"""
    return {
        'first_name': fake_fr.first_name(),
        'last_name': fake_fr.last_name(),
        'roles': random.sample([
            'Directeur', 'Responsable communication', 'Accueil', 
            'Responsable technique', 'Guide', 'Animateur'
        ], k=random.randint(1, 2)),
        'phones': [fake_fr.phone_number() for _ in range(random.randint(1, 2))],
        'emails': [fake_fr.email()],
        'websites': [fake_fr.url()] if random.random() > 0.5 else []
    }


def generate_picture() -> Dict[str, Any]:
    """Génère les métadonnées d'une image"""
    width = random.choice([1920, 1280, 1024, 800])
    height = random.choice([1080, 720, 768, 600])
    
    capture_date = fake_fr.date_between(start_date='-2y', end_date='today')
    
    return {
        'height': height,
        'width': width,
        'main_picture': random.random() > 0.7,
        'url': f"https://example.com/images/{uuid.uuid4().hex}.jpg",
        'file_type': random.choice(['jpg', 'png', 'webp']),
        'capture_date': capture_date.isoformat(),
        'copyrights': [f"© {fake_fr.company()}"] if random.random() > 0.3 else [],
        'title': generate_multilingual_text(fake_fr.sentence(nb_words=4)),
        'caption': generate_multilingual_text(fake_fr.sentence(nb_words=8)) if random.random() > 0.5 else None,
        'validity_period': {
            'start_date': capture_date.isoformat(),
            'end_date': (capture_date + timedelta(days=365)).isoformat()
        } if random.random() > 0.5 else None
    }


def generate_schedule() -> Dict[str, Any]:
    """Génère un horaire d'ouverture"""
    opening_time = f"{random.randint(6, 10):02d}:{random.choice(['00', '30'])}"
    closing_time = f"{random.randint(17, 22):02d}:{random.choice(['00', '30'])}"
    
    # Calculer la durée d'ouverture en minutes
    open_h, open_m = map(int, opening_time.split(':'))
    close_h, close_m = map(int, closing_time.split(':'))
    duration = (close_h * 60 + close_m) - (open_h * 60 + open_m)
    
    start_date = fake_fr.date_between(start_date='-1y', end_date='today')
    
    return {
        'opening_duration': duration,
        'opening_time': opening_time,
        'weekdays': random.sample(WEEKDAYS, k=random.randint(3, 7)),
        'validity_period': {
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=random.randint(180, 365))).isoformat()
        },
        'description': generate_multilingual_text(f"Horaires d'ouverture: {opening_time} - {closing_time}")
    }


def generate_product() -> Dict[str, Any]:
    """Génère un produit/tarif"""
    min_price = round(random.uniform(0, 50), 2)
    max_price = round(min_price + random.uniform(5, 100), 2)
    
    start_date = fake_fr.date_between(start_date='today', end_date='+6m')
    
    return {
        'min_price': min_price,
        'max_price': max_price,
        'name': random.choice([
            'Entrée adulte', 'Entrée enfant', 'Pass famille', 
            'Visite guidée', 'Location équipement', 'Menu dégustation',
            'Forfait journée', 'Abonnement annuel'
        ]),
        'currency': 'euro',
        'price_description': fake_fr.sentence(nb_words=10),
        'validity_period': {
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=365)).isoformat()
        }
    }


def generate_ratings() -> Dict[str, Any]:
    """Génère des notes et évaluations"""
    return {
        'distributions': [
            {
                'type': 'general',
                'values': [
                    {'nb_ratings': random.randint(10, 200), 'value': 0},
                    {'nb_ratings': random.randint(20, 300), 'value': 0.25},
                    {'nb_ratings': random.randint(50, 500), 'value': 0.5},
                    {'nb_ratings': random.randint(100, 800), 'value': 0.75},
                    {'nb_ratings': random.randint(200, 1000), 'value': 1}
                ]
            }
        ],
        'types': [
            {
                'source': random.choice(['tripadvisor', 'google', 'booking']),
                'values': [
                    {'mean_value': round(random.uniform(0.5, 1), 3), 'type': rating_type}
                    for rating_type in random.sample(['ambiance', 'price', 'service', 'location', 'cleanliness'], k=random.randint(2, 4))
                ]
            }
        ]
    }


def generate_description(poi_name: str, poi_type: str) -> Dict[str, Any]:
    """Génère une description multilingue"""
    descriptions_templates = {
        'sites': [
            f"{poi_name} est un site remarquable offrant une expérience unique aux visiteurs.",
            f"Découvrez {poi_name}, un lieu chargé d'histoire et de culture.",
            f"{poi_name} vous accueille pour une visite mémorable."
        ],
        'activities': [
            f"{poi_name} propose des activités variées pour tous les âges.",
            f"Vivez des moments inoubliables avec {poi_name}.",
            f"Aventure et découverte vous attendent à {poi_name}."
        ],
        'accommodations': [
            f"{poi_name} vous offre un séjour confortable et reposant.",
            f"Bienvenue à {poi_name}, votre havre de paix.",
            f"Profitez d'un accueil chaleureux à {poi_name}."
        ],
        'restaurants': [
            f"{poi_name} vous invite à découvrir sa cuisine savoureuse.",
            f"Gastronomie et convivialité vous attendent à {poi_name}.",
            f"Savourez les délices de {poi_name}."
        ],
        'events': [
            f"{poi_name} est un événement à ne pas manquer.",
            f"Participez à {poi_name}, une expérience unique.",
            f"Rejoignez-nous pour {poi_name}."
        ]
    }
    
    base_description = random.choice(descriptions_templates.get(poi_type, descriptions_templates['sites']))
    
    return {
        'type': random.choice(['general', 'short', 'detailed']),
        **generate_multilingual_text(base_description)
    }


def generate_source_reference(source: str) -> Dict[str, Any]:
    """Génère une référence source"""
    prefixes = {
        'Datatourisme': 'DT',
        'Apidae': 'AP',
        'TripAdvisor': 'TA',
        'Tourinsoft': 'TS',
        'GooglePlaces': 'GP'
    }
    
    return {
        'reference': f"{prefixes.get(source, 'XX')}{random.randint(10000, 99999)}",
        'source': source,
        'last_update': fake_fr.date_between(start_date='-6m', end_date='today').isoformat()
    }


# ============================================================================
# GÉNÉRATEUR DE POI COMPLET
# ============================================================================

def generate_poi(
    poi_type: str = None,
    source: str = None,
    region: str = None,
    force_duplicate: bool = False,
    duplicate_of: Dict = None
) -> Dict[str, Any]:
    """
    Génère un POI complet avec toutes ses caractéristiques.
    
    Args:
        poi_type: Type de POI (sites, activities, etc.)
        source: Source de données (Datatourisme, Apidae, etc.)
        region: Région française
        force_duplicate: Si True, génère un POI similaire à duplicate_of
        duplicate_of: POI de référence pour créer un doublon
    
    Returns:
        Dict contenant toutes les données du POI
    """
    if poi_type is None:
        poi_type = random.choice(POI_TYPES)
    
    if source is None:
        source = random.choice(SOURCES)
    
    if region is None:
        region = random.choice(list(REGIONS_FR.keys()))
    
    # Génération du nom
    name_templates = {
        'sites': ['Château de {}', 'Musée {}', 'Parc {}', 'Église {}', 'Jardin {}'],
        'activities': ['Centre {} Aventure', 'Espace {}', 'Club {}', 'Base nautique {}'],
        'accommodations': ['Hôtel {}', 'Gîte {}', 'Camping {}', 'Auberge {}'],
        'restaurants': ['Restaurant {}', 'Brasserie {}', 'Café {}', 'Bistrot {}'],
        'events': ['Festival {}', 'Marché {}', 'Salon {}', 'Fête de {}']
    }
    
    if force_duplicate and duplicate_of:
        # Créer un doublon avec variations mineures
        poi_name = duplicate_of['poi_name']['fr']
        address = duplicate_of['addresses'][0].copy()
        geopoint = duplicate_of['geopoints'][0].copy()
        # Légère variation des coordonnées
        geopoint['latitude'] += random.uniform(-0.001, 0.001)
        geopoint['longitude'] += random.uniform(-0.001, 0.001)
    else:
        template = random.choice(name_templates.get(poi_type, name_templates['sites']))
        poi_name = template.format(fake_fr.city())
        address = generate_address(region)
        geopoint = generate_geopoint(region)
    
    # Construction du POI
    poi = {
        'id': None,  # Sera assigné lors de l'intégration en BDD
        'closed': random.random() < 0.05,  # 5% de POI fermés
        'display': random.random() > 0.02,  # 98% affichables
        'tags': random.sample(POI_TAGS.get(poi_type, POI_TAGS['sites']), k=random.randint(1, 4)),
        'types': [poi_type] + (random.sample([t for t in POI_TYPES if t != poi_type], k=1) if random.random() > 0.7 else []),
        
        'age_limit': {
            'min_age': random.choice([0, 3, 6, 12, 18]),
            'max_age': random.choice([70, 80, 99, None])
        } if random.random() > 0.3 else None,
        
        'duration': {
            'average_duration': random.randint(30, 480),
            'min_duration': random.randint(15, 60),
            'max_duration': random.randint(120, 1440)
        } if random.random() > 0.4 else None,
        
        'group_size_limit': {
            'min_group_size': random.randint(1, 5),
            'max_group_size': random.randint(20, 500),
            'max_wheelchairs': random.randint(1, 50)
        } if random.random() > 0.5 else None,
        
        'poi_name': generate_multilingual_text(poi_name),
        'ratings': generate_ratings() if random.random() > 0.3 else None,
        
        'addresses': [address],
        'contacts': [generate_contact() for _ in range(random.randint(1, 3))],
        'descriptions': [generate_description(poi_name, poi_type)],
        'geopoints': [geopoint],
        'pictures': [generate_picture() for _ in range(random.randint(1, 5))],
        'products': [generate_product() for _ in range(random.randint(0, 3))],
        'schedules': [generate_schedule() for _ in range(random.randint(1, 3))],
        'sources': [generate_source_reference(source)]
    }
    
    return poi


def generate_poi_dataset(
    num_pois: int = 100,
    duplicate_rate: float = 0.15,
    sources_distribution: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Génère un dataset complet de POI avec des doublons simulés.
    
    Args:
        num_pois: Nombre total de POI à générer
        duplicate_rate: Taux de doublons (0.15 = 15%)
        sources_distribution: Distribution des sources (ex: {'Datatourisme': 0.4, 'Apidae': 0.3})
    
    Returns:
        Liste de POI
    """
    if sources_distribution is None:
        sources_distribution = {
            'Datatourisme': 0.35,
            'Apidae': 0.25,
            'TripAdvisor': 0.20,
            'Tourinsoft': 0.15,
            'GooglePlaces': 0.05
        }
    
    pois = []
    duplicates_to_create = int(num_pois * duplicate_rate)
    unique_pois = num_pois - duplicates_to_create
    
    print(f"Génération de {unique_pois} POI uniques et {duplicates_to_create} doublons...")
    
    # Générer les POI uniques
    for i in range(unique_pois):
        # Sélectionner la source selon la distribution
        rand = random.random()
        cumulative = 0
        selected_source = list(sources_distribution.keys())[0]
        
        for source, prob in sources_distribution.items():
            cumulative += prob
            if rand <= cumulative:
                selected_source = source
                break
        
        poi = generate_poi(source=selected_source)
        pois.append(poi)
        
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{unique_pois} POI uniques générés...")
    
    # Générer les doublons
    print(f"Génération de {duplicates_to_create} doublons...")
    for i in range(duplicates_to_create):
        # Sélectionner un POI existant comme référence
        reference_poi = random.choice(pois[:unique_pois])
        
        # Créer un doublon avec une source différente
        available_sources = [s for s in SOURCES if s != reference_poi['sources'][0]['source']]
        duplicate_source = random.choice(available_sources)
        
        duplicate_poi = generate_poi(
            poi_type=reference_poi['types'][0],
            source=duplicate_source,
            force_duplicate=True,
            duplicate_of=reference_poi
        )
        pois.append(duplicate_poi)
    
    # Mélanger pour plus de réalisme
    random.shuffle(pois)
    
    print(f"Dataset généré: {len(pois)} POI au total")
    
    return pois


def save_dataset(pois: List[Dict], output_dir: str = '/data', split_by_source: bool = True):
    """
    Sauvegarde le dataset en fichiers JSON.
    
    Args:
        pois: Liste des POI
        output_dir: Répertoire de sortie
        split_by_source: Si True, crée un fichier par source
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if split_by_source:
        # Grouper par source
        by_source = {}
        for poi in pois:
            source = poi['sources'][0]['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(poi)
        
        # Sauvegarder chaque source
        for source, source_pois in by_source.items():
            filename = f"{output_dir}/pois_{source.lower()}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(source_pois, f, ensure_ascii=False, indent=2)
            print(f"Sauvegardé: {filename} ({len(source_pois)} POI)")
    
    # Sauvegarder le dataset complet
    filename = f"{output_dir}/pois_all_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)
    print(f"Sauvegardé: {filename} ({len(pois)} POI)")
    
    return filename


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Générateur de données POI fictives')
    parser.add_argument('--num-pois', type=int, default=100, help='Nombre de POI à générer')
    parser.add_argument('--duplicate-rate', type=float, default=0.15, help='Taux de doublons')
    parser.add_argument('--output-dir', type=str, default='/data/raw', help='Répertoire de sortie')
    parser.add_argument('--split-by-source', action='store_true', help='Séparer par source')
    
    args = parser.parse_args()
    
    # Générer le dataset
    pois = generate_poi_dataset(
        num_pois=args.num_pois,
        duplicate_rate=args.duplicate_rate
    )
    
    # Sauvegarder
    save_dataset(pois, args.output_dir, args.split_by_source)
    
    # Statistiques
    print("\n📊 Statistiques du dataset:")
    print(f"  - Total POI: {len(pois)}")
    
    types_count = {}
    sources_count = {}
    regions_count = {}
    
    for poi in pois:
        for t in poi['types']:
            types_count[t] = types_count.get(t, 0) + 1
        
        source = poi['sources'][0]['source']
        sources_count[source] = sources_count.get(source, 0) + 1
        
        if poi['addresses']:
            region = poi['addresses'][0]['region']
            regions_count[region] = regions_count.get(region, 0) + 1
    
    print(f"\n  Par type:")
    for t, count in sorted(types_count.items(), key=lambda x: -x[1]):
        print(f"    - {t}: {count}")
    
    print(f"\n  Par source:")
    for s, count in sorted(sources_count.items(), key=lambda x: -x[1]):
        print(f"    - {s}: {count}")
    
    print(f"\n  Par région:")
    for r, count in sorted(regions_count.items(), key=lambda x: -x[1]):
        print(f"    - {r}: {count}")
