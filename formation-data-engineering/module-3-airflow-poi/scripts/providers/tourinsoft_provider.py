"""
Tourinsoft API Provider
Module 3 - Formation Data Engineering

Provider pour l'API Tourinsoft
Documentation: Varie selon les départements/régions

Note: Tourinsoft est une solution utilisée par de nombreux offices de tourisme.
L'accès API dépend des conventions avec chaque territoire.
"""

import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .base import BaseDataProvider, ProviderConfig, ExtractionResult

logger = logging.getLogger(__name__)


class TourinsoftProvider(BaseDataProvider):
    """
    Provider pour l'API Tourinsoft.
    
    Tourinsoft est une solution de gestion de l'information touristique
    utilisée par de nombreux offices de tourisme en France.
    
    L'API varie selon les territoires, mais le format de données
    est généralement similaire (XML ou JSON).
    
    Pour obtenir un accès:
    - Contacter l'office de tourisme du territoire concerné
    - Signer une convention de partenariat
    - Obtenir les credentials API
    
    Configuration requise:
        - api_url: URL spécifique au territoire
        - api_key: Clé API fournie par l'office
        - api_secret: Identifiant de syndication (optionnel)
    """
    
    # Mapping des types Tourinsoft vers notre format
    TYPE_MAPPING = {
        'PATRIMOINE': 'sites',
        'PATRIMOINE_CULTUREL': 'sites',
        'PATRIMOINE_NATUREL': 'sites',
        'EQUIPEMENT': 'activities',
        'ACTIVITE': 'activities',
        'HEBERGEMENT': 'accommodations',
        'HOTEL': 'accommodations',
        'CAMPING': 'accommodations',
        'MEUBLE': 'accommodations',
        'RESTAURATION': 'restaurants',
        'RESTAURANT': 'restaurants',
        'FETE_MANIFESTATION': 'events',
        'MANIFESTATION': 'events',
    }
    
    def __init__(self, config: ProviderConfig):
        """
        Initialise le provider Tourinsoft.
        
        Args:
            config: Configuration avec api_url et api_key obligatoires
        """
        super().__init__(config)
        self._session = None
    
    def authenticate(self) -> bool:
        """
        Configure l'authentification Tourinsoft.
        
        Le format d'authentification varie selon les territoires.
        Généralement: Basic Auth ou clé API en paramètre.
        
        Returns:
            True si configuré
        """
        if not self.config.api_url:
            self.logger.error("API URL is required for Tourinsoft (varies by territory)")
            return False
        
        try:
            self._session = requests.Session()
            
            # Configuration selon le type d'auth
            if self.config.api_key and self.config.api_secret:
                # Auth avec user/password
                self._session.auth = (self.config.api_key, self.config.api_secret)
            elif self.config.api_key:
                # Auth avec clé API en header ou paramètre
                self._session.params = {'apiKey': self.config.api_key}
            
            self._session.headers.update({
                'Accept': 'application/json'
            })
            
            self._authenticated = True
            self.logger.info("Tourinsoft API credentials configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication setup failed: {e}")
            return False
    
    def extract(self, **kwargs) -> ExtractionResult:
        """
        Extrait les données depuis l'API Tourinsoft.
        
        Args:
            syndication_id: ID de syndication (flux)
            types: Types d'objets à récupérer
            modified_since: Date de dernière modification
            
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
        
        syndication_id = kwargs.get('syndication_id', self.config.api_secret)
        types = kwargs.get('types', [])
        
        self.logger.info(f"Extracting from Tourinsoft (syndication={syndication_id})...")
        
        # =====================================================================
        # TODO: Implémenter les appels API réels
        # =====================================================================
        #
        # Exemple d'appels à une API Tourinsoft typique:
        #
        # # Format XML (courant)
        # response = self._session.get(
        #     f"{self.config.api_url}/syndication/{syndication_id}",
        #     params={
        #         'format': 'json',  # ou xml
        #         'type': 'PATRIMOINE',
        #         'count': 100,
        #         'offset': 0
        #     }
        # )
        #
        # # Certains territoires utilisent des endpoints différents
        # response = self._session.get(
        #     f"{self.config.api_url}/api/v1/offres",
        #     params={
        #         'selection': syndication_id,
        #         'format': 'json'
        #     }
        # )
        # =====================================================================
        
        self.logger.warning("Tourinsoft API varies by territory - use FakeDataProvider")
        
        return ExtractionResult(
            source=self.config.name,
            pois=[],
            count=0,
            timestamp=datetime.now().isoformat(),
            duration_seconds=time.time() - start_time,
            warnings=[
                "Tourinsoft API integration pending",
                "API format varies by territory",
                "Contact local tourism office for access",
                "For now, use FakeDataProvider for testing"
            ]
        )
    
    def normalize(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données Tourinsoft au format POI unifié.
        
        Args:
            raw_data: Données brutes de l'API Tourinsoft
            
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
                self.logger.warning(f"Failed to normalize Tourinsoft item: {e}")
        
        return normalized
    
    def _normalize_item(self, item: Dict) -> Optional[Dict]:
        """
        Normalise un item Tourinsoft.
        
        Structure typique Tourinsoft (peut varier):
        {
            "SyndicObjectID": "123456",
            "SyndicObjectName": "Château de ...",
            "SyndicStructureId": "OT123",
            "ObjectTypeName": "PATRIMOINE_CULTUREL",
            "GmapLatitude": "48.8584",
            "GmapLongitude": "2.2945",
            "Address1": "...",
            "Address2": "...",
            "Zip": "75007",
            "City": "Paris",
            "Description": "...",
            "Phone": "0123456789",
            "Email": "contact@example.com",
            "Website": "https://...",
            "Photos": [{"URL": "...", "Copyright": "..."}]
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
                'source': 'Tourinsoft',
                'reference': str(item.get('SyndicObjectID', item.get('id', ''))),
                'last_update': datetime.now().isoformat()
            }]
        }
        
        # Nom
        name = item.get('SyndicObjectName', item.get('name', item.get('nom', '')))
        poi['poi_name']['fr'] = name
        
        # Type
        type_name = item.get('ObjectTypeName', item.get('type', ''))
        mapped_type = self.TYPE_MAPPING.get(type_name.upper(), 'sites')
        poi['types'].append(mapped_type)
        
        # Adresse
        city = item.get('City', item.get('city', item.get('commune', '')))
        zip_code = item.get('Zip', item.get('zip', item.get('codePostal', '')))
        
        address_parts = []
        for key in ['Address1', 'Address2', 'address', 'adresse']:
            if item.get(key):
                address_parts.append(item[key])
        
        if city or zip_code:
            poi['addresses'].append({
                'city': city,
                'zip_code': str(zip_code) if zip_code else None,
                'country': 'France',
                'street_addresses': address_parts if address_parts else []
            })
        
        # Coordonnées
        lat = item.get('GmapLatitude', item.get('latitude', item.get('lat')))
        lon = item.get('GmapLongitude', item.get('longitude', item.get('lon', item.get('lng'))))
        
        if lat and lon:
            try:
                poi['geopoints'].append({
                    'latitude': float(lat),
                    'longitude': float(lon)
                })
            except (ValueError, TypeError):
                pass
        
        # Description
        desc = item.get('Description', item.get('description', ''))
        if desc:
            poi['descriptions'].append({
                'type': 'general',
                'fr': desc
            })
        
        # Contact
        contact = {}
        if item.get('Phone', item.get('phone', item.get('telephone'))):
            contact['phones'] = [item.get('Phone', item.get('phone', item.get('telephone')))]
        if item.get('Email', item.get('email')):
            contact['emails'] = [item.get('Email', item.get('email'))]
        if item.get('Website', item.get('website', item.get('siteWeb'))):
            contact['websites'] = [item.get('Website', item.get('website', item.get('siteWeb')))]
        
        if contact:
            poi['contacts'].append(contact)
        
        # Photos
        photos = item.get('Photos', item.get('photos', item.get('illustrations', [])))
        for photo in photos:
            if isinstance(photo, dict):
                url = photo.get('URL', photo.get('url', photo.get('urlDiaporama')))
                if url:
                    poi['pictures'].append({
                        'url': url,
                        'copyrights': [photo.get('Copyright', photo.get('copyright', ''))] if photo.get('Copyright') or photo.get('copyright') else []
                    })
            elif isinstance(photo, str):
                poi['pictures'].append({'url': photo})
        
        return poi
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du provider Tourinsoft."""
        base_check = super().health_check()
        
        api_status = 'unknown'
        if self.config.api_url:
            try:
                response = requests.get(
                    self.config.api_url,
                    timeout=5
                )
                api_status = 'reachable' if response.status_code < 500 else f'error_{response.status_code}'
            except Exception:
                api_status = 'unreachable'
        else:
            api_status = 'no_api_url'
        
        return {
            **base_check,
            'api_status': api_status,
            'api_url': self.config.api_url,
            'has_api_key': bool(self.config.api_key),
            'note': 'Tourinsoft API varies by territory'
        }
