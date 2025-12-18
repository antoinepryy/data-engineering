"""
Apidae API Provider
Module 3 - Formation Data Engineering

Provider pour l'API Apidae (https://api.apidae-tourisme.com)
Documentation: https://dev.apidae-tourisme.com/

Note: Ce provider est un stub prêt à être complété avec les vraies appels API.
"""

import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .base import BaseDataProvider, ProviderConfig, ExtractionResult

logger = logging.getLogger(__name__)


class ApidaeProvider(BaseDataProvider):
    """
    Provider pour l'API Apidae.
    
    Apidae (anciennement SITRA) est la base de données touristique de référence
    pour les régions Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, et autres.
    
    API Documentation: https://dev.apidae-tourisme.com/
    
    Pour obtenir un accès:
    1. Créer un compte sur https://base.apidae-tourisme.com
    2. Créer un projet API
    3. Récupérer les clés (api_key et projet_id)
    
    Configuration requise:
        - api_url: URL de base de l'API
        - api_key: Clé API Apidae
        - api_secret: Secret API (projet_id)
    """
    
    BASE_URL = "https://api.apidae-tourisme.com/api/v002"
    
    # Mapping des types Apidae vers notre format
    TYPE_MAPPING = {
        'PATRIMOINE_CULTUREL': 'sites',
        'PATRIMOINE_NATUREL': 'sites',
        'EQUIPEMENT': 'activities',
        'ACTIVITE': 'activities',
        'HEBERGEMENT_LOCATIF': 'accommodations',
        'HEBERGEMENT_COLLECTIF': 'accommodations',
        'HOTELLERIE': 'accommodations',
        'HOTELLERIE_PLEIN_AIR': 'accommodations',
        'RESTAURATION': 'restaurants',
        'FETE_ET_MANIFESTATION': 'events',
        'DEGUSTATION': 'restaurants',
        'COMMERCE_ET_SERVICE': 'sites',
    }
    
    def __init__(self, config: ProviderConfig):
        """
        Initialise le provider Apidae.
        
        Args:
            config: Configuration avec api_key et api_secret (projet_id) obligatoires
        """
        if not config.api_url:
            config.api_url = self.BASE_URL
        
        super().__init__(config)
        self._session = None
    
    def authenticate(self) -> bool:
        """
        Authentifie auprès de l'API Apidae.
        
        Apidae utilise une authentification par clé API + projet ID.
        
        Returns:
            True si authentifié
        """
        if not self.config.api_key or not self.config.api_secret:
            self.logger.error("API key and project ID are required for Apidae")
            return False
        
        try:
            self._session = requests.Session()
            
            # Apidae utilise les paramètres dans l'URL
            self._session.params = {
                'apiKey': self.config.api_key,
                'projetId': self.config.api_secret
            }
            
            self._authenticated = True
            self.logger.info("Apidae credentials configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication setup failed: {e}")
            return False
    
    def extract(self, **kwargs) -> ExtractionResult:
        """
        Extrait les données depuis l'API Apidae.
        
        Args:
            selection_ids: Liste d'IDs de sélections Apidae (optionnel)
            types: Types d'objets à récupérer
            communes: Codes INSEE des communes
            limit: Nombre max de résultats
            
        Returns:
            ExtractionResult avec les POI extraits
        """
        start_time = time.time()
        
        if not self._authenticated:
            if not self.authenticate():
                return ExtractionResult(
                    source=self.config.name,
                    pois=[],
                    count=0,
                    timestamp=datetime.now().isoformat(),
                    errors=[{'error': 'Authentication failed'}]
                )
        
        selection_ids = kwargs.get('selection_ids', [])
        types = kwargs.get('types', [])
        limit = kwargs.get('limit', self.config.page_size)
        
        self.logger.info(f"Extracting from Apidae (selections={selection_ids}, limit={limit})...")
        
        # =====================================================================
        # TODO: Implémenter les appels API réels
        # =====================================================================
        #
        # Exemple d'appel à l'API Apidae:
        #
        # # Recherche par sélection
        # response = self._session.get(
        #     f"{self.config.api_url}/recherche/list-objets-touristiques",
        #     params={
        #         'query': json.dumps({
        #             'selectionIds': [12345],
        #             'count': 100,
        #             'first': 0,
        #             'responseFields': [
        #                 'id', 'nom', 'localisation', 'informations',
        #                 'presentation', 'illustrations', 'contacts'
        #             ]
        #         })
        #     }
        # )
        #
        # # Recherche par critères
        # response = self._session.get(
        #     f"{self.config.api_url}/recherche/list-objets-touristiques",
        #     params={
        #         'query': json.dumps({
        #             'criteresQuery': '(type:PATRIMOINE_CULTUREL)',
        #             'locales': ['fr'],
        #             'count': 100
        #         })
        #     }
        # )
        # =====================================================================
        
        self.logger.warning("Apidae API integration not yet implemented - use FakeDataProvider")
        
        return ExtractionResult(
            source=self.config.name,
            pois=[],
            count=0,
            timestamp=datetime.now().isoformat(),
            duration_seconds=time.time() - start_time,
            warnings=[
                "Apidae API integration pending",
                "Configure api_key and api_secret (projet_id)",
                "For now, use FakeDataProvider for testing"
            ]
        )
    
    def normalize(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données Apidae au format POI unifié.
        
        Args:
            raw_data: Données brutes de l'API Apidae
            
        Returns:
            Liste de POI au format normalisé
        """
        normalized = []
        
        for item in raw_data:
            try:
                poi = self._normalize_item(item)
                if poi:
                    normalized.append(poi)
            except Exception as e:
                self.logger.warning(f"Failed to normalize Apidae item: {e}")
        
        return normalized
    
    def _normalize_item(self, item: Dict) -> Optional[Dict]:
        """
        Normalise un item Apidae.
        
        Structure typique Apidae:
        {
            "id": 12345,
            "type": "PATRIMOINE_CULTUREL",
            "nom": {"libelleFr": "Château de ..."},
            "localisation": {
                "adresse": {
                    "adresse1": "...",
                    "codePostal": "69000",
                    "commune": {"nom": "Lyon"}
                },
                "geolocalisation": {
                    "geoJson": {"coordinates": [4.8357, 45.7640]}
                }
            },
            "presentation": {
                "descriptifCourt": {"libelleFr": "..."},
                "descriptifDetaille": {"libelleFr": "..."}
            },
            "illustrations": [...],
            "informationsContact": {...}
        }
        """
        poi = {
            'id': None,
            'closed': False,
            'display': True,
            'tags': [],
            'types': [],
            'poi_name': {},
            'addresses': [],
            'geopoints': [],
            'contacts': [],
            'descriptions': [],
            'pictures': [],
            'products': [],
            'schedules': [],
            'sources': [{
                'source': 'Apidae',
                'reference': str(item.get('id', '')),
                'last_update': datetime.now().isoformat()
            }]
        }
        
        # Nom
        nom = item.get('nom', {})
        poi['poi_name']['fr'] = nom.get('libelleFr', '')
        if nom.get('libelleEn'):
            poi['poi_name']['en'] = nom.get('libelleEn')
        
        # Type
        apidae_type = item.get('type', '')
        mapped_type = self.TYPE_MAPPING.get(apidae_type, 'sites')
        poi['types'].append(mapped_type)
        
        # Localisation
        localisation = item.get('localisation', {})
        
        # Adresse
        adresse = localisation.get('adresse', {})
        if adresse:
            commune = adresse.get('commune', {})
            poi['addresses'].append({
                'city': commune.get('nom'),
                'zip_code': adresse.get('codePostal'),
                'country': 'France',
                'street_addresses': [adresse.get('adresse1')] if adresse.get('adresse1') else []
            })
        
        # Coordonnées
        geo = localisation.get('geolocalisation', {})
        geojson = geo.get('geoJson', {})
        coords = geojson.get('coordinates', [])
        if len(coords) >= 2:
            poi['geopoints'].append({
                'longitude': coords[0],
                'latitude': coords[1]
            })
        
        # Descriptions
        presentation = item.get('presentation', {})
        if presentation.get('descriptifCourt', {}).get('libelleFr'):
            poi['descriptions'].append({
                'type': 'short',
                'fr': presentation['descriptifCourt']['libelleFr']
            })
        if presentation.get('descriptifDetaille', {}).get('libelleFr'):
            poi['descriptions'].append({
                'type': 'detailed',
                'fr': presentation['descriptifDetaille']['libelleFr']
            })
        
        # Illustrations
        for illus in item.get('illustrations', []):
            if illus.get('traductionFichiers', []):
                fichier = illus['traductionFichiers'][0]
                poi['pictures'].append({
                    'url': fichier.get('url', ''),
                    'title': {'fr': illus.get('nom', {}).get('libelleFr', '')},
                    'main_picture': illus.get('principale', False)
                })
        
        return poi
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du provider Apidae."""
        base_check = super().health_check()
        
        api_status = 'unknown'
        if self.config.api_key and self.config.api_secret:
            try:
                response = requests.get(
                    f"{self.config.api_url}/referentiel/communes",
                    params={
                        'apiKey': self.config.api_key,
                        'projetId': self.config.api_secret,
                        'query': '{"count": 1}'
                    },
                    timeout=5
                )
                api_status = 'reachable' if response.status_code == 200 else f'error_{response.status_code}'
            except Exception:
                api_status = 'unreachable'
        else:
            api_status = 'no_credentials'
        
        return {
            **base_check,
            'api_status': api_status,
            'api_url': self.config.api_url,
            'has_api_key': bool(self.config.api_key),
            'has_project_id': bool(self.config.api_secret)
        }
