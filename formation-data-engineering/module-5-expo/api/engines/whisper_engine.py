"""
Moteur STT Whisper (OpenAI)
Transcription de haute qualite, multi-langue, fonctionne offline.
"""

from typing import Dict, Any
from .base import BaseSTTEngine

# Cache singleton pour le modele Whisper (remplace @st.cache_resource)
_whisper_models: Dict[str, Any] = {}


def get_whisper_model(size: str = "tiny"):
    """
    Charge et cache le modele Whisper.
    Utilise un singleton au lieu de @st.cache_resource.
    """
    if size not in _whisper_models:
        import whisper
        _whisper_models[size] = whisper.load_model(size)
    return _whisper_models[size]


class WhisperEngine(BaseSTTEngine):
    """
    Moteur STT utilisant OpenAI Whisper.

    Avantages:
    - Fonctionne offline
    - Excellente qualite
    - Detection automatique de langue
    - Multi-langue (99 langues)

    Inconvenients:
    - Necessite GPU pour les gros modeles
    - Plus lent que les APIs cloud pour les petits fichiers
    """

    name = "whisper"

    def __init__(self, model_size: str = "tiny"):
        """
        Args:
            model_size: Taille du modele ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self._model = None

    def transcribe(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Transcrit avec Whisper.

        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue ou 'auto' pour detection automatique

        Returns:
            Dict avec text, language, engine
        """
        model = get_whisper_model(self.model_size)

        # Whisper accepte None pour la detection auto
        lang_param = None if language == "auto" else language

        result = model.transcribe(audio_path, language=lang_param)

        return {
            "text": result["text"].strip(),
            "language": result.get("language", language),
            "engine": self.name,
            "model_size": self.model_size
        }

    def is_available(self) -> bool:
        """Whisper est toujours disponible (modele local)."""
        try:
            import whisper
            return True
        except ImportError:
            return False

    def get_supported_languages(self) -> list:
        """Whisper supporte 99 langues."""
        return [
            'auto', 'fr', 'en', 'es', 'de', 'it', 'pt', 'nl', 'pl', 'ru',
            'ja', 'zh', 'ko', 'ar', 'hi', 'tr', 'vi', 'th', 'id', 'cs'
        ]
