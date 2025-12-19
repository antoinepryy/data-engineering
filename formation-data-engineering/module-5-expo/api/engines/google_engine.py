"""
Moteur STT Google Speech Recognition
API cloud gratuite via la bibliotheque speech_recognition.
"""

from typing import Dict, Any
from .base import BaseSTTEngine


class GoogleEngine(BaseSTTEngine):
    """
    Moteur STT utilisant Google Speech Recognition.

    Avantages:
    - Tres bonne precision
    - Pas besoin de modele local
    - Multi-langue

    Inconvenients:
    - Necessite une connexion internet
    - Limites de requetes (API gratuite)
    - Necessite conversion WAV
    """

    name = "google"

    def transcribe(self, audio_path: str, language: str = "fr-FR") -> Dict[str, Any]:
        """
        Transcrit avec Google Speech Recognition.

        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue Google (fr-FR, en-US, es-ES, etc.)

        Returns:
            Dict avec text, language, engine
        """
        import speech_recognition as sr
        from pydub import AudioSegment
        import tempfile
        import os

        # Convertir en WAV (requis par speech_recognition)
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio.export(tmp.name, format="wav")
            wav_path = tmp.name

        try:
            r = sr.Recognizer()

            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)

            # Convertir le code langue simple en format Google si necessaire
            lang_code = self._normalize_language(language)

            text = r.recognize_google(audio_data, language=lang_code)

            return {
                "text": text,
                "language": language,
                "engine": self.name
            }

        finally:
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def _normalize_language(self, language: str) -> str:
        """
        Convertit les codes langue simples en format Google.

        Args:
            language: Code langue (fr, en, fr-FR, en-US, etc.)

        Returns:
            Code langue au format Google (fr-FR, en-US, etc.)
        """
        # Si deja au format complet, retourner tel quel
        if '-' in language:
            return language

        # Mapping des codes simples vers Google
        mapping = {
            'fr': 'fr-FR',
            'en': 'en-US',
            'es': 'es-ES',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-BR',
            'nl': 'nl-NL',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'ko': 'ko-KR',
            'ar': 'ar-SA',
        }

        return mapping.get(language, f"{language}-{language.upper()}")

    def is_available(self) -> bool:
        """Google STT necessite une connexion internet."""
        try:
            import speech_recognition as sr
            # Verifier la connectivite (simple check)
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=2)
            return True
        except Exception:
            return False

    def get_supported_languages(self) -> list:
        """Google supporte de nombreuses langues."""
        return [
            'fr', 'fr-FR', 'en', 'en-US', 'en-GB', 'es', 'es-ES',
            'de', 'de-DE', 'it', 'it-IT', 'pt', 'pt-BR', 'nl', 'nl-NL',
            'ru', 'ru-RU', 'ja', 'ja-JP', 'zh', 'zh-CN', 'ko', 'ko-KR'
        ]
