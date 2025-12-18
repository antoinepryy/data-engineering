"""
Data Providers pour le Pipeline ETL POI
Module 3 - Formation Data Engineering

Ce module fournit une architecture extensible pour récupérer des données POI
depuis différentes sources (fake data, APIs réelles, fichiers, etc.)

Usage:
    from providers import ProviderFactory, ProviderType
    
    # Mode fake data (défaut)
    provider = ProviderFactory.get_provider('datatourisme')
    pois = provider.extract(num_pois=100)
    
    # Mode API réelle
    provider = ProviderFactory.get_provider('datatourisme', use_real_api=True)
    pois = provider.extract()
"""

from .base import BaseDataProvider, ProviderConfig
from .factory import ProviderFactory, ProviderType, get_default_factory, reset_default_factory
from .fake_provider import FakeDataProvider
from .datatourisme_provider import DatatourismeProvider
from .apidae_provider import ApidaeProvider
from .tripadvisor_provider import TripAdvisorProvider
from .tourinsoft_provider import TourinsoftProvider

__all__ = [
    'BaseDataProvider',
    'ProviderConfig',
    'ProviderFactory',
    'ProviderType',
    'get_default_factory',
    'reset_default_factory',
    'FakeDataProvider',
    'DatatourismeProvider',
    'ApidaeProvider',
    'TripAdvisorProvider',
    'TourinsoftProvider',
]
