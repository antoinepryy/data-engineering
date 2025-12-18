"""
Cache des modèles avec @st.cache_resource
Optimise les performances en évitant de recharger les modèles à chaque requête
"""

import streamlit as st


@st.cache_resource
def get_whisper_model(size: str = "tiny"):
    """
    Charge et cache le modèle Whisper.

    Args:
        size: Taille du modèle ('tiny', 'base', 'small', 'medium', 'large')

    Returns:
        Modèle Whisper chargé
    """
    import whisper
    return whisper.load_model(size)


# Mapping des langues vers les chemins des modèles Vosk
VOSK_MODELS = {
    "en": "/app/models/vosk-model-small-en-us-0.15",
    "fr": "/app/models/vosk-model-small-fr-0.22",
}


@st.cache_resource
def get_vosk_model(language: str = "en"):
    """
    Charge et cache le modèle Vosk pour STT offline.

    Args:
        language: Code langue ('en' pour anglais, 'fr' pour français)

    Returns:
        Modèle Vosk chargé
    """
    import vosk
    path = VOSK_MODELS.get(language, VOSK_MODELS["en"])
    return vosk.Model(path)


@st.cache_resource
def get_pyttsx3_engine():
    """
    Initialise et cache le moteur pyttsx3 pour TTS offline.

    Returns:
        Engine pyttsx3 initialisé
    """
    import pyttsx3
    return pyttsx3.init()
