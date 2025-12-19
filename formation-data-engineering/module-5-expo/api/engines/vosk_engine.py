"""
Moteur STT Vosk (Kaldi-based)
Reconnaissance vocale offline, leger et rapide.
"""

import json
from typing import Dict, Any
from .base import BaseSTTEngine

# Chemins des modeles Vosk (dans le conteneur Docker)
# 3 modeles disponibles pour comparaison:
# - fr: small (41 MB) - rapide, usage courant
# - fr-large: large (1.4 GB) - haute precision
# - en: small (40 MB) - anglais
VOSK_MODELS = {
    "fr": "/app/models/vosk-model-small-fr-0.22",
    "fr-large": "/app/models/vosk-model-fr-0.22",
    "en": "/app/models/vosk-model-small-en-us-0.15",
}

# Cache singleton pour les modeles Vosk
_vosk_models: Dict[str, Any] = {}


def get_vosk_model(language: str = "fr"):
    """
    Charge et cache le modele Vosk.
    """
    if language not in _vosk_models:
        import vosk
        path = VOSK_MODELS.get(language, VOSK_MODELS["fr"])
        _vosk_models[language] = vosk.Model(path)
    return _vosk_models[language]


class VoskEngine(BaseSTTEngine):
    """
    Moteur STT utilisant Vosk (base sur Kaldi).

    Avantages:
    - Completement offline
    - Tres leger et rapide
    - Faible consommation memoire

    Inconvenients:
    - Moins precis que Whisper
    - Langues limitees aux modeles telecharges
    - Necessite conversion WAV 16kHz
    """

    name = "vosk"

    def transcribe(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """
        Transcrit avec Vosk.

        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue ('fr' ou 'en')

        Returns:
            Dict avec text, language, engine
        """
        import vosk
        from pydub import AudioSegment
        import tempfile
        import os

        # Convertir en WAV 16kHz mono (requis par Vosk)
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio.export(tmp.name, format="wav")
            wav_path = tmp.name

        try:
            # Charger le modele
            model = get_vosk_model(language)
            rec = vosk.KaldiRecognizer(model, 16000)

            # Lire et traiter le fichier WAV
            with open(wav_path, 'rb') as wf:
                # Skip WAV header (44 bytes)
                wf.read(44)

                results = []
                while True:
                    data = wf.read(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if result.get('text'):
                            results.append(result['text'])

                # Resultat final
                final = json.loads(rec.FinalResult())
                if final.get('text'):
                    results.append(final['text'])

            transcription = " ".join(results).strip()

            return {
                "text": transcription,
                "language": language,
                "engine": self.name
            }

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def is_available(self) -> bool:
        """Verifie si Vosk et les modeles sont disponibles."""
        try:
            import vosk
            import os
            # Verifier qu'au moins un modele existe
            for path in VOSK_MODELS.values():
                if os.path.exists(path):
                    return True
            return False
        except ImportError:
            return False

    def get_supported_languages(self) -> list:
        """Langues disponibles selon les modeles telecharges."""
        import os
        return [lang for lang, path in VOSK_MODELS.items() if os.path.exists(path)]
