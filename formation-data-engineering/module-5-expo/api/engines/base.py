"""
Classe de base pour les moteurs STT.
Simple mais extensible pour ajouter de nouveaux providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSTTEngine(ABC):
    """
    Classe abstraite de base pour tous les moteurs STT.

    Pour ajouter un nouveau moteur:
    1. Creer une classe qui herite de BaseSTTEngine
    2. Implementer la methode transcribe()
    3. L'ajouter dans routes.py ENGINES dict
    """

    name: str = "base"

    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """
        Transcrit un fichier audio en texte.

        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue (fr, en, es, auto, etc.)

        Returns:
            Dict avec:
                - text: Texte transcrit
                - language: Langue detectee ou utilisee
                - engine: Nom du moteur
                - (optionnel) confidence: Score de confiance
        """
        pass

    def is_available(self) -> bool:
        """
        Verifie si le moteur est disponible (modele charge, API accessible, etc.)

        Returns:
            True si le moteur peut etre utilise
        """
        return True

    def get_supported_languages(self) -> list:
        """
        Retourne la liste des langues supportees.

        Returns:
            Liste des codes langues (ex: ['fr', 'en', 'es'])
        """
        return ['fr', 'en']
