"""
Factory pour la création et gestion des providers de données POI.

Ce module permet de switcher facilement entre les données fake et les vraies APIs
sans modifier le code existant.
"""

from enum import Enum
from typing import Dict, List, Optional, Type
import os
import json
import logging

from .base import BaseDataProvider, ProviderConfig
from .fake_provider import FakeDataProvider
from .datatourisme_provider import DatatourismeProvider
from .apidae_provider import ApidaeProvider
from .tripadvisor_provider import TripAdvisorProvider
from .tourinsoft_provider import TourinsoftProvider

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Types de providers disponibles."""
    FAKE = "fake"
    DATATOURISME = "datatourisme"
    APIDAE = "apidae"
    TRIPADVISOR = "tripadvisor"
    TOURINSOFT = "tourinsoft"


# Mapping des types vers les classes de providers
PROVIDER_CLASSES: Dict[ProviderType, Type[BaseDataProvider]] = {
    ProviderType.FAKE: FakeDataProvider,
    ProviderType.DATATOURISME: DatatourismeProvider,
    ProviderType.APIDAE: ApidaeProvider,
    ProviderType.TRIPADVISOR: TripAdvisorProvider,
    ProviderType.TOURINSOFT: TourinsoftProvider,
}


class ProviderFactory:
    """
    Factory pour créer et gérer les providers de données POI.

    Permet de:
    - Créer des providers à partir de la configuration
    - Switcher entre fake data et vraies APIs
    - Gérer plusieurs providers simultanément

    Usage:
        # Création simple avec fake data
        factory = ProviderFactory()
        provider = factory.get_provider(ProviderType.FAKE)

        # Création avec configuration
        factory = ProviderFactory.from_config_file("config/providers.json")
        providers = factory.get_all_active_providers()

        # Mode mixte (certains fake, certains réels)
        factory = ProviderFactory()
        factory.set_provider_mode(ProviderType.DATATOURISME, use_real=True)
        factory.set_provider_mode(ProviderType.APIDAE, use_real=False)
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialise la factory.

        Args:
            config: Configuration optionnelle des providers
        """
        self._config = config or {}
        self._providers: Dict[ProviderType, BaseDataProvider] = {}
        self._provider_modes: Dict[ProviderType, bool] = {}  # True = real, False = fake

        # Par défaut, tous les providers sont en mode fake
        for provider_type in ProviderType:
            if provider_type != ProviderType.FAKE:
                self._provider_modes[provider_type] = False

    @classmethod
    def from_config_file(cls, config_path: str) -> "ProviderFactory":
        """
        Crée une factory à partir d'un fichier de configuration.

        Args:
            config_path: Chemin vers le fichier JSON de configuration

        Returns:
            Instance de ProviderFactory configurée
        """
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            config = {}

        return cls(config)

    @classmethod
    def from_env(cls) -> "ProviderFactory":
        """
        Crée une factory à partir des variables d'environnement.

        Variables supportées:
            POI_PROVIDER_CONFIG: Chemin vers le fichier de config
            POI_USE_REAL_APIS: "true" pour activer toutes les vraies APIs
            POI_DATATOURISME_API_KEY: Clé API Datatourisme
            POI_APIDAE_API_KEY: Clé API Apidae
            POI_APIDAE_API_SECRET: Secret API Apidae
            POI_TRIPADVISOR_API_KEY: Clé API TripAdvisor
            POI_TOURINSOFT_BASE_URL: URL de base Tourinsoft

        Returns:
            Instance de ProviderFactory configurée
        """
        config_path = os.environ.get("POI_PROVIDER_CONFIG")
        if config_path:
            return cls.from_config_file(config_path)

        config = {
            "use_real_apis": os.environ.get("POI_USE_REAL_APIS", "false").lower() == "true",
            "providers": {}
        }

        # Configuration Datatourisme
        if os.environ.get("POI_DATATOURISME_API_KEY"):
            config["providers"]["datatourisme"] = {
                "enabled": True,
                "api_key": os.environ.get("POI_DATATOURISME_API_KEY"),
                "base_url": os.environ.get("POI_DATATOURISME_BASE_URL",
                                          "https://diffuseur.datatourisme.fr/webservice")
            }

        # Configuration Apidae
        if os.environ.get("POI_APIDAE_API_KEY"):
            config["providers"]["apidae"] = {
                "enabled": True,
                "api_key": os.environ.get("POI_APIDAE_API_KEY"),
                "api_secret": os.environ.get("POI_APIDAE_API_SECRET"),
                "projet_id": os.environ.get("POI_APIDAE_PROJET_ID"),
                "base_url": os.environ.get("POI_APIDAE_BASE_URL",
                                          "https://api.apidae-tourisme.com/api/v002")
            }

        # Configuration TripAdvisor
        if os.environ.get("POI_TRIPADVISOR_API_KEY"):
            config["providers"]["tripadvisor"] = {
                "enabled": True,
                "api_key": os.environ.get("POI_TRIPADVISOR_API_KEY"),
                "base_url": os.environ.get("POI_TRIPADVISOR_BASE_URL",
                                          "https://api.content.tripadvisor.com/api/v1")
            }

        # Configuration Tourinsoft
        if os.environ.get("POI_TOURINSOFT_BASE_URL"):
            config["providers"]["tourinsoft"] = {
                "enabled": True,
                "base_url": os.environ.get("POI_TOURINSOFT_BASE_URL"),
                "api_key": os.environ.get("POI_TOURINSOFT_API_KEY")
            }

        return cls(config)

    def set_provider_mode(self, provider_type: ProviderType, use_real: bool) -> None:
        """
        Définit le mode d'un provider (réel ou fake).

        Args:
            provider_type: Type de provider
            use_real: True pour utiliser l'API réelle, False pour fake
        """
        if provider_type == ProviderType.FAKE:
            logger.warning("Cannot change mode for FAKE provider type")
            return

        self._provider_modes[provider_type] = use_real

        # Invalide le cache si le provider existe
        if provider_type in self._providers:
            del self._providers[provider_type]

    def get_provider(self, provider_type: ProviderType) -> BaseDataProvider:
        """
        Récupère un provider par son type.

        Si le provider est en mode fake, retourne un FakeDataProvider configuré
        pour simuler ce type de source.

        Args:
            provider_type: Type de provider souhaité

        Returns:
            Instance du provider
        """
        # Retourne le provider en cache s'il existe
        if provider_type in self._providers:
            return self._providers[provider_type]

        # Cas spécial: FAKE retourne toujours FakeDataProvider
        if provider_type == ProviderType.FAKE:
            provider = self._create_fake_provider()
            self._providers[provider_type] = provider
            return provider

        # Vérifie si on doit utiliser le vrai provider ou fake
        use_real = self._provider_modes.get(provider_type, False)

        # Override par la config globale
        if self._config.get("use_real_apis", False):
            use_real = True

        if use_real:
            provider = self._create_real_provider(provider_type)
        else:
            provider = self._create_fake_provider(source_name=provider_type.value)

        self._providers[provider_type] = provider
        return provider

    def _create_fake_provider(self, source_name: Optional[str] = None) -> FakeDataProvider:
        """
        Crée un FakeDataProvider.

        Args:
            source_name: Nom de source à simuler (optionnel)

        Returns:
            Instance de FakeDataProvider
        """
        fake_config = self._config.get("fake", {})

        config = ProviderConfig(
            name=source_name or "fake",
            enabled=True,
            api_key=None,
            base_url=None,
            extra={
                "num_pois": fake_config.get("num_pois", 100),
                "duplicate_rate": fake_config.get("duplicate_rate", 0.15),
                "source_override": source_name
            }
        )

        return FakeDataProvider(config)

    def _create_real_provider(self, provider_type: ProviderType) -> BaseDataProvider:
        """
        Crée un provider réel.

        Args:
            provider_type: Type de provider

        Returns:
            Instance du provider réel

        Raises:
            ValueError: Si le provider n'est pas configuré
        """
        provider_config = self._config.get("providers", {}).get(provider_type.value, {})

        if not provider_config.get("enabled", False):
            raise ValueError(
                f"Provider {provider_type.value} is not enabled. "
                f"Check your configuration or use fake mode."
            )

        config = ProviderConfig(
            name=provider_type.value,
            enabled=True,
            api_key=provider_config.get("api_key"),
            base_url=provider_config.get("base_url"),
            extra={k: v for k, v in provider_config.items()
                   if k not in ("enabled", "api_key", "base_url")}
        )

        provider_class = PROVIDER_CLASSES[provider_type]
        return provider_class(config)

    def get_all_active_providers(self) -> Dict[ProviderType, BaseDataProvider]:
        """
        Récupère tous les providers actifs selon la configuration.

        Returns:
            Dictionnaire des providers actifs
        """
        active_providers = {}

        providers_config = self._config.get("providers", {})

        for provider_type in ProviderType:
            if provider_type == ProviderType.FAKE:
                continue

            # Vérifie si le provider est explicitement activé dans la config
            provider_conf = providers_config.get(provider_type.value, {})
            if provider_conf.get("enabled", False) or self._config.get("use_real_apis", False):
                try:
                    active_providers[provider_type] = self.get_provider(provider_type)
                except ValueError as e:
                    logger.warning(f"Could not create provider {provider_type.value}: {e}")

        # Si aucun provider actif, utilise fake par défaut
        if not active_providers:
            active_providers[ProviderType.FAKE] = self.get_provider(ProviderType.FAKE)

        return active_providers

    def extract_from_all(self, **kwargs) -> Dict[str, List[Dict]]:
        """
        Extrait les données de tous les providers actifs.

        Args:
            **kwargs: Arguments passés à chaque provider

        Returns:
            Dictionnaire {source_name: [pois]}
        """
        results = {}

        for provider_type, provider in self.get_all_active_providers().items():
            try:
                extraction = provider.extract(**kwargs)
                if extraction.success:
                    results[provider.source_name] = extraction.data
                else:
                    logger.error(
                        f"Extraction failed for {provider.source_name}: "
                        f"{extraction.errors}"
                    )
            except Exception as e:
                logger.error(f"Error extracting from {provider_type.value}: {e}")

        return results

    def get_provider_status(self) -> Dict[str, Dict]:
        """
        Retourne le statut de tous les providers.

        Returns:
            Dictionnaire avec le statut de chaque provider
        """
        status = {}

        for provider_type in ProviderType:
            if provider_type == ProviderType.FAKE:
                status["fake"] = {
                    "type": "fake",
                    "mode": "fake",
                    "available": True,
                    "configured": True
                }
                continue

            provider_conf = self._config.get("providers", {}).get(provider_type.value, {})
            use_real = self._provider_modes.get(provider_type, False)

            status[provider_type.value] = {
                "type": provider_type.value,
                "mode": "real" if use_real else "fake",
                "available": provider_conf.get("enabled", False),
                "configured": bool(provider_conf.get("api_key") or
                                  provider_conf.get("base_url"))
            }

        return status


# Singleton global pour faciliter l'utilisation
_default_factory: Optional[ProviderFactory] = None


def get_default_factory() -> ProviderFactory:
    """
    Retourne la factory par défaut (singleton).

    Returns:
        Instance de ProviderFactory
    """
    global _default_factory
    if _default_factory is None:
        _default_factory = ProviderFactory.from_env()
    return _default_factory


def reset_default_factory() -> None:
    """Réinitialise la factory par défaut."""
    global _default_factory
    _default_factory = None
