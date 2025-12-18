"""
Classes de base pour les Data Providers
Module 3 - Formation Data Engineering
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration pour un provider de données."""
    
    # Identification
    name: str
    source_type: str  # 'fake', 'api', 'file', 'database'
    
    # API settings
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    # Rate limiting
    rate_limit: int = 100  # requêtes par minute
    timeout: int = 30  # secondes
    max_retries: int = 3
    
    # Pagination
    page_size: int = 100
    max_pages: Optional[int] = None
    
    # Filters
    regions: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)
    
    # Fake data settings
    num_pois: int = 100
    duplicate_rate: float = 0.15
    
    # Cache
    use_cache: bool = True
    cache_ttl: int = 3600  # secondes
    
    def __post_init__(self):
        """Validation après initialisation."""
        if self.source_type == 'api' and not self.api_url:
            raise ValueError(f"API URL required for provider {self.name}")


@dataclass
class ExtractionResult:
    """Résultat d'une extraction de données."""
    
    source: str
    pois: List[Dict[str, Any]]
    count: int
    timestamp: str
    
    # Métadonnées
    duration_seconds: float = 0.0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Pagination info
    page: int = 1
    total_pages: int = 1
    has_more: bool = False
    
    # API info (si applicable)
    api_calls_made: int = 0
    rate_limit_remaining: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            'source': self.source,
            'count': self.count,
            'timestamp': self.timestamp,
            'duration_seconds': self.duration_seconds,
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'page': self.page,
            'total_pages': self.total_pages,
            'has_more': self.has_more,
            'api_calls_made': self.api_calls_made
        }


class BaseDataProvider(ABC):
    """
    Classe abstraite de base pour tous les providers de données POI.
    
    Chaque provider doit implémenter:
    - extract(): Récupérer les données brutes
    - normalize(): Transformer au format unifié
    - validate(): Valider les données
    
    Optionnellement:
    - authenticate(): Si l'API nécessite une authentification
    - paginate(): Pour gérer la pagination
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialise le provider.
        
        Args:
            config: Configuration du provider
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self._authenticated = False
        self._session = None
    
    @property
    def name(self) -> str:
        """Nom du provider."""
        return self.config.name
    
    @property
    def source_type(self) -> str:
        """Type de source (fake, api, file, etc.)."""
        return self.config.source_type
    
    @abstractmethod
    def extract(self, **kwargs) -> ExtractionResult:
        """
        Extrait les données depuis la source.
        
        Args:
            **kwargs: Arguments spécifiques au provider
            
        Returns:
            ExtractionResult contenant les POI extraits
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données brutes au format POI unifié.
        
        Args:
            raw_data: Données brutes de la source
            
        Returns:
            Liste de POI au format normalisé
        """
        pass
    
    def validate(self, poi: Dict) -> tuple[bool, List[str]]:
        """
        Valide un POI selon les règles de base.
        
        Args:
            poi: POI à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Règle 1: Nom obligatoire
        if not poi.get('poi_name') or not poi['poi_name'].get('fr'):
            errors.append('missing_name_fr')
        
        # Règle 2: Au moins une localisation
        if not poi.get('addresses') and not poi.get('geopoints'):
            errors.append('missing_location')
        
        # Règle 3: Au moins un type
        if not poi.get('types'):
            errors.append('missing_type')
        
        # Règle 4: Source obligatoire
        if not poi.get('sources'):
            errors.append('missing_source')
        
        # Règle 5: Coordonnées valides (si présentes)
        for geo in poi.get('geopoints', []):
            lat = geo.get('latitude', 0)
            lon = geo.get('longitude', 0)
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                errors.append('invalid_coordinates')
                break
        
        return len(errors) == 0, errors
    
    def authenticate(self) -> bool:
        """
        Authentifie auprès de l'API si nécessaire.
        
        Returns:
            True si authentifié avec succès
        """
        # Par défaut, pas d'authentification nécessaire
        self._authenticated = True
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état du provider.
        
        Returns:
            Dict avec le statut et les infos de santé
        """
        return {
            'provider': self.name,
            'source_type': self.source_type,
            'status': 'ok',
            'authenticated': self._authenticated,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du provider.
        
        Returns:
            Dict avec les statistiques
        """
        return {
            'provider': self.name,
            'config': {
                'rate_limit': self.config.rate_limit,
                'page_size': self.config.page_size,
                'use_cache': self.config.use_cache
            }
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, type={self.source_type})"
