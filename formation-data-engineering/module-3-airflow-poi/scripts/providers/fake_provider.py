"""
Fake Data Provider - Génère des données POI fictives
Module 3 - Formation Data Engineering

Ce provider génère des données réalistes pour les tests et démonstrations.
"""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

from .base import BaseDataProvider, ProviderConfig, ExtractionResult

# Tentative d'import de Faker (optionnel)
try:
    from faker import Faker
    fake_fr = Faker('fr_FR')
    fake_en = Faker('en_US')
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    fake_fr = None
    fake_en = None


# ============================================================================
# CONSTANTES
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

REGIONS_FR = {
    'Ile-de-France': {'departments': ['Paris', 'Seine-et-Marne', 'Yvelines', 'Essonne'], 'lat_range': (48.5, 49.0), 'lon_range': (1.8, 3.0)},
    'Provence-Alpes-Côte d\'Azur': {'departments': ['Bouches-du-Rhône', 'Var', 'Alpes-Maritimes', 'Vaucluse'], 'lat_range': (43.0, 44.5), 'lon_range': (4.5, 7.5)},
    'Auvergne-Rhône-Alpes': {'departments': ['Rhône', 'Loire', 'Isère', 'Savoie', 'Haute-Savoie'], 'lat_range': (44.5, 46.5), 'lon_range': (3.5, 7.0)},
    'Nouvelle-Aquitaine': {'departments': ['Gironde', 'Dordogne', 'Charente-Maritime', 'Pyrénées-Atlantiques'], 'lat_range': (43.0, 46.5), 'lon_range': (-1.5, 1.5)},
    'Occitanie': {'departments': ['Haute-Garonne', 'Hérault', 'Gard', 'Pyrénées-Orientales'], 'lat_range': (42.5, 44.5), 'lon_range': (0.0, 4.5)},
    'Bretagne': {'departments': ['Finistère', 'Côtes-d\'Armor', 'Morbihan', 'Ille-et-Vilaine'], 'lat_range': (47.5, 48.8), 'lon_range': (-4.8, -1.0)},
    'Centre-Val de Loire': {'departments': ['Loiret', 'Indre-et-Loire', 'Loir-et-Cher', 'Cher'], 'lat_range': (46.5, 48.5), 'lon_range': (0.5, 3.0)},
}

NAME_TEMPLATES = {
    'sites': ['Château de {}', 'Musée {}', 'Parc {}', 'Église {}', 'Jardin {}', 'Abbaye de {}'],
    'activities': ['Centre {} Aventure', 'Espace {}', 'Club {}', 'Base nautique {}', 'Parcours {}'],
    'accommodations': ['Hôtel {}', 'Gîte {}', 'Camping {}', 'Auberge {}', 'Domaine {}'],
    'restaurants': ['Restaurant {}', 'Brasserie {}', 'Café {}', 'Bistrot {}', 'Auberge {}'],
    'events': ['Festival {}', 'Marché {}', 'Salon {}', 'Fête de {}', 'Nuit de {}']
}

CITY_NAMES = [
    'Bellevue', 'Montfort', 'Saint-Martin', 'Fontaine', 'Boisvert',
    'Rochelle', 'Clairmont', 'Vallon', 'Beaumont', 'Grandpré',
    'Villeneuve', 'Champagne', 'Laval', 'Bordeaux', 'Nantes'
]

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class FakeDataProvider(BaseDataProvider):
    """
    Provider de données fictives pour les tests et démonstrations.
    
    Génère des POI réalistes avec tous les attributs du format unifié.
    Supporte la génération de doublons pour tester la déduplication.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialise le FakeDataProvider.
        
        Args:
            config: Configuration avec notamment:
                - num_pois: Nombre de POI à générer
                - duplicate_rate: Taux de doublons (0.0 - 1.0)
                - regions: Filtrer par régions
                - types: Filtrer par types
        """
        super().__init__(config)
        self._generated_pois = []
    
    def extract(self, **kwargs) -> ExtractionResult:
        """
        Génère des données POI fictives.
        
        Args:
            num_pois: Nombre de POI (override config)
            duplicate_rate: Taux de doublons (override config)
            
        Returns:
            ExtractionResult avec les POI générés
        """
        start_time = time.time()
        
        num_pois = kwargs.get('num_pois', self.config.num_pois)
        duplicate_rate = kwargs.get('duplicate_rate', self.config.duplicate_rate)
        
        self.logger.info(f"Generating {num_pois} fake POIs with {duplicate_rate:.0%} duplicate rate...")
        
        pois = []
        errors = []
        warnings = []
        
        # Calculer le nombre de POI uniques vs doublons
        num_duplicates = int(num_pois * duplicate_rate)
        num_unique = num_pois - num_duplicates
        
        # Générer les POI uniques
        for i in range(num_unique):
            try:
                poi = self._generate_poi()
                pois.append(poi)
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        
        # Générer les doublons
        if num_duplicates > 0 and len(pois) > 0:
            for i in range(num_duplicates):
                try:
                    # Sélectionner un POI de référence
                    reference_poi = random.choice(pois[:num_unique])
                    duplicate = self._generate_duplicate(reference_poi)
                    pois.append(duplicate)
                except Exception as e:
                    errors.append({'index': num_unique + i, 'error': str(e), 'type': 'duplicate'})
        
        # Mélanger
        random.shuffle(pois)
        
        # Stocker pour référence
        self._generated_pois = pois
        
        duration = time.time() - start_time
        
        if len(errors) > 0:
            warnings.append(f"{len(errors)} errors during generation")
        
        self.logger.info(f"Generated {len(pois)} POIs in {duration:.2f}s ({len(errors)} errors)")
        
        return ExtractionResult(
            source=self.config.name,
            pois=pois,
            count=len(pois),
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            errors=errors,
            warnings=warnings
        )
    
    def normalize(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Les données fake sont déjà au format normalisé.
        
        Args:
            raw_data: Données générées
            
        Returns:
            Même données (déjà normalisées)
        """
        # Les fake data sont générées au format final
        return raw_data
    
    def _generate_poi(self, poi_type: str = None, region: str = None) -> Dict[str, Any]:
        """
        Génère un POI fictif complet.
        
        Args:
            poi_type: Type de POI (optionnel, aléatoire si non spécifié)
            region: Région (optionnel, aléatoire si non spécifié)
            
        Returns:
            POI au format unifié
        """
        # Sélectionner type et région
        if poi_type is None:
            if self.config.types:
                poi_type = random.choice(self.config.types)
            else:
                poi_type = random.choice(POI_TYPES)
        
        if region is None:
            if self.config.regions:
                region = random.choice(self.config.regions)
            else:
                region = random.choice(list(REGIONS_FR.keys()))
        
        # Générer le nom
        poi_name = self._generate_name(poi_type)
        
        # Construire le POI
        poi = {
            'id': None,
            'closed': random.random() < 0.05,
            'display': random.random() > 0.02,
            'tags': self._generate_tags(poi_type),
            'types': [poi_type] + (random.sample([t for t in POI_TYPES if t != poi_type], k=1) if random.random() > 0.8 else []),
            
            'age_limit': self._generate_age_limit() if random.random() > 0.4 else None,
            'duration': self._generate_duration() if random.random() > 0.5 else None,
            'group_size_limit': self._generate_group_limit() if random.random() > 0.6 else None,
            
            'poi_name': self._generate_multilingual_text(poi_name),
            'ratings': self._generate_ratings() if random.random() > 0.3 else None,
            
            'addresses': [self._generate_address(region)],
            'contacts': [self._generate_contact() for _ in range(random.randint(1, 2))],
            'descriptions': [self._generate_description(poi_name, poi_type)],
            'geopoints': [self._generate_geopoint(region)],
            'pictures': [self._generate_picture() for _ in range(random.randint(1, 4))],
            'products': [self._generate_product() for _ in range(random.randint(0, 3))],
            'schedules': [self._generate_schedule() for _ in range(random.randint(1, 2))],
            'sources': [self._generate_source()]
        }
        
        return poi
    
    def _generate_duplicate(self, reference: Dict) -> Dict:
        """
        Génère un doublon d'un POI existant (source différente, légères variations).
        
        Args:
            reference: POI de référence
            
        Returns:
            POI doublon
        """
        # Copier et modifier
        duplicate = {
            'id': None,
            'closed': reference.get('closed', False),
            'display': reference.get('display', True),
            'tags': reference.get('tags', [])[:],
            'types': reference.get('types', [])[:],
            
            'age_limit': reference.get('age_limit'),
            'duration': reference.get('duration'),
            'group_size_limit': reference.get('group_size_limit'),
            
            # Même nom avec possible variation
            'poi_name': reference.get('poi_name', {}).copy(),
            'ratings': self._generate_ratings() if random.random() > 0.5 else None,
            
            # Copier l'adresse avec légère variation
            'addresses': [],
            'contacts': [self._generate_contact()],  # Contact différent
            'descriptions': reference.get('descriptions', [])[:],
            
            # Coordonnées avec légère variation
            'geopoints': [],
            'pictures': [self._generate_picture() for _ in range(random.randint(1, 2))],
            'products': reference.get('products', [])[:],
            'schedules': reference.get('schedules', [])[:],
            
            # Source différente
            'sources': [self._generate_source(exclude_source=reference.get('sources', [{}])[0].get('source'))]
        }
        
        # Copier l'adresse avec variation
        if reference.get('addresses'):
            addr = reference['addresses'][0].copy()
            # Possible variation de l'adresse
            if random.random() > 0.7:
                addr['street_addresses'] = [self._generate_street()]
            duplicate['addresses'] = [addr]
        
        # Copier les coordonnées avec légère variation
        if reference.get('geopoints'):
            geo = reference['geopoints'][0].copy()
            geo['latitude'] += random.uniform(-0.001, 0.001)
            geo['longitude'] += random.uniform(-0.001, 0.001)
            duplicate['geopoints'] = [geo]
        
        return duplicate
    
    # ========================================================================
    # Générateurs d'attributs
    # ========================================================================
    
    def _generate_name(self, poi_type: str) -> str:
        """Génère un nom de POI."""
        templates = NAME_TEMPLATES.get(poi_type, NAME_TEMPLATES['sites'])
        template = random.choice(templates)
        
        if FAKER_AVAILABLE:
            city = fake_fr.city()
        else:
            city = random.choice(CITY_NAMES)
        
        return template.format(city)
    
    def _generate_multilingual_text(self, text_fr: str) -> Dict[str, str]:
        """Génère un texte multilingue."""
        return {
            'fr': text_fr,
            'en': f"[EN] {text_fr}",
            'es': f"[ES] {text_fr}",
            'de': f"[DE] {text_fr}"
        }
    
    def _generate_tags(self, poi_type: str) -> List[str]:
        """Génère des tags pour un type de POI."""
        available_tags = POI_TAGS.get(poi_type, POI_TAGS['sites'])
        return random.sample(available_tags, k=min(random.randint(1, 3), len(available_tags)))
    
    def _generate_address(self, region: str) -> Dict[str, Any]:
        """Génère une adresse."""
        region_data = REGIONS_FR.get(region, list(REGIONS_FR.values())[0])
        
        if FAKER_AVAILABLE:
            city = fake_fr.city()
            street = fake_fr.street_address()
        else:
            city = random.choice(CITY_NAMES)
            street = f"{random.randint(1, 100)} rue de la {random.choice(['Paix', 'Liberté', 'République', 'Victoire'])}"
        
        return {
            'insee_code': random.randint(10000, 99999),
            'city': city,
            'zip_code': str(random.randint(10000, 99999)),
            'department': random.choice(region_data['departments']),
            'region': region,
            'country': 'France',
            'address_complement': random.choice(['', 'Bis', 'Ter']) if random.random() > 0.8 else None,
            'street_addresses': [street]
        }
    
    def _generate_street(self) -> str:
        """Génère une adresse de rue."""
        if FAKER_AVAILABLE:
            return fake_fr.street_address()
        return f"{random.randint(1, 100)} rue de la {random.choice(['Paix', 'Liberté', 'République'])}"
    
    def _generate_geopoint(self, region: str) -> Dict[str, float]:
        """Génère des coordonnées GPS."""
        region_data = REGIONS_FR.get(region, list(REGIONS_FR.values())[0])
        
        return {
            'latitude': round(random.uniform(*region_data['lat_range']), 6),
            'longitude': round(random.uniform(*region_data['lon_range']), 6),
            'altitude': random.randint(0, 1500) if random.random() > 0.5 else None
        }
    
    def _generate_contact(self) -> Dict[str, Any]:
        """Génère un contact."""
        if FAKER_AVAILABLE:
            first_name = fake_fr.first_name()
            last_name = fake_fr.last_name()
            email = fake_fr.email()
            phone = fake_fr.phone_number()
            website = fake_fr.url()
        else:
            first_name = random.choice(['Jean', 'Marie', 'Pierre', 'Sophie', 'Thomas'])
            last_name = random.choice(['Dupont', 'Martin', 'Bernard', 'Petit', 'Robert'])
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"0{random.randint(1, 9)}{random.randint(10000000, 99999999)}"
            website = f"https://www.{last_name.lower()}.fr"
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'roles': random.sample(['Directeur', 'Accueil', 'Communication', 'Guide'], k=random.randint(1, 2)),
            'phones': [phone],
            'emails': [email],
            'websites': [website] if random.random() > 0.5 else []
        }
    
    def _generate_description(self, poi_name: str, poi_type: str) -> Dict[str, Any]:
        """Génère une description."""
        templates = {
            'sites': f"{poi_name} est un site remarquable offrant une expérience unique.",
            'activities': f"{poi_name} propose des activités variées pour tous les âges.",
            'accommodations': f"{poi_name} vous offre un séjour confortable.",
            'restaurants': f"{poi_name} vous invite à découvrir sa cuisine.",
            'events': f"{poi_name} est un événement à ne pas manquer."
        }
        
        text = templates.get(poi_type, templates['sites'])
        
        return {
            'type': random.choice(['general', 'short', 'detailed']),
            **self._generate_multilingual_text(text)
        }
    
    def _generate_picture(self) -> Dict[str, Any]:
        """Génère les métadonnées d'une image."""
        width = random.choice([1920, 1280, 1024])
        height = random.choice([1080, 720, 768])
        
        return {
            'height': height,
            'width': width,
            'main_picture': random.random() > 0.7,
            'url': f"https://example.com/images/{uuid.uuid4().hex}.jpg",
            'file_type': random.choice(['jpg', 'png', 'webp']),
            'capture_date': (datetime.now() - timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d'),
            'copyrights': [f"© Example {random.randint(2020, 2024)}"] if random.random() > 0.5 else [],
            'title': self._generate_multilingual_text(f"Image {random.randint(1, 100)}"),
            'caption': None
        }
    
    def _generate_product(self) -> Dict[str, Any]:
        """Génère un produit/tarif."""
        min_price = round(random.uniform(0, 30), 2)
        
        return {
            'min_price': min_price,
            'max_price': round(min_price + random.uniform(5, 50), 2),
            'name': random.choice(['Entrée adulte', 'Entrée enfant', 'Pass famille', 'Visite guidée']),
            'currency': 'euro',
            'price_description': 'Tarif standard',
            'validity_period': {
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            }
        }
    
    def _generate_schedule(self) -> Dict[str, Any]:
        """Génère un horaire d'ouverture."""
        opening = f"{random.randint(8, 10):02d}:00"
        closing = f"{random.randint(17, 20):02d}:00"
        
        return {
            'opening_duration': random.randint(480, 720),
            'opening_time': opening,
            'weekdays': random.sample(WEEKDAYS, k=random.randint(5, 7)),
            'validity_period': {
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            },
            'description': self._generate_multilingual_text(f"Ouvert de {opening} à {closing}")
        }
    
    def _generate_ratings(self) -> Dict[str, Any]:
        """Génère des notes."""
        return {
            'distributions': [{
                'type': 'general',
                'values': [
                    {'nb_ratings': random.randint(10, 100), 'value': v}
                    for v in [0, 0.25, 0.5, 0.75, 1]
                ]
            }],
            'types': [{
                'source': random.choice(['tripadvisor', 'google']),
                'values': [
                    {'mean_value': round(random.uniform(0.5, 1), 2), 'type': t}
                    for t in random.sample(['ambiance', 'price', 'service'], k=2)
                ]
            }]
        }
    
    def _generate_age_limit(self) -> Dict[str, int]:
        """Génère une limite d'âge."""
        return {
            'min_age': random.choice([0, 3, 6, 12]),
            'max_age': random.choice([70, 80, 99])
        }
    
    def _generate_duration(self) -> Dict[str, int]:
        """Génère une durée."""
        avg = random.randint(60, 240)
        return {
            'average_duration': avg,
            'min_duration': avg - 30,
            'max_duration': avg + 60
        }
    
    def _generate_group_limit(self) -> Dict[str, int]:
        """Génère une limite de groupe."""
        return {
            'min_group_size': random.randint(1, 5),
            'max_group_size': random.randint(20, 200),
            'max_wheelchairs': random.randint(1, 20)
        }
    
    def _generate_source(self, exclude_source: str = None) -> Dict[str, Any]:
        """Génère une référence source."""
        sources = ['Datatourisme', 'Apidae', 'TripAdvisor', 'Tourinsoft']
        
        if exclude_source:
            sources = [s for s in sources if s != exclude_source]
        
        source = random.choice(sources)
        prefixes = {'Datatourisme': 'DT', 'Apidae': 'AP', 'TripAdvisor': 'TA', 'Tourinsoft': 'TS'}
        
        return {
            'source': source,
            'reference': f"{prefixes.get(source, 'XX')}{random.randint(10000, 99999)}",
            'last_update': (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du provider."""
        return {
            **super().health_check(),
            'faker_available': FAKER_AVAILABLE,
            'generated_count': len(self._generated_pois)
        }
